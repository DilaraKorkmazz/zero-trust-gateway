# Zero-Trust API Gateway

A lightweight reverse proxy and security gateway built with **FastAPI**, designed to enforce perimeter defense and access control before forwarding traffic to internal microservices.

---

## Key Features

- **Zero-Trust Access Control (RBAC):** Strict JWT verification and role checking (`admin` vs. `user`) at the edge.
- **Sliding Window Rate Limiter:** Protects internal routes against brute-force and DDoS attempts (configured to 5 requests/minute per IP, returns `429 Too Many Requests`). Supports Redis with an in-memory fallback.
- **Immutable Audit Trail:** Structured JSON logging (`audit.log`) recording client IP, HTTP method, target path, execution latency, and response status codes.
- **Docker Ready:** Containerized setup for edge deployment alongside Redis and upstream services.

---

## Architecture

```text
Incoming Request
       │
       ▼
┌─────────────────────────────────────────┐
│        Zero-Trust API Gateway           │
│  - Middleware: Audit Logging            │
│  - Rate Limiter: Redis / In-Memory      │
│  - Security: JWT & RBAC Engine          │
└──────────────────┬──────────────────────┘
                   │  (Forwarding only if authorized)
                   ▼
┌─────────────────────────────────────────┐
│     Internal Upstream Microservice      │
│          (Port 8001: /admin-stats)      │
└─────────────────────────────────────────┘
