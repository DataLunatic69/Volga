"""Deployment Guide."""

# Deployment Documentation

## Prerequisites

- Docker and Docker Compose
- Python 3.9+
- PostgreSQL (for production)
- Redis (for production)
- OpenAI API key
- WhatsApp Business Account

## Environment Setup

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your configuration values.

## Local Development

### Using Docker Compose

```bash
docker-compose up
```

This starts:
- FastAPI backend (port 8000)
- PostgreSQL database
- Redis cache

### Without Docker

```bash
# Install dependencies
pip install -r requirements.txt

# Setup database
python scripts/setup_db.py

# Run server
python scripts/start_local.py
```

## Production Deployment

### Docker Build

```bash
docker build -t nexcell-ai-backend:latest .
```

### Kubernetes Deployment

```bash
kubectl apply -f k8s/
```

### Environment Variables

Required environment variables:

- `WHATSAPP_PHONE_ID`: WhatsApp phone ID
- `WHATSAPP_ACCESS_TOKEN`: WhatsApp API token
- `OPENAI_API_KEY`: OpenAI API key
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection URL

## Database Migrations

```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

## Health Checks

```bash
# Health endpoint
curl http://localhost:8000/health/

# Readiness endpoint
curl http://localhost:8000/health/ready
```

## Monitoring

- Application logs in `/var/log/nexcell/`
- Metrics available via Prometheus endpoint
- ELK stack for log aggregation (optional)
