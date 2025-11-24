from app.db import SessionLocal
from app.models import User
from app.auth import get_password_hash
from datetime import datetime, timezone

def seed_data():
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.username == 'admin').first()
        if existing_admin:
            print("Admin user already exists.")
            return

        # Create admin user
        admin = User(
            username='admin',
            password_hash=get_password_hash('adminpass'),
            role='admin',
            created_at=datetime.now(tz=timezone.utc)
        )
        db.add(admin)
        db.commit()
        print("Admin user created successfully!")
        print("Username: admin")
        print("Password: adminpass")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
