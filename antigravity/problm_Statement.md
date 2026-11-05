# 🏛️ Problem Statement: Agentic RAG Government Scheme Analyzer

## 1. Executive Summary
Welfare governance in India encompasses thousands of Central, State, and District-level schemes designed to support low-income families, farmers, students, entrepreneurs, women, senior citizens, and marginalized communities. Despite budget allocations running into trillions of rupees annually, a massive **welfare delivery gap** persists: millions of eligible citizens fail to access benefits to which they are legally entitled, while others apply for schemes for which they are ineligible, overburdening administrative resources.

The **Government Scheme Analyzer** addresses this challenge through an intelligent, multi-agent Retrieval-Augmented Generation (RAG) system that transforms complex bureaucratic eligibility criteria and voluminous official guidelines into instant, personalized, deterministic, and verifiable eligibility assessments.

---

## 2. Background and Context

Governments release policies and welfare initiatives through official gazette notifications, operational guidelines, and policy PDF documents. These documents are characterized by:
- **High Volume & Fragmented Jurisdiction:** Over 3,000 active schemes distributed across Central ministries and 28 States / 8 Union Territories.
- **Complex, Multi-Variable Eligibility Rules:** Strict thresholds involving income ceilings, age brackets, caste/category reservations (SC, ST, OBC, General), landholding limits, educational stages, gender, and disability status.
- **Dynamic Policy Updates:** Eligibility thresholds, subsidy amounts, and application deadlines are continuously revised across fiscal years.

Citizens typically interact with this ecosystem through unorganized local agents, overcrowded service kiosks (e.g., MeeSeva, CSCs), or by manually navigating fragmented government portals (e.g., India.gov.in, myScheme).

---

## 3. The Core Problems

### Problem 1: Information Asymmetry and Accessibility Barrier
- **Linguistic & Bureaucratic Complexity:** Official documents are written in legalistic, bureaucratic language that is difficult for ordinary citizens to interpret.
- **Fragmented Discovery:** A citizen does not know which ministry or department governs their specific need (e.g., a handloom weaver looking for financial aid could be under the Ministry of Textiles, MSME, or State Commerce).
- **Static Search Inadequacy:** Keyword searches on traditional portals fail when users search in conversational terms (e.g., *"I am a small farmer with 2 acres in Telangana and need money for seeds"* vs. *"Input Subsidy under Rythu Bharosa"*).

### Problem 2: The LLM Hallucination & Determinism Dilemma in Welfare
Generative AI and Large Language Models (LLMs) excel at natural language comprehension, but fail critically when applied blindly to legal and welfare eligibility:
- **Numerical & Boundary Hallucinations:** LLMs often fail at strict mathematical inequalities (e.g., admitting an applicant with family income ₹2,60,000 into a scheme strictly capped at ₹2,50,000).
- **Confabulation of Benefits:** LLMs may blend provisions from two different schemes or hallucinate non-existent subsidy amounts.
- **High Stakes:** A hallucinated eligibility assessment wastes a citizen's time and money (obtaining affidavits, certificates) and erodes trust in public services.

### Problem 3: Lack of Source Citations and Auditability
- Traditional chatbots provide answers as flat text without proving where the rules come from.
- Citizens and case-workers require **verifiable proof**—citing the exact official scheme guideline, paragraph, and page number—so they can contest rejections or proceed with application filings with confidence.

### Problem 4: The Black-Box AI User Experience
- Standard AI interfaces present a spinner followed by an opaque answer.
- Citizens cannot see whether the AI understood their demographic details, which rules were applied, or which documents were inspected.
- Transparency is essential to build citizen trust in AI-driven public services.

---

## 4. Proposed Solution: Hybrid Agentic RAG Architecture

The project solves these problems through a **dual-engine hybrid architecture** orchestrated by **LangGraph** and powered by **Google Gemini 2.5 Flash** and **FAISS**:

1. **Separation of Soft and Hard Logic (Inspired by KGLens Research):**
   - **Soft Knowledge (Semantic Discovery):** High-dimensional vector search using Google's `text-embedding-004` and FAISS retrieves semantically relevant schemes from messy natural language queries.
   - **Hard Knowledge (Deterministic Evaluation):** A mathematical Python Rule Engine evaluates candidate schemes against structured database constraints (`>=`, `<=`, `==`, `IN`) stored in SQLite/PostgreSQL, completely bypassing LLM hallucination for critical thresholds.

2. **Self-Reflective Verification Agent (Inspired by Self-RAG Research):**
   - An independent auditor agent examines the output of the rule engine against the raw text chunks of official scheme guidelines.
   - Flags each condition as `VERIFIED`, `CONTRADICTED`, or `UNSUPPORTED` and generates verbatim document citations with page numbers.

3. **Real-Time Agentic Observability (SSE):**
   - A Server-Sent Events (SSE) streaming architecture displays the multi-agent reasoning steps in real-time on the frontend:
     $$\text{Intent Parser} \longrightarrow \text{Hybrid Retriever} \longrightarrow \text{Rule Engine} \longrightarrow \text{Document Verifier}$$

4. **Dynamic Profile Overrides:**
   - Enables citizens to query hypotheticals (e.g., *"What if my income drops to 1.5 Lakhs?"*) without altering their permanent profile, enabling proactive life-planning.

---

## 5. Target Stakeholders & Personas

| Stakeholder Persona | Key Needs | System Value Delivered |
| :--- | :--- | :--- |
| **Citizen / Beneficiary** (Students, Farmers, Daily Wage Earners) | Plain-language discovery, zero technical jargon, clear eligibility verdict, actionable guidance. | Natural language search, instant check against personal profile, step-by-step transparency. |
| **Common Service Center (CSC) / Village Kiosk Operator** | Fast scheme lookup for visiting villagers with varying demographics. | Ability to enter ad-hoc queries, test dynamic demographic overrides, print cited eligibility proof. |
| **Scheme Administrator / Government Officer** | Ingest new policy circulars, define strict criteria, audit AI verification. | Dedicated Admin portal to upload PDF guidelines, define mathematical rules, and monitor document chunking. |

---

## 6. Success Metrics & Key Performance Indicators (KPIs)

- **Eligibility Precision (Zero Hallucination):** 100% deterministic mathematical accuracy on modeled eligibility rules (income ceilings, age limits, caste restrictions).
- **Retrieval Relevance (Top-K Recall):** $\ge 90\%$ recall of relevant schemes in the top 5 vector matches for demographic-laden queries.
- **Verification Citation Fidelity:** 100% of claims verified against retrieved official text with identifiable page/section sources.
- **Latency & Streaming UX:** Time-to-first-event $< 500\text{ms}$ via SSE; full multi-agent pipeline resolution within $< 4.0\text{s}$.
- **Extensibility:** Capacity to support arbitrary scheme rules via structured JSON condition schemas without code refactoring.
