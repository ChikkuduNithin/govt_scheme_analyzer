# ADR 009: FastAPI Framework with SQLAlchemy ORM and SQLite Database

## Status
**Accepted**

## Context
The backend requires:
- High asynchronous concurrency for handling streaming endpoints (Server-Sent Events) alongside standard CRUD operations.
- Strong typing and automatic OpenAPI documentation generation.
- A robust relational abstraction for Users, Schemes, Documents, and Eligibility Rules.
- Zero-friction developer setup for rapid local prototyping without requiring external database server dependencies.

Evaluated options:
- **Django / Django REST Framework:** Robust but synchronous by default, heavy boilerplate, complex async streaming setup.
- **Node.js (Express / NestJS):** Fast async, but Python is mandatory for direct integration with LangGraph, PyTorch/FAISS, and the Google GenAI SDK.
- **FastAPI + SQLAlchemy + SQLite (with PostgreSQL migration path):** High-performance async Python framework with native Pydantic validation, OpenAPI docs, and clean ORM abstractions.

## Decision
We chose **FastAPI** paired with **SQLAlchemy ORM** and a **SQLite** database (`scheme_analyzer.db`):
1. **Async FastAPI Endpoints:**
   - Asynchronous generators (`async def run_agent_stream`) power the SSE `/stream` endpoint.
   - Dependency injection (`deps.get_db`, `deps.get_current_active_user`) cleanly manages session lifecycles and JWT authentication.
2. **SQLAlchemy Relational Models:**
   - `User` & `UserProfile`: Citizen identity and demographic attributes.
   - `Scheme`: Government scheme metadata.
   - `EligibilityRule`: Structured JSON condition criteria.
   - `Document` & `DocumentChunk`: Text chunks and embedding pointers.
3. **Storage Fallback Strategy:**
   - Default configuration uses `sqlite:///./scheme_analyzer.db` for instant, standalone execution without launching a PostgreSQL daemon.
   - Models and migrations (`alembic`) are built standard-compliant so switching to PostgreSQL for enterprise deployments requires only updating `DATABASE_URI` in `.env`.

## Consequences

### Positive
- **Instant Onboarding:** Developers and evaluators can clone the repository, install dependencies, run `python seed_real.py`, and launch immediately with zero database infrastructure.
- **Async Streaming:** FastAPI's `StreamingResponse` integrates smoothly with LangGraph's streaming generators.
- **Auto-generated Documentation:** Interactive Swagger UI available at `/docs` out of the box.

### Negative / Trade-offs
- SQLite has database-level write locks under high concurrent write loads (mitigated because scheme analysis is almost exclusively read-only; admin writes can be migrated to PostgreSQL in production).
