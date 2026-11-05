# ADR 005: Real-Time Agentic Observability via Server-Sent Events (SSE)

## Status
**Accepted**

## Context
Multi-agent systems executing multi-step workflows (intent parsing $\rightarrow$ vector retrieval $\rightarrow$ deterministic rule evaluation $\rightarrow$ document verification) take between 2 to 4 seconds to execute end-to-end.
In traditional synchronous HTTP request/response:
- The user is left staring at an unresponsive loading spinner.
- The user has zero visibility into whether the AI parsed their query accurately, which state was filtered, or why a decision was reached.
- This "black box" experience reduces user confidence and increases perceived latency.

Alternatives considered:
1. **Polling:** Client makes periodic GET requests. Inefficient, introduces race conditions and unnecessary server load.
2. **WebSockets:** Full bidirectional communication. Over-engineered for what is essentially a unidirectional stream from server to client; introduces connection state management and firewall/proxy complexities.
3. **Server-Sent Events (SSE):** Standard HTTP unidirectional streaming protocol (`text/event-stream`).

## Decision
We implemented **Server-Sent Events (SSE)** via FastAPI's `StreamingResponse` at `GET /api/v1/analyze/stream`:
- The backend iterates over `app_workflow.stream(initial_state)` from LangGraph.
- As each agent node finishes execution, the backend yields an event chunk:
  ```
  data: {"type": "step", "node": "coordinator"}

  data: {"type": "step", "node": "retriever"}

  data: {"type": "step", "node": "eligibility_engine"}

  data: {"type": "step", "node": "verification"}
  ```
- Upon completion, the backend emits a final event containing the complete verified results:
  ```
  data: {"type": "result", "data": { ... }}
  ```
- If an exception occurs, a typed error event is streamed gracefully without breaking the HTTP connection:
  ```
  data: {"type": "error", "message": "..."}
  ```
- On the frontend (`Analyze.tsx`), an `EventSource` (or streamed `fetch`) receives events in real time, animating the multi-agent progress checklist.

## Consequences

### Positive
- **Drastically Reduced Perceived Latency:** Users see visual confirmation within 200-300ms of submitting a query.
- **Trust & Explainability:** Users can visually verify that their intent was parsed and that official documents are being verified.
- **Standard HTTP:** Operates over standard HTTP/HTTPS ports without requiring specialized WebSocket proxies or custom protocols.

### Negative / Trade-offs
- HTTP/1.1 connections have a per-browser domain limit of 6 simultaneous SSE connections (though HTTP/2 multiplexing removes this limit).
- Requires careful handling of connection termination on the client side to avoid orphaned server generator tasks.
