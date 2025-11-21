# Secure AI Monitoring Sandbox - API Documentation

## Overview
FastAPI-based backend with JWT authentication, real-time file monitoring, and AI-powered event analysis.

## Base URL
```
http://localhost:8000
```

## Authentication
All endpoints except `/auth/login` and `/health` require JWT authentication.

**Headers:**
```
Authorization: Bearer <token>
```

---

## Authentication Endpoints

### POST `/auth/login`
Login and receive JWT token.

**Request:**
```json
{
  "username": "admin",
  "password": "adminpass"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
}
```

**Rate Limit:** 5 requests/minute

---

## Folder Endpoints

### GET `/folders/`
List all monitored folders with pagination.

**Query Parameters:**
- `limit` (int, default: 100) - Max results
- `offset` (int, default: 0) - Skip results

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Documents",
      "path": "C:\\Users\\Alex\\Documents",
      "owner_id": 1,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0,
  "has_more": false
}
```

**Rate Limit:** 100 requests/minute

### POST `/folders/`
Create a new monitored folder.

**Request:**
```json
{
  "name": "Documents",
  "path": "C:\\Users\\Alex\\Documents"
}
```

**Validation:**
- Path must be absolute
- No directory traversal (`..`)
- Name: 1-255 characters

**Response:** 201 Created

**Rate Limit:** 20 requests/minute

### DELETE `/folders/{id}`
Remove a folder from monitoring.

**Response:** 204 No Content

**Rate Limit:** 20 requests/minute

---

## File Endpoints

### GET `/files/`
List all monitored files with pagination.

**Query Parameters:**
- `limit` (int, default: 100)
- `offset` (int, default: 0)

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "report.pdf",
      "path": "C:\\Users\\Alex\\Documents\\report.pdf",
      "folder_id": 1,
      "owner_id": 1
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

### POST `/files/`
Add a file to monitoring.

**Request:**
```json
{
  "name": "report.pdf",
  "path": "C:\\Users\\Alex\\Documents\\report.pdf",
  "folder_id": 1
}
```

**Rate Limit:** 20 requests/minute

---

## Event Endpoints

### GET `/events/`
List file system events with filtering and pagination.

**Query Parameters:**
- `limit` (int, default: 50)
- `offset` (int, default: 0)
- `event_type` (string) - Filter: `create`, `modify`, `delete`
- `processed_flag` (bool) - Filter by processing status

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "event_type": "modify",
      "timestamp": "2024-01-01T12:00:00Z",
      "target_file_id": 1,
      "target_folder_id": null,
      "processed_flag": true,
      "ai_severity": "Medium"
    }
  ],
  "total": 1,
  "has_more": false
}
```

**Rate Limit:** 100 requests/minute

---

## Log Endpoints

### GET `/logs/`
Retrieve system logs.

**Response:**
```json
[
  {
    "id": 1,
    "log_type": "NOTIFY",
    "message": "High severity event detected",
    "timestamp": "2024-01-01T12:00:00Z",
    "related_event_id": 1
  }
]
```

**Log Types:**
- `NOTIFY` - Notification sent
- `ESCALATE` - Escalation created
- `AI_FEEDBACK` - AI learning event

---

## AI Rules Endpoints (Admin Only)

### GET `/ai-rules/`
List AI decision rules.

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "rule_name": "Sensitive File Modified",
      "pattern": "*.docx",
      "severity_level": "High",
      "action": "notify",
      "adaptive_flag": true,
      "weight": 1.2
    }
  ]
}
```

### POST `/ai-rules/`
Create a new AI rule.

**Request:**
```json
{
  "rule_name": "Sensitive File Modified",
  "pattern": "*.docx",
  "severity_level": "High",
  "action": "notify"
}
```

**Severity Levels:** `Low`, `Medium`, `High`, `Critical`

**Actions:** `notify`, `escalate`, `log`

---

## File Monitoring Endpoints (Admin Only)

### GET `/monitoring/status`
Get file monitoring service status.

**Response:**
```json
{
  "is_running": true,
  "watched_folders_count": 5,
  "uptime_seconds": 3600
}
```

---

## Health Check

### GET `/health`
Check API health.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Rate Limit:** 200 requests/minute (lenient)

---

## Rate Limiting

Different endpoints have different rate limits:

- **Auth endpoints:** 5 requests/minute
- **Write endpoints:** 20 requests/minute
- **Read endpoints:** 100 requests/minute
- **Health endpoint:** 200 requests/minute

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

**429 Response:**
```json
{
  "error": "Rate limit exceeded"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Validation error",
  "detail": "Path must be absolute"
}
```

### 401 Unauthorized
```json
{
  "error": "Invalid credentials"
}
```

### 403 Forbidden
```json
{
  "error": "Admin access required"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "path"],
      "msg": "Directory traversal detected",
      "type": "value_error"
    }
  ]
}
```

---

## Security Features

### Input Validation
- **Path Validation:** Prevents directory traversal (`..`)
- **Password Requirements:** 8+ chars, uppercase, lowercase, digit, special char
- **Username:** 3-50 alphanumeric characters
- **String Length Limits:** Prevents DoS attacks

### Authentication
- **JWT Tokens:** Secure, stateless authentication
- **bcrypt Hashing:** Industry-standard password hashing
- **Role-Based Access:** Admin vs User permissions

### Rate Limiting
- **Endpoint-Specific Limits:** Stricter on auth/write operations
- **IP-Based Tracking:** Per-client rate limiting

---

## AI Engine Features

### Adaptive Learning
The AI engine learns from admin feedback:
- Approved decisions increase rule weights
- Rejected decisions decrease rule weights
- Severity thresholds adjust based on patterns

### Rule Caching
- Rules cached for 60 seconds
- Reduces database load
- Automatic cache invalidation

### Notification Batching
- Notifications batched every 5 minutes
- Prevents email spam
- Retry logic (3 attempts) for failed emails

### Weighted Severity Calculation
```
final_severity = base_severity * rule_weight * pattern_match_score
```

---

## Configuration

Environment variables (`.env`):

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/db

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Monitoring
FILE_MONITOR_ENABLED=true
FILE_MONITOR_RECURSIVE=true

# Rate Limiting
AUTH_RATE_LIMIT=5/minute
WRITE_RATE_LIMIT=20/minute
READ_RATE_LIMIT=100/minute

# Password Policy
MIN_PASSWORD_LENGTH=8
REQUIRE_UPPERCASE=true
REQUIRE_LOWERCASE=true
REQUIRE_DIGIT=true
REQUIRE_SPECIAL_CHAR=true

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## Database Schema

### Tables
- `users` - User accounts
- `folders` - Monitored folders
- `files` - Monitored files
- `events` - File system events
- `ai_rules` - AI decision rules
- `ai_feedback` - Admin feedback for learning
- `logs` - System logs

### Indices (Optimized)
- `ix_events_timestamp` - Event queries by time
- `ix_events_processed_flag` - Unprocessed events
- `ix_events_event_type` - Filter by type
- `ix_logs_log_type` - Filter logs by type
- `ix_ai_rules_severity_level` - Rule queries

---

## WebSocket Support (Future)
Real-time event streaming planned for future release.

---

## Support
For issues or questions, refer to project documentation in `/docs/`.
