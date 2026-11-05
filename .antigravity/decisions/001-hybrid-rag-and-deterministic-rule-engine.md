# ADR 001: Hybrid Architecture — Separating Soft Semantics from Deterministic Rule Logic

## Status
**Accepted**

## Context
In public welfare administration, eligibility criteria contain rigid legal and mathematical conditions:
- Strict income ceilings (e.g., Annual family income $\le ₹2,50,000$).
- Exact age limits (e.g., Age between 18 and 35 years).
- Specific caste, tribe, or minority categorizations (e.g., SC, ST, OBC).
- Specific geographic residency (e.g., Citizen of Telangana).

When relying solely on Generative AI (LLMs) or traditional naive RAG:
1. LLMs frequently hallucinate mathematical comparisons (e.g., evaluating ₹2,60,000 as $\le$ ₹2,50,000, or miscalculating dates of birth).
2. Probabilistic text generation cannot guarantee 100% adherence to strict legal rules.
3. False positives misguide citizens into filing futile applications; false negatives deny rightful benefits to disadvantaged individuals.

## Decision
We adopted a **Hybrid Architecture** inspired by the **KGLens** and **Self-RAG** paradigms:
1. **Soft Knowledge (Semantic Discovery):** Natural language intent parsing and broad discovery of candidate schemes are handled via high-dimensional vector embeddings (`text-embedding-004` + FAISS).
2. **Hard Knowledge (Deterministic Rule Engine):** All eligibility criteria are stored as structured JSON conditions in the relational database (`annual_income <= 250000`, `age <= 25`, `category IN ['SC', 'ST', 'OBC']`).
3. An explicit Python Rule Engine (`app.verification.rule_engine`) deterministically checks the user's demographic profile against these rules using hard-coded comparison logic:
   - Outputting distinct statuses: `SATISFIED`, `NOT_SATISFIED`, or `UNKNOWN`.
   - Aggregating into scheme statuses: `LIKELY_ELIGIBLE`, `POSSIBLY_ELIGIBLE`, `NOT_ELIGIBLE`, or `INSUFFICIENT_INFORMATION`.
4. The LLM is **never** permitted to decide numerical or categorical eligibility on its own.

## Consequences

### Positive
- **Zero Hallucination on Cutoffs:** Numerical inequalities and categorical memberships are calculated with 100% mathematical precision.
- **Explainability:** The system can report exactly which rules were met and which failed (e.g., *"Failed: Annual income of ₹3,00,000 exceeds maximum allowable ₹2,50,000"*).
- **Separation of Concerns:** Administrators can update eligibility numbers in the database without re-indexing embeddings or retraining prompts.

### Negative / Trade-offs
- Requires structured modeling of scheme eligibility rules in the database during the ingestion phase.
- Unstructured rules that cannot be reduced to simple boolean/numeric conditions require manual categorization or fall into the `UNKNOWN` state for manual review.
