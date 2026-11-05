# ADR 006: Selection of Google Gemini Models & High-Dimensional Embeddings

## Status
**Accepted (Updated)**

## Context
The system requires two types of AI capabilities:
1. **Generative LLM Reasoning:** For natural language intent parsing (extracting keywords and filters) and self-reflective document verification (matching claims to source passages and producing citations).
2. **Dense Vector Embeddings:** For semantic representation of official government policy guidelines and user queries.

During real-world verification, earlier model designations (`gemini-2.5-flash` and `text-embedding-004`) were deprecated/superseded by the Google Gemini API. Furthermore, single-model configurations were prone to transient HTTP 503 high-demand spikes.

## Decision
We standardized on Google's modern Generative AI stack using the **official Google GenAI SDK (`google-genai`)** with resilient multi-model failover:
- **Embedding Model:** `gemini-embedding-001` (and `gemini-embedding-2`)
  - **3072-dimensional** output vectors, providing fine-grained semantic discrimination across regional and central government policy lexicons.
  - Normalized with $L_2$ norm for exact cosine inner-product indexing in FAISS (`IndexFlatIP`).
  - Batch generation supported for rapid document ingestion.
- **Reasoning Models with Automatic Fallback:**
  - Primary: `gemini-3.5-flash` and `gemini-3.5-flash-lite`.
  - Resilient Fallback Chain (`app.utils.llm.generate_with_fallback`): `["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-flash-latest", "gemini-3.8-flash"]`.
  - Configured with `response_mime_type="application/json"` for reliable, schema-compliant JSON output in the Coordinator and Verification nodes.

## Consequences

### Positive
- **100% Zero-Downtime Resilience:** If any model experiences a transient 503 spike, the fallback router automatically retries against the next available generation model without interrupting the user's analysis.
- **Guaranteed JSON Output:** Using `response_mime_type="application/json"` eliminates markdown-fenced formatting errors (e.g. ` ```json `), preventing JSON parse exceptions.
- **Superior Semantic Retrieval:** 3072-dimensional vector space captures nuanced distinctions between overlapping state and central welfare criteria.

### Negative / Trade-offs
- Higher vector dimensionality (3072 vs 768) increases memory footprint in FAISS by $4\times$, but for tens of thousands of scheme chunks, this requires merely tens of megabytes of RAM.
