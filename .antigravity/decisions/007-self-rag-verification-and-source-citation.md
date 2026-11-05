# ADR 007: Self-RAG Verification Agent & Ground-Truth Source Citations

## Status
**Accepted**

## Context
Even when eligibility rules are deterministically evaluated by a mathematical rule engine, government scheme applicants require **verifiable legal backing**. In real-world interactions with case workers or government portals:
- Citizens must know *which section or page* of the official notification contains the rule.
- If a rule was satisfied or failed, the user needs to see the exact text snippet from the official guideline supporting that conclusion.
- If an uploaded document has been modified or outdated, or if a rule was entered incorrectly, the system must detect discrepancies between database rules and the source document text.

## Decision
Inspired by the **Self-RAG (Self-Reflective Retrieval-Augmented Generation)** methodology, we introduced a dedicated **Verification Agent Node** (`app.agents.verification_node.verification_node`):
1. **Inputs to the Auditor:**
   - The candidate scheme ID.
   - The deterministic calculation result from the Rule Engine (list of satisfied, not-satisfied, and unknown rules).
   - The raw retrieved document chunks for that specific scheme, including `page_number` and `section` metadata.
2. **Verification Protocol:**
   - The agent is prompted strictly as an auditor: it is prohibited from using outside parametric knowledge.
   - For every condition evaluated by the rule engine, the auditor classifies the claim into one of three statuses:
     - `VERIFIED`: Directly corroborated by the document text.
     - `CONTRADICTED`: The document text conflicts with the claimed condition.
     - `UNSUPPORTED`: The document text does not mention this condition.
   - It extracts verbatim quotations and source references (`evidence_citation` with page numbers).
3. **Structured Schema Output:**
   ```json
   {
     "summary": "Eligible for Post Matric Scholarship. Annual family income requirement verified from page 2.",
     "claims": [
       {
         "claim": "Family income must be below 2.5 Lakhs",
         "status": "VERIFIED",
         "evidence_citation": "Scholarships will be paid to students whose parents/guardians' income from all sources does not exceed Rs. 2,50,000/- per annum (Page 1)",
         "reasoning": "The applicant's income of 1.5 Lakhs satisfies the 2.5 Lakh limit stipulated in paragraph 3."
       }
     ]
   }
   ```

## Consequences

### Positive
- **Auditable Proof:** Citizens receive authoritative quotes and page numbers they can present to administrative offices.
- **Anomaly Detection:** Catches discrepancies where a database rule does not match the uploaded gazette text.
- **User Trust:** Replaces blind assertions with transparent, cited evidence.

### Negative / Trade-offs
- Adds an additional LLM inference call per matched scheme, contributing roughly 1.0 to 1.5 seconds to total pipeline execution time.
