# ADR 002: Multi-Agent Orchestration Using LangGraph

## Status
**Accepted**

## Context
A single prompt or monolithic LLM chain cannot handle the end-to-end welfare analysis pipeline because the process involves disparate cognitive steps:
1. Parsing ambiguous, messy natural language queries and extracting filters.
2. Querying external dense vector indexes and applying relational filters.
3. Executing deterministic mathematical rule checks.
4. Auditing claims and generating verbatim citations from source PDFs.

Simple sequential chains (e.g., standard LangChain `SequentialChain`) lack fine-grained state management, circular reflection capability, and streaming observability. Autonomous ReAct agent loops without strict state transitions can veer off-course, introduce unnecessary latency, or loop unpredictably.

## Decision
We chose **LangGraph** (`StateGraph`) to orchestrate the multi-agent workflow:
- A strongly typed `AgentState` is passed between discrete nodes.
- **Node 1 (`coordinator`):** Natural language intent parser powered by Gemini 2.5 Flash with structured JSON output.
- **Node 2 (`retriever`):** Hybrid vector search and SQL filter executor.
- **Node 3 (`eligibility_engine`):** Python deterministic rule evaluator.
- **Node 4 (`verification`):** Self-reflective auditor checking claims against raw PDF document chunks.
- Edges define deterministic flow transitions:
  $$\text{entry} \longrightarrow \text{coordinator} \longrightarrow \text{retriever} \longrightarrow \text{eligibility\_engine} \longrightarrow \text{verification} \longrightarrow \text{END}$$

## Consequences

### Positive
- **Deterministic Agent Flow:** Prevents agents from entering infinite autonomous loops or deviating from business policy.
- **Native Streaming Support:** LangGraph's `.stream()` method yields state updates after each node executes, enabling real-time Server-Sent Events (SSE) on the frontend.
- **Testability & Isolation:** Each node is a pure or parameterized Python function that can be unit tested in complete isolation without running the entire pipeline.
- **Extensibility:** Facilitates future conditional branches (e.g., human-in-the-loop review nodes, dynamic re-retrieval on low confidence).

### Negative / Trade-offs
- Adds a dependency on `langgraph` and `langchain-core`.
- Graph state modifications must adhere to a strict shared dictionary schema (`AgentState`).
