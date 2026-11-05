# 🏛️ Architecture Decision Records (ADRs)

This directory maintains the log of all key architectural, technical, and design decisions made for the **Agentic RAG Government Scheme Analyzer** project.

Each record documents the **Context**, the **Decision** taken, and the resulting **Consequences** (positive trade-offs and negative considerations).

---

## 📑 Index of Decisions

| ADR ID | Title | Status | Primary Impact Area |
| :--- | :--- | :--- | :--- |
| [**ADR 001**](file:///c:/Users/nithi/OneDrive/Documents/govt_scheme_analyzer/antigravity/decisions/001-hybrid-rag-and-deterministic-rule-engine.md) | Hybrid Architecture: Separating Soft Knowledge (Embeddings) from Hard Logic (Rule Engine) | `Accepted` | Core AI & Eligibility Accuracy |
| [**ADR 002**](file:///c:/Users/nithi/OneDrive/Documents/govt_scheme_analyzer/antigravity/decisions/002-multi-agent-orchestration-langgraph.md) | Multi-Agent Orchestration Using LangGraph StateGraph | `Accepted` | Agent Workflow & Orchestration |
| [**ADR 003**](file:///c:/Users/nithi/OneDrive/Documents/govt_scheme_analyzer/antigravity/decisions/003-faiss-vector-store-selection.md) | Selection of FAISS as Local Dense Vector Store | `Accepted` | Vector Storage & Infrastructure |
| [**ADR 004**](file:///c:/Users/nithi/OneDrive/Documents/govt_scheme_analyzer/antigravity/decisions/004-two-stage-hybrid-retrieval-strategy.md) | Two-Stage Hybrid Retrieval with Relational Filtering & Lexical Fallback | `Accepted` | Information Retrieval & Recall |
| [**ADR 005**](file:///c:/Users/nithi/OneDrive/Documents/govt_scheme_analyzer/antigravity/decisions/005-realtime-agent-observability-via-sse.md) | Real-Time Agentic Observability via Server-Sent Events (SSE) | `Accepted` | API Streaming & Frontend UX |
| [**ADR 006**](file:///c:/Users/nithi/OneDrive/Documents/govt_scheme_analyzer/antigravity/decisions/006-gemini-and-text-embedding-models.md) | Selection of Google Gemini 2.5 Flash and text-embedding-004 | `Accepted` | LLM Models & GenAI SDK |
| [**ADR 007**](file:///c:/Users/nithi/OneDrive/Documents/govt_scheme_analyzer/antigravity/decisions/007-self-rag-verification-and-source-citation.md) | Self-RAG Verification Agent & Ground-Truth Source Citations | `Accepted` | Fact Verification & Auditability |
| [**ADR 008**](file:///c:/Users/nithi/OneDrive/Documents/govt_scheme_analyzer/antigravity/decisions/008-dynamic-query-overrides-for-user-profiles.md) | Dynamic Non-Destructive Query Profile Overrides | `Accepted` | User Experience & Query Parsing |
| [**ADR 009**](file:///c:/Users/nithi/OneDrive/Documents/govt_scheme_analyzer/antigravity/decisions/009-fastapi-backend-and-sqlite-orm-architecture.md) | FastAPI Framework with SQLAlchemy ORM and SQLite Database | `Accepted` | Backend Architecture & Persistence |
| [**ADR 010**](file:///c:/Users/nithi/OneDrive/Documents/govt_scheme_analyzer/antigravity/decisions/010-react-vite-tailwind-frontend-design.md) | React 18, Vite, and Tailwind CSS v4 Frontend Architecture | `Accepted` | Frontend UI/UX & Build System |

---

## 🛠️ ADR Template

When proposing a new architectural decision, please follow this standard format:

```markdown
# ADR XXX: [Short Title of the Decision]

## Status
[Proposed | Accepted | Superseded | Deprecated]

## Context
[What is the problem, business need, or technical constraint that requires this decision?]

## Decision
[What is the change/decision being committed to? What alternatives were considered and why was this chosen?]

## Consequences
### Positive
[What advantages and benefits does this decision provide?]

### Negative / Trade-offs
[What drawbacks, maintenance overheads, or risks are introduced?]
```
