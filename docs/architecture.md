"""System Architecture Documentation."""

# Architecture Overview

## System Design

### Multi-Agent System

The application uses a LangGraph-based multi-agent system with the following agents:

1. **Receptionist Agent**
   - Initial greeting and intent detection
   - Extracts user requirements and language

2. **Qualifier Agent**
   - Evaluates lead quality
   - Calculates qualification scores
   - Routes qualified/unqualified leads

3. **Property Expert Agent**
   - Searches property database using vector embeddings
   - Provides personalized property recommendations
   - Handles property inquiries

4. **Booking Agent**
   - Manages property viewing appointments
   - Handles availability checks and confirmation
   - Sends booking confirmations

5. **Follow-up Agent**
   - Manages post-engagement follow-ups
   - Schedules reminder messages
   - Handles nurture campaigns

6. **Supervisor Agent**
   - Routes conversations between agents
   - Manages workflow orchestration

### Technology Stack

- **Framework**: FastAPI
- **AI/ML**: LangGraph, LangChain, OpenAI GPT-4
- **Database**: PostgreSQL (primary), SQLite (dev)
- **Vector DB**: Chroma/Pinecone
- **Cache**: Redis
- **Messaging**: WhatsApp Business API, Twilio (future)
- **Deployment**: Docker, Kubernetes

### Data Flow

```
WhatsApp Message
    ↓
Webhook Handler
    ↓
Message Processor
    ↓
LangGraph Workflow
    ↓
Agent Routing
    ↓
Business Logic
    ↓
Database/Vector DB
    ↓
Response Generation
    ↓
WhatsApp API
    ↓
User Message
```

### Key Components

- **app/**: Main application code
- **app/core/**: AI agents and workflow logic
- **app/api/**: API endpoints and webhooks
- **app/database/**: Data models and CRUD operations
- **app/services/**: Business services
- **app/integrations/**: External service integrations
- **tests/**: Test suite
- **data/**: Sample data and embeddings

## Scalability Considerations

- Message queue for high-volume message processing
- Horizontal scaling of agent workers
- Vector DB replication for availability
- Redis caching for conversation state
- Database connection pooling
