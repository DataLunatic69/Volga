"""API Documentation."""

# NexCell AI Receptionist API

## Overview

The NexCell AI Receptionist Backend provides a multi-agent AI system for WhatsApp-based property inquiries and booking management.

## Base URL

```
http://localhost:8000
```

## Authentication

API endpoints use JWT token authentication.

## Endpoints

### Health Check

- **GET** `/health/`
  - Returns application health status
  - Response: `{ "status": "healthy", "service": "NexCell AI Receptionist", "version": "0.1.0" }`

- **GET** `/health/ready`
  - Returns readiness status and dependency health
  - Response: `{ "ready": true, "dependencies": {...} }`

### WhatsApp Webhooks

- **POST** `/webhooks/whatsapp`
  - Handle incoming WhatsApp messages
  - Body: WhatsApp webhook payload

- **GET** `/webhooks/whatsapp`
  - Verify WhatsApp webhook subscription
  - Query params: `hub_mode`, `hub_challenge`, `hub_verify_token`

### Admin REST API

- **GET** `/api/conversations`
  - Get all conversations
  - Response: List of conversations

- **GET** `/api/conversations/{conversation_id}`
  - Get specific conversation details
  - Response: Conversation object

- **GET** `/api/leads`
  - Get all leads
  - Response: List of leads

- **GET** `/api/properties`
  - Get all properties
  - Response: List of properties

- **POST** `/api/sync-properties`
  - Trigger property synchronization
  - Response: Sync status

- **POST** `/api/test-message`
  - Send a test WhatsApp message
  - Body: `{ "phone_number": string, "message": string }`

## Error Handling

All errors follow standard HTTP status codes and return JSON responses with error details.

## Rate Limiting

API requests are rate-limited. Check response headers for rate limit information.
