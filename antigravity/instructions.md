# 📜 Engineering Standards & Quality Instructions
## Guidelines for Writing High-Quality Code in Government Scheme Analyzer

This document defines the mandatory engineering practices, architecture patterns, coding standards, and testing procedures for the **Agentic RAG Government Scheme Analyzer** project. All contributors and AI coding agents must adhere strictly to these guidelines.

---

## 1. Core Engineering Principles

1. **Zero-Hallucination on Critical Business Rules:**
   - Never delegate mathematical inequality checks, age calculations, or categorical eligibility evaluations directly to LLM prompts.
   - Always route rule evaluations through the deterministic Python Rule Engine (`app.verification.rule_engine`).
   - Use the LLM only for semantic intent parsing, semantic retrieval ranking, and verifying documentary citations against raw text chunks.

2. **Defense in Depth & Graceful Fallbacks:**
   - Every external call (Google Gemini API, FAISS vector search, PDF parsing) must be wrapped in structured `try...except` blocks with meaningful fallback paths.
   - If FAISS search fails or is uninitialized, the system must transparently fall back to database lexical search (`_retrieve_from_database`).
   - If the LLM Coordinator fails, fall back to raw query keywords rather than crashing the pipeline.

3. **Stateless Workflows & Immutability:**
   - All LangGraph nodes must be pure or deterministic functions taking an `AgentState` dictionary and returning a state update slice.
   - Dynamic query overrides must never mutate the persistent database profile of a user.

4. **Observability First:**
   - Long-running multi-agent pipelines must emit streaming status events (SSE) so users can observe the system's thought process at every transition.

---

## 2. Python & FastAPI Standards

### 2.1 Code Style & Type Annotations
- Adhere strictly to **PEP 8** standards.
- Enforce full type annotations on all function signatures, including arguments and return values:
  ```python
  # Good
  def evaluate_rule(profile: UserProfile, rule: EligibilityRule) -> RuleStatus:
      ...

  # Bad
  def evaluate_rule(profile, rule):
      ...
  ```
- Use `pydantic` schemas for API request validation, response serialization, and internal configuration.

### 2.2 FastAPI Architecture & Dependency Injection
- Organize endpoints logically under `app/api/api_v1/endpoints/`.
- Never instantiate database sessions or global services inside endpoint route handlers. Always inject dependencies via `Depends()`:
  ```python
  @router.get("/profile", response_model=UserProfileOut)
  def get_profile(
      db: Session = Depends(deps.get_db),
      current_user: User = Depends(deps.get_current_active_user)
  ):
      return user_service.get_user_profile(db, current_user.id)
  ```
- Keep controllers thin: business logic belongs in `services/`, deterministic logic in `verification/`, and multi-agent coordination in `agents/`.

### 2.3 Database & SQLAlchemy Best Practices
- Always commit transactions within dedicated service/repository layers, and ensure sessions close cleanly via FastAPI's `yield` dependency pattern.
- Explicitly add database indexes on columns frequently used in filtering: `state`, `department`, `is_active`, and `user_id`.
- Use SQLAlchemy relationships with proper cascade rules and avoid accidental $N+1$ query bottlenecks by using eager loading (`joinedload` or explicit joins) where appropriate.

---

## 3. Multi-Agent & AI Engineering Standards

### 3.1 LangGraph State Management
- All keys in `AgentState` (`app/agents/state.py`) must be explicitly declared with `TypedDict`.
- Nodes must return partial dictionary updates, never mutative side-effects on input state:
  ```python
  # Good: returns new key/value updates
  def coordinator_node(state: AgentState) -> Dict[str, Any]:
      return {"search_keywords": parsed_keywords, "state_filter": parsed_state}

  # Bad: mutating incoming state object
  def coordinator_node(state: AgentState):
      state["search_keywords"] = parsed_keywords
      return state
  ```

### 3.2 Google GenAI SDK Usage
- Always use the official `google-genai` SDK (`from google import genai` and `from google.genai import types`).
- For nodes requiring structured data (e.g., Coordinator and Verification nodes), always specify `response_mime_type="application/json"`:
  ```python
  response = client.models.generate_content(
      model='gemini-2.5-flash',
      contents=prompt_content,
      config=types.GenerateContentConfig(
          response_mime_type="application/json",
          temperature=0.1,  # Low temperature for factual consistency
      ),
  )
  ```
- Always sanitize and wrap `json.loads(response.text)` in a fallback handler to guard against malformed JSON or API rate limits.

### 3.3 Prompt Engineering Standards
- System prompts must specify an exact, unambiguous persona and required output schema.
- Verification prompts must explicitly restrict the LLM to the provided context chunks:
  > *"For each claim, determine if it is VERIFIED, CONTRADICTED, or UNSUPPORTED based **only** on the provided document text."*
- Prohibit the LLM from hallucinating page numbers or inventing outside clauses.

---

## 4. Vector Store & RAG Quality Guidelines

### 4.1 Chunking & Metadata Preservation
- Chunks must preserve source context: `document_id`, `scheme_id`, `page_number`, and `section`.
- Optimal chunk size: 500 to 1000 characters with 100 characters overlap to prevent boundary truncation of vital clauses.
- Store chunk text cleanly in SQLite/PostgreSQL, ensuring vectors in FAISS map 1-to-1 with database chunk IDs.

### 4.2 FAISS Vector Storage Hygiene
- Always apply $L_2$ vector normalization (`faiss.normalize_L2(vectors)`) before adding to or searching in `IndexFlatIP`.
- Ensure the dimensionality of incoming vectors matches the index dimension (768 for `text-embedding-004`).
- Guard vector search calls with checks against `self.index.ntotal == 0`.
- Maintain synchronization between `faiss_index.bin` and `faiss_meta.pkl`.

---

## 5. Frontend & React Standards (TypeScript & Tailwind)

### 5.1 TypeScript Discipline
- Set `"strict": true` in `tsconfig.json`.
- Prohibit the use of `any` where domain interfaces can be declared.
- Share API payload definitions between frontend and backend contracts:
  ```typescript
  export interface SchemeVerification {
    summary: string;
    claims: Array<{
      claim: string;
      status: 'VERIFIED' | 'CONTRADICTED' | 'UNSUPPORTED';
      evidence_citation: string;
      reasoning: string;
    }>;
  }
  ```

### 5.2 Server-Sent Events (SSE) Client Handling
- Always attach an `AbortController` to streaming fetch requests.
- Ensure event streams are closed when components unmount to prevent memory leaks and zombie network connections:
  ```typescript
  useEffect(() => {
    const controller = new AbortController();
    return () => controller.abort();
  }, []);
  ```
- Gracefully handle stream interruptions and render distinct UI error banners.

### 5.3 UI/UX & Tailwind CSS Standards
- Maintain high accessibility and contrast ratios for public welfare tools.
- Visual status indicators must follow established color semantics:
  - `LIKELY ELIGIBLE`: Green badges (`bg-emerald-100 text-emerald-800 border-emerald-300`).
  - `POSSIBLY ELIGIBLE`: Amber badges (`bg-amber-100 text-amber-800 border-amber-300`).
  - `NOT ELIGIBLE`: Red badges (`bg-rose-100 text-rose-800 border-rose-300`).
  - `INSUFFICIENT INFORMATION`: Slate badges (`bg-slate-100 text-slate-800 border-slate-300`).
- Ensure all views are responsive across mobile screens (320px+).

---

## 6. Security & Data Protection Guidelines

1. **Authentication & Secret Management:**
   - Never commit `.env` files or API keys (`GEMINI_API_KEY`, `SECRET_KEY`) to Git.
   - Use cryptographically strong random keys for JWT signing in production.
   - Passwords must be hashed using `bcrypt` with salt rounds $\ge 12$.

2. **Protection of Citizen PII:**
   - Demographics (income, disability status, caste) represent sensitive citizen data.
   - Strip PII from debug log statements. Never log full raw user profiles into server console logs.

3. **CORS & Input Sanitization:**
   - In production, replace `allow_origins=["*"]` with specific trusted frontend origin URLs.
   - Validate and sanitize all string inputs in search queries and admin forms against SQL injection and script execution.

---

## 7. Testing & Quality Assurance

### 7.1 Backend Unit & Integration Tests
- Run backend tests using `pytest`:
  ```bash
  cd backend
  pytest tests/
  ```
- **Rule Engine Unit Tests:** Must thoroughly verify boundary edge conditions:
  - Income exactly at cutoff ($== 250000$).
  - Income ₹1 above cutoff ($> 250000$).
  - Age calculation on leap years and exact birth dates.
  - Multi-value category membership (`category IN ['SC', 'ST']`).
- **Mocking External APIs:** Never call live Google Gemini APIs during automated unit test runs. Mock `genai.Client` responses using `unittest.mock`.

### 7.2 Manual Smoke Testing Checklist
Before committing major changes, verify:
- [ ] `seed_real.py` executes without error and seeds 30 schemes with FAISS vectors.
- [ ] `/health` endpoint returns `{"status": "ok"}`.
- [ ] Streaming endpoint `/api/v1/analyze/stream` emits all 4 steps and terminates with a `result` payload.
- [ ] Frontend successfully renders step-by-step progress and cited verification cards.
- [ ] Dynamic query overrides parse rupees and ages accurately.

---

## 8. Git Commit & Documentation Standards

- Write clear, conventional commit messages:
  - `feat: add hybrid fallback for empty vector index`
  - `fix: resolve date of birth edge case in rule engine`
  - `docs: add ADR for Server-Sent Events architecture`
  - `test: add unit tests for dynamic query override regex`
- When modifying architectural components, update the corresponding ADR in `antigravity/decisions/` and keep `requirements.md` in sync.
- Preserve existing comments and docstrings across files unless directly refactoring that functionality.
