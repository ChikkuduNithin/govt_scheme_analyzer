# ADR 010: React 18, Vite, and Tailwind CSS v4 Frontend Architecture

## Status
**Accepted**

## Context
The user interface for the Government Scheme Analyzer must:
1. Deliver a responsive, mobile-accessible experience suitable for citizens, kiosk operators, and administrators across India.
2. Render real-time multi-agent thinking progress (displaying step-by-step progress checklist for Coordinator, Retriever, Rule Engine, and Verifier).
3. Present complex eligibility verdicts (satisfied rules, failed rules, verbatim legal citations) in an intuitive, accessible visual hierarchy.
4. Support rapid build cycles and minimal bundle sizes for low-bandwidth cellular environments.

Options evaluated:
- **Next.js / SSR:** Adds Node server complexity when the backend is already Python/FastAPI.
- **Traditional Create React App (CRA):** Deprecated, slow webpack builds, bloated bundles.
- **Vite + React 18 (SPA) + Tailwind CSS v4 + TypeScript:** Ultra-fast HMR, tiny production bundles, utility-first modern styling, and direct client-side SSE handling.

## Decision
We selected **React 18** bootstrapped with **Vite**, written in **TypeScript**, and styled using **Tailwind CSS v4**:
1. **Real-time Event Streaming:**
   - The `Analyze.tsx` page manages an `AbortController` and streams `/api/v1/analyze/stream` chunks directly into React state.
   - Interactive progress indicators dynamically light up as events arrive (`coordinator` $\rightarrow$ `retriever` $\rightarrow$ `eligibility_engine` $\rightarrow$ `verification`).
2. **Component Separation:**
   - `pages/Analyze.tsx`: Citizen conversational analysis interface with real-time SSE progress tracker and card-based results.
   - `pages/Dashboard.tsx`: Scheme discovery catalog with category/state filters.
   - `pages/Admin.tsx`: Scheme creation, rule builder, and document ingestion portal.
   - `context/AuthContext.tsx`: Client-side JWT management with automatic token persistence in `localStorage`.
3. **Tailwind CSS v4 Utility Styling:**
   - Provides accessible contrast ratios, clean typography, badge indicators for eligibility (`LIKELY ELIGIBLE` in green, `NOT ELIGIBLE` in red, `POSSIBLY ELIGIBLE` in amber), and responsive flex/grid layouts.

## Consequences

### Positive
- **Instant Hot Module Replacement (HMR):** Sub-second dev reload times with Vite.
- **Low Footprint:** Small client bundle size enables fast loading on 3G/4G connections.
- **Type Safety:** TypeScript interfaces enforce contract consistency between FastAPI backend schemas and frontend state.

### Negative / Trade-offs
- Single-page application (SPA) architecture requires client-side JavaScript execution; initial SEO indexing of client-rendered pages is less optimal than SSR, though the primary platform is an authenticated citizen portal.
