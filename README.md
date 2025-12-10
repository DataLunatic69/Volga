# NexCell AI Receptionist Backend

## Overview

This is the backend service for the NexCell AI Receptionist system - an AI-powered WhatsApp chatbot for property management companies.

## Features

- 🤖 Multi-agent AI system using LangGraph
- 💬 WhatsApp integration for messaging
- 🏢 Property search and recommendations
- 📅 Booking and scheduling management
- 🎯 Lead qualification and nurturing
- 📊 Conversation analytics
- 🔒 GDPR compliance

## Architecture

The system uses a multi-agent architecture with specialized agents:

- **Receptionist Agent**: Initial greeting and intent detection
- **Qualifier Agent**: Lead qualification based on business rules
- **Property Expert Agent**: Property search and recommendations
- **Booking Agent**: Appointment scheduling
- **Follow-up Agent**: Lead nurturing and follow-ups
- **Supervisor Agent**: Workflow orchestration

## Quick Start

### Prerequisites

- Python 3.9+
- Docker and Docker Compose (optional)
- PostgreSQL (for production)
- Redis (for caching)
- OpenAI API key
- WhatsApp Business Account

### Local Development

#### Using Docker Compose

```bash
docker-compose up
```

#### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Run database setup
python scripts/setup_db.py

# Start server
python scripts/start_local.py
```

The API will be available at `http://localhost:8000`

## Project Structure

```
ai-backend/
├── app/                    # Main application
│   ├── api/               # REST and webhook endpoints
│   ├── core/              # AI agents and workflow
│   ├── database/          # Database models and CRUD
│   ├── integrations/      # External service integrations
│   ├── services/          # Business services
│   └── utils/             # Utility functions
├── tests/                 # Test suite
├── data/                  # Sample and reference data
├── scripts/               # Utility and setup scripts
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container configuration
└── docker-compose.yml     # Local development setup
```

## API Documentation

See `docs/api.md` for detailed API documentation.

### Health Check

```bash
curl http://localhost:8000/health/
```

### WhatsApp Webhook

POST endpoint for WhatsApp incoming messages:
```
POST /webhooks/whatsapp
```

## Configuration

Copy `.env.example` to `.env` and configure the required environment variables:

```bash
cp .env.example .env
```

Key variables:
- `WHATSAPP_PHONE_ID`: Your WhatsApp phone ID
- `OPENAI_API_KEY`: OpenAI API key
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection URL

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_webhooks.py
```

## Deployment

See `docs/deployment.md` for deployment instructions.

## Development

### Code Style

- Black for code formatting
- Flake8 for linting
- MyPy for type checking

```bash
black .
flake8 .
mypy .
```

### Creating Migrations

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Documentation

- `docs/api.md` - API endpoints and usage
- `docs/architecture.md` - System architecture
- `docs/testing.md` - Testing guide
- `docs/deployment.md` - Deployment instructions

## License

Proprietary - NexCell AI

## Support

For issues and questions, contact the development team.
