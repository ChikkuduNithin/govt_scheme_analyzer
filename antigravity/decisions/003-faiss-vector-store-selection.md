# ADR 003: Selection of FAISS as Local Dense Vector Store

## Status
**Accepted**

## Context
Retrieval-Augmented Generation requires searching hundreds to thousands of chunked government scheme documents based on semantic vector similarity.
Several vector store options were evaluated:
1. **PostgreSQL + pgvector:** Industry-standard relational + vector extension.
2. **Cloud Vector Databases (Pinecone, Weaviate, Qdrant):** Hosted vector engines.
3. **FAISS (Facebook AI Similarity Search):** High-performance, in-memory C++ library with Python bindings.

Key constraints:
- The system must run smoothly on local development machines and lightweight servers without mandating external cloud subscriptions or complex Docker setups for pgvector.
- Fast startup and minimal latency for similarity queries.
- Clean persistence to disk for easy backups and distribution.

## Decision
We selected **FAISS** with an `IndexFlatIP` (Inner Product on $L_2$-normalized vectors) paired with Python `pickle` metadata storage:
- Chunks are embedded into 768-dimensional vectors.
- Vectors are $L_2$-normalized using `faiss.normalize_L2()`, making Inner Product mathematically equivalent to Cosine Similarity.
- The FAISS index is serialized to `faiss_index.bin` and the chunk ID mapping is serialized to `faiss_meta.pkl`.
- Relational metadata remains in SQLite/PostgreSQL, avoiding duplicate metadata overhead in the vector store.

## Consequences

### Positive
- **Zero External Infrastructure:** Runs locally without running a dedicated vector DB service or requiring Postgres C-extensions.
- **Sub-Millisecond Search:** `IndexFlatIP` executes exact brute-force cosine similarity across thousands of vectors in $< 2\text{ms}$.
- **Simplicity:** Index and metadata are self-contained files that can be easily committed, seeded (`seed_real.py`), or transferred.

### Negative / Trade-offs
- In-memory storage scales with dataset size; for hundreds of thousands of documents, an approximate index (e.g., `IndexIVFFlat` or `HNSW`) or distributed vector database (e.g., Qdrant/Milvus) would be necessary.
- Concurrency for real-time document insertions requires atomic writes or thread locking around `faiss_store.save()`.
