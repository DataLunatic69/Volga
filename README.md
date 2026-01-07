# NexCell AI Receptionist - Backend API

AI-powered real estate CRM backend built with FastAPI, PostgreSQL, Redis, and Celery.

## Prerequisites

- Python 3.13+
- PostgreSQL (Supabase)
- Redis (Upstash or local)
- Gmail account (for email sending)

## Quick Start

### 1. Install UV Package Manager

```bash
pip install uv
```

### 2. Clone and Setup Project

```bash
# Clone the repository
git clone <repository-url>
cd Volga

# Install dependencies and create virtual environment
uv sync

# Activate virtual environment
source .venv/bin/activate
```

### 3. Environment Configuration

Create a `.env` file in the project root with the following variables:

```env
# Database (Supabase)
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database

# Redis
REDIS_URL=rediss://default:password@host:6379

# JWT
JWT_SECRET_KEY=your-256-bit-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# Email (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_FROM_NAME=NexCell AI Receptionist
MAIL_STARTTLS=True
MAIL_SSL_TLS=False

# Backend Domain (for email links)
BACKEND_DOMAIN=http://localhost:8000

# Application
APP_NAME=NexCell AI Receptionist
ENVIRONMENT=development
DEBUG=True
API_PORT=8000
```

**Note:** For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

### 4. Database Setup

```bash
# Run migrations
uv run alembic upgrade head

# Seed default roles and permissions (optional)
uv run python scripts/seed_permissions.py
```

### 5. Make Scripts Executable

```bash
chmod +x run.sh
chmod +x scripts/start_celery_worker.sh
chmod +x scripts/start_celery_beat.sh
```

### 6. Start Services

#### Terminal 1: Start Celery Worker (for background email tasks)

```bash
./scripts/start_celery_worker.sh
```

Or manually:
```bash
celery -A app.workers.celery_app worker \
    --loglevel=info \
    --queues=email_queue \
    --concurrency=4 \
    --hostname=worker@%h
```

#### Terminal 2: Start FastAPI Server

```bash
./run.sh
```

Or manually:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Terminal 3: Start Celery Beat (optional - for periodic tasks)

```bash
./scripts/start_celery_beat.sh
```

### 7. Verify Setup

```bash
# Test connections (database, Redis, email, etc.)
uv run python scripts/test_connections.py
```

## API Documentation

Once the server is running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Project Structure

```
Volga/
├── app/
│   ├── api/              # API endpoints and middlewares
│   ├── auth/             # Authentication & authorization
│   ├── core/              # Core utilities (logging, rate limiting)
│   ├── database/          # Database models and session
│   ├── services/          # Business logic services
│   ├── workers/           # Celery workers and tasks
│   └── templates/         # Email templates
├── alembic/               # Database migrations
├── scripts/               # Utility scripts
└── tests/                 # Test files
```

## Common Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Run database migrations
uv run alembic upgrade head

# Create new migration
uv run alembic revision --autogenerate -m "description"


```

## Troubleshooting

### Celery Worker Not Processing Tasks

1. Ensure worker is listening to `email_queue`:
   ```bash
   celery -A app.workers.celery_app worker --queues=email_queue --loglevel=info
   ```

2. Check Redis connection in worker logs

3. Verify task routing in `app/workers/celery_app.py`

### Email Not Sending

1. Verify Gmail App Password is correct
2. Check Celery worker logs for errors
3. Test email configuration:
   ```bash
   uv run python scripts/test_connections.py
   ```

### Database Connection Issues

1. Verify `DATABASE_URL` format: `postgresql+asyncpg://...`
2. Check Supabase connection settings
3. Ensure migrations are up to date

## Development

### Adding New Dependencies

```bash
uv add package-name
```

### Code Style

- Follow PEP 8
- Use type hints
- Run `ruff check .` before committing

## License

[Your License Here]

