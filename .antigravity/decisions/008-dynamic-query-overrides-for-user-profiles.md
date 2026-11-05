# ADR 008: Dynamic Non-Destructive Query Profile Overrides

## Status
**Accepted**

## Context
When citizens use welfare advisory platforms, their questions frequently involve "what-if" scenarios, family queries, or newly changed circumstances:
- *"I am checking on behalf of my 65-year-old mother whose income is 80k."*
- *"What if I become an unemployed student next month?"*
- *"I recently moved to Maharashtra; do I qualify for state pensions here?"*

In conventional profile-based architectures:
- Either the system blindly uses the logged-in user's static database profile (producing incorrect results for the user's intended query),
- Or the user must navigate to a profile settings page and permanently overwrite their real demographics before running each query.

## Decision
We implemented a **Dynamic Query Override Layer** (`_apply_query_overrides` in `app.api.api_v1.endpoints.analyze`):
1. **Cloning Profile State:**
   - The user's persisted `UserProfile` is read from the database.
   - A shallow copy is wrapped into an in-memory `types.SimpleNamespace`.
2. **Deterministic Regex Extraction:**
   - Before handing the state to LangGraph, high-confidence regex extractors parse the incoming query for:
     - Income phrases (`"1.5 lakhs"`, `"50k"`, `"earning 200000"`) $\rightarrow$ parsed into standard float rupees.
     - Age phrases (`"55 yr old"`, `"age 25"`) $\rightarrow$ translated into temporary `date_of_birth`.
     - State names (e.g., `"Telangana"`, `"Maharashtra"`, `"Tamil Nadu"`).
     - Caste/category keywords (`"SC"`, `"ST"`, `"OBC"`, `"Minority"`, `"General"`).
     - Gender and employment statuses (`"female"`, `"student"`, `"unemployed"`).
3. **Transient Application:**
   - Matched entities dynamically override the `SimpleNamespace` fields for that specific analysis execution only.
   - An `overrides` dictionary is tracked and returned in the API response payload so the frontend can notify the user:
     *"Evaluating with query overrides: Age = 55, State = Maharashtra"*.
   - The user's underlying database record in `user_profiles` remains untouched.

## Consequences

### Positive
- **Fluid User Experience:** Citizens can freely explore eligibility for relatives or hypothetical scenarios without destroying their saved profile.
- **Explainability:** The frontend explicitly highlights when a query term overrode a saved profile attribute.
- **Safety:** Prevents accidental data corruption or unwanted persistence of temporary search variables.

### Negative / Trade-offs
- Natural language phrasing edge cases (e.g. complex comparative phrases) may require continuous refinement of the regex extraction patterns.
