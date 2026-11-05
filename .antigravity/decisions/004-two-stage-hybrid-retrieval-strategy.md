# ADR 004: Two-Stage Hybrid Retrieval with Relational Filtering & Lexical Fallback

## Status
**Accepted**

## Context
Pure dense vector search on government guidelines can produce false positives:
- A query about "agriculture loans in Telangana" might retrieve an identical-sounding scheme applicable exclusively to Karnataka or Rajasthan because the semantic embeddings for agricultural welfare descriptions are very close.
- A scheme might be semantically relevant but inactive or retired (`is_active == False`).
- Vector search alone lacks awareness of jurisdictional hierarchy (Central vs. State).

Furthermore, if the vector index is empty, uninitialized, or encounters dimension mismatches, a pure vector retriever fails completely.

## Decision
We implemented a **Two-Stage Hybrid Retrieval Strategy** (`app.rag.retriever.retrieve_hybrid`):

1. **Stage 1: Broad Dense Vector Search:**
   - Embed the query using Gemini `text-embedding-004`.
   - Search the FAISS index for the top $N = 20$ nearest candidate chunk IDs.
2. **Stage 2: Relational Filtering (SQLAlchemy):**
   - Join `DocumentChunk` with `Scheme`.
   - Filter candidates to include only active schemes (`Scheme.is_active == True`).
   - Enforce geographic filtering: candidate scheme must either match the user's state (`Scheme.state ILIKE :state`) or be a nationwide Central initiative (`Scheme.state ILIKE '%central%'`).
   - Filter by department if specified by the intent coordinator.
   - Return the top $K = 5$ or $10$ verified candidates.
3. **Resilient Lexical Fallback (`_retrieve_from_database`):**
   - If FAISS search is unavailable, returns empty, or encounters an index error, the system automatically falls back to an SQL keyword frequency search across scheme names, departments, descriptions, and chunk texts.

## Consequences

### Positive
- **Jurisdictional Accuracy:** Eliminates cross-state scheme confusion (e.g., preventing a resident of Telangana from being offered a Maharashtra state subsidy).
- **High Recall & Precision:** Combines the semantic breadth of dense embeddings with the exactness of relational database constraints.
- **Fault Tolerance:** System continues functioning seamlessly even if the FAISS index file is missing or corrupted.

### Negative / Trade-offs
- If Stage 1 candidate pool ($N = 20$) fails to include state-specific candidates due to semantic competition from popular Central schemes, those candidates might be filtered out before Stage 2. (Mitigated by increasing candidate pool $N$ or adding pre-filtering).
