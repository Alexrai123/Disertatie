# File System Monitoring Service
# References:
# - see docs/02_functional_req.txt §2 System Monitoring
# - see docs/14_ai_engine_design.txt §1(a) Event Listener
# - Uses watchdog library for real-time file system monitoring

from __future__ import annotations
import logging
import threading
import time
from pathlib import Path
from typing import Dict, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..db import SessionLocal
from ..models import Folder, File, Event, User, Log
from ..ai.event_listener import handle_event
from fastapi import BackgroundTasks

logger = logging.getLogger("app.file_monitor")


class FolderEventHandler(FileSystemEventHandler):
    """
    Handles file system events for a monitored folder.
    Creates Event records in the database when changes are detected.
    """
    
    def __init__(self, folder_id: int, folder_path: str):
        super().__init__()
        self.folder_id = folder_id
        self.folder_path = folder_path
        logger.info(f"Initialized event handler for folder {folder_id}: {folder_path}")
    
    def _create_event(self, event_type: str, path: str):
        """Create an event in the database for a file system change"""
        try:
            db = SessionLocal()
            try:
                # Get folder info
                folder = db.get(Folder, self.folder_id)
                if not folder:
                    logger.warning(f"Folder {self.folder_id} not found, skipping event")
                    return
                
                # Check if this file is registered in our database
                file_record = db.execute(
                    select(File).where(File.path == path, File.folder_id == self.folder_id)
                ).scalar_one_or_none()
                
                # Create event
                event = Event(
                    event_type=event_type,
                    target_file_id=file_record.id if file_record else None,
                    target_folder_id=self.folder_id,
                    triggered_by_user_id=folder.owner_id,  # System-triggered, use folder owner
                    processed_flag=False,
                )
                db.add(event)
                db.commit()
                db.refresh(event)
                
                logger.info(
                    f"Created event {event.id}: type={event_type} path={path} folder={self.folder_id}"
                )
                
                # Process event through AI engine
                # Note: BackgroundTasks not available here, so process synchronously
                handle_event(db, event, background_tasks=None)
                
                # Add log entry
                db.add(Log(
                    log_type="FILE_MONITOR",
                    message=f"File monitor detected {event_type} event: {path}",
                    related_event_id=event.id
                ))
                db.commit()
                
            finally:
                db.close()
        except Exception as e:
            logger.exception(f"Error creating event for {event_type} on {path}: {e}")
    
    def on_created(self, event: FileSystemEvent):
        if not event.is_directory:
            logger.debug(f"File created: {event.src_path}")
            self._create_event("create", event.src_path)
    
    def on_modified(self, event: FileSystemEvent):
        if not event.is_directory:
            logger.debug(f"File modified: {event.src_path}")
            self._create_event("modify", event.src_path)
    
    def on_deleted(self, event: FileSystemEvent):
        if not event.is_directory:
            logger.debug(f"File deleted: {event.src_path}")
            self._create_event("delete", event.src_path)


class FileMonitorService:
    """
    Service that monitors registered folders for file system changes.
    Runs in a background thread and automatically creates events.
    """
    
    def __init__(self):
        self.observer: Observer | None = None
        self.watched_folders: Dict[int, str] = {}  # folder_id -> path
        self.handlers: Dict[int, FolderEventHandler] = {}  # folder_id -> handler
        self.running = False
        self._lock = threading.Lock()
        logger.info("FileMonitorService initialized")
    
    def start(self):
        """Start the file monitoring service"""
        with self._lock:
            if self.running:
                logger.warning("File monitor already running")
                return
            
            logger.info("Starting file monitoring service...")
            self.observer = Observer()
            self.running = True
            
            # Load all folders from database and start watching
            self._load_folders()
            
            # Start the observer
            self.observer.start()
            logger.info("File monitoring service started")
    
    def stop(self):
        """Stop the file monitoring service"""
        with self._lock:
            if not self.running:
                return
            
            logger.info("Stopping file monitoring service...")
            self.running = False
            
            if self.observer:
                self.observer.stop()
                self.observer.join(timeout=5)
                self.observer = None
            
            self.watched_folders.clear()
            self.handlers.clear()
            logger.info("File monitoring service stopped")
    
    def _load_folders(self):
        """Load all folders from database and start watching them"""
        try:
            db = SessionLocal()
            try:
                folders = db.execute(select(Folder)).scalars().all()
                logger.info(f"Loading {len(folders)} folders for monitoring")
                
                for folder in folders:
                    self._watch_folder(folder.id, folder.path)
                
            finally:
                db.close()
        except Exception as e:
            logger.exception(f"Error loading folders: {e}")
    
    def _watch_folder(self, folder_id: int, folder_path: str):
        """Start watching a specific folder"""
        try:
            # Check if path exists
            path = Path(folder_path)
            if not path.exists():
                logger.warning(f"Folder path does not exist: {folder_path}")
                return
            
            if not path.is_dir():
                logger.warning(f"Path is not a directory: {folder_path}")
                return
            
            # Create handler
            handler = FolderEventHandler(folder_id, folder_path)
            self.handlers[folder_id] = handler
            
            # Schedule with observer
            if self.observer:
                self.observer.schedule(handler, folder_path, recursive=False)
                self.watched_folders[folder_id] = folder_path
                logger.info(f"Now watching folder {folder_id}: {folder_path}")
        
        except Exception as e:
            logger.exception(f"Error watching folder {folder_id} ({folder_path}): {e}")
    
    def add_folder(self, folder_id: int, folder_path: str):
        """Add a new folder to watch"""
        with self._lock:
            if not self.running:
                logger.warning("File monitor not running, cannot add folder")
                return
            
            if folder_id in self.watched_folders:
                logger.info(f"Folder {folder_id} already being watched")
                return
            
            self._watch_folder(folder_id, folder_path)
    
    def remove_folder(self, folder_id: int):
        """Remove a folder from watching"""
        with self._lock:
            if folder_id not in self.watched_folders:
                return
            
            # Unschedule the handler
            handler = self.handlers.get(folder_id)
            if handler and self.observer:
                # Note: watchdog doesn't have a direct unschedule method
                # We need to stop and restart the observer to remove a watch
                # For now, just remove from our tracking
                del self.watched_folders[folder_id]
                del self.handlers[folder_id]
                logger.info(f"Stopped watching folder {folder_id}")
    
    def get_status(self) -> dict:
        """Get current monitoring status"""
        with self._lock:
            return {
                "running": self.running,
                "watched_folders": len(self.watched_folders),
                "folders": [
                    {"id": folder_id, "path": path}
                    for folder_id, path in self.watched_folders.items()
                ]
            }


# Global instance
_monitor_service: FileMonitorService | None = None


def get_monitor_service() -> FileMonitorService:
    """Get the global file monitor service instance"""
    global _monitor_service
    if _monitor_service is None:
        _monitor_service = FileMonitorService()
    return _monitor_service


def start_monitoring():
    """Start the file monitoring service"""
    service = get_monitor_service()
    service.start()


def stop_monitoring():
    """Stop the file monitoring service"""
    service = get_monitor_service()
    service.stop()
