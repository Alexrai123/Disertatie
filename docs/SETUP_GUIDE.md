y# Secure AI Monitoring Sandbox - Setup Guide

## Prerequisites

### Required Software
- **Python 3.10+** - Backend runtime
- **Node.js 18+** - Frontend runtime
- **PostgreSQL 14+** - Database
- **Git** - Version control

### Optional
- **Docker** - Containerized deployment
- **VS Code** - Recommended IDE

---

## Backend Setup

### 1. Navigate to Backend Directory
```powershell
cd backend
```

### 2. Create Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

**Dependencies Include:**
- FastAPI - Web framework
- SQLAlchemy - ORM
- Alembic - Database migrations
- bcrypt - Password hashing
- slowapi - Rate limiting
- watchdog - File monitoring
- email-validator - Input validation

### 4. Configure Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/secure_ai_sandbox

# JWT Authentication
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Monitoring
FILE_MONITOR_ENABLED=true
FILE_MONITOR_RECURSIVE=true

# Rate Limiting
AUTH_RATE_LIMIT=5/minute
WRITE_RATE_LIMIT=20/minute
READ_RATE_LIMIT=100/minute
HEALTH_RATE_LIMIT=200/minute

# Password Policy
MIN_PASSWORD_LENGTH=8
REQUIRE_UPPERCASE=true
REQUIRE_LOWERCASE=true
REQUIRE_DIGIT=true
REQUIRE_SPECIAL_CHAR=true

# Email Notifications (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
NOTIFICATION_FROM_EMAIL=noreply@example.com
NOTIFICATION_BATCH_INTERVAL=300
```

### 5. Setup Database

**Create Database:**
```powershell
# Using psql
createdb secure_ai_sandbox

# Or using PostgreSQL GUI (pgAdmin, DBeaver, etc.)
```

**Run Migrations:**
```powershell
alembic upgrade head
```

This creates:
- `users` table
- `folders` table
- `files` table
- `events` table
- `ai_rules` table
- `ai_feedback` table
- `logs` table
- Database indices for performance

### 6. Create Admin User

Run Python script to create initial admin:

```powershell
python -c "
from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash
from datetime import datetime, timezone

db = SessionLocal()
admin = User(
    username='admin',
    password_hash=get_password_hash('adminpass'),
    role='admin',
    created_at=datetime.now(tz=timezone.utc)
)
db.add(admin)
db.commit()
print('Admin user created!')
db.close()
"
```

**Default Credentials:**
- Username: `admin`
- Password: `adminpass`

⚠️ **Change these in production!**

### 7. Start Backend Server

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Server will run at:** `http://localhost:8000`

**API Documentation:** `http://localhost:8000/docs`

---

## Frontend Setup

### 1. Navigate to Frontend Directory
```powershell
cd frontend
```

### 2. Install Dependencies
```powershell
npm install
```

**Dependencies Include:**
- React 18 - UI framework
- React Router - Navigation
- Axios - HTTP client
- TypeScript - Type safety

### 3. Configure API URL

Edit `frontend/src/api.ts` if needed:

```typescript
const api = axios.create({
  baseURL: 'http://localhost:8000',  // Backend URL
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### 4. Start Development Server

```powershell
npm run dev
```

**Frontend will run at:** `http://localhost:5173`

### 5. Build for Production

```powershell
npm run build
```

Output in `dist/` directory.

---

## Verification

### 1. Check Backend Health
```powershell
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 2. Test Login

Open browser to `http://localhost:5173`

Login with:
- Username: `admin`
- Password: `adminpass`

### 3. Add Test Folder

1. Navigate to **Folders** page
2. Click **Add Folder**
3. Enter:
   - Name: `Test Folder`
   - Path: `C:\Users\YourUsername\Documents` (or any valid path)
4. Click **Create**

File monitoring will automatically start for this folder.

### 4. Verify File Monitoring

**Check monitoring status:**
```powershell
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/monitoring/status
```

Expected response:
```json
{
  "is_running": true,
  "watched_folders_count": 1,
  "uptime_seconds": 120
}
```

---

## Running Tests

### Backend Tests

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest tests/ -v
```

**Test Coverage:**
- Input validation (40+ tests)
- Rate limiting
- File monitoring
- Authentication
- AI rules and feedback
- Event processing

### Frontend Tests (Future)

```powershell
cd frontend
npm test
```

---

## Troubleshooting

### Database Connection Error
**Error:** `could not connect to server`

**Solution:**
1. Ensure PostgreSQL is running
2. Check `DATABASE_URL` in `.env`
3. Verify database exists: `psql -l`

### Port Already in Use
**Error:** `Address already in use`

**Solution:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F
```

### File Monitoring Not Working
**Error:** Events not being created

**Solution:**
1. Check `FILE_MONITOR_ENABLED=true` in `.env`
2. Verify folder path is absolute
3. Check backend logs for errors
4. Ensure folder exists and is accessible

### Frontend Can't Connect to Backend
**Error:** `Network Error`

**Solution:**
1. Verify backend is running on port 8000
2. Check CORS settings in `app/main.py`
3. Ensure `baseURL` in `api.ts` is correct

### Rate Limit Errors
**Error:** `429 Too Many Requests`

**Solution:**
- Wait for rate limit window to reset
- Adjust rate limits in `.env` for development
- Use different endpoints (they have different limits)

---

## Production Deployment

### Environment Variables
Update `.env` with production values:
- Strong `SECRET_KEY` (use `openssl rand -hex 32`)
- Production database URL
- Real SMTP credentials
- Appropriate rate limits

### Security Checklist
- [ ] Change default admin password
- [ ] Use HTTPS (SSL/TLS)
- [ ] Set strong `SECRET_KEY`
- [ ] Configure firewall rules
- [ ] Enable database backups
- [ ] Set up monitoring/logging
- [ ] Review rate limits
- [ ] Disable debug mode

### Docker Deployment (Optional)

```powershell
# Build and run with Docker Compose
docker-compose up -d
```

---

## Next Steps

1. **Add AI Rules** - Configure custom detection rules
2. **Set Up Email** - Configure SMTP for notifications
3. **Monitor Events** - Check Events page for file changes
4. **Review Logs** - Check system logs for AI decisions
5. **Provide Feedback** - Train AI by approving/rejecting decisions

---

## Support

- **Documentation:** `/docs/` directory
- **API Docs:** `http://localhost:8000/docs`
- **Issues:** Check logs in `backend/logs/`

---

## Architecture Overview

```
┌─────────────────┐
│   Frontend      │  React + TypeScript
│   (Port 5173)   │  Modern UI with dark theme
└────────┬────────┘
         │ HTTP/REST
         ↓
┌─────────────────┐
│   Backend       │  FastAPI + Python
│   (Port 8000)   │  JWT Auth, Rate Limiting
└────────┬────────┘
         │
    ┌────┴────┬─────────────┐
    ↓         ↓             ↓
┌────────┐ ┌──────────┐ ┌──────────┐
│Database│ │File      │ │AI Engine │
│Postgres│ │Monitor   │ │Adaptive  │
└────────┘ └──────────┘ └──────────┘
```

---

## Features Enabled

✅ **Security**
- bcrypt password hashing
- JWT authentication
- Input validation & sanitization
- Rate limiting
- Path traversal prevention

✅ **File Monitoring**
- Real-time file system watching
- Automatic event creation
- Recursive directory monitoring
- Create/Modify/Delete detection

✅ **AI Engine**
- Adaptive learning from feedback
- Rule caching (60s TTL)
- Weighted severity calculation
- Notification batching

✅ **Frontend**
- Modern dark theme UI
- Responsive design
- Real-time updates
- Admin dashboard
- Filtering & pagination

---

## Development Tips

### Hot Reload
Both frontend and backend support hot reload:
- Backend: `--reload` flag in uvicorn
- Frontend: Vite dev server auto-reloads

### Database Migrations
After model changes:
```powershell
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### API Testing
Use built-in Swagger UI:
`http://localhost:8000/docs`

### Debugging
Enable debug logging in `.env`:
```bash
LOG_LEVEL=DEBUG
```

---

**Setup Complete! 🎉**

Your Secure AI Monitoring Sandbox is ready to use.
