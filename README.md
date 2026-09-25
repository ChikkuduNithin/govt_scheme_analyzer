# 🏛️ Agentic RAG Government Scheme Analyzer

An advanced, multi-agent AI system designed to intelligently match citizens with government schemes. This project utilizes a sophisticated Agentic Retrieval-Augmented Generation (RAG) architecture powered by Google's Gemini models and LangGraph to perform deep intent parsing, deterministic rule evaluation, and hallucination-free document verification.

## 🚀 Tech Stack

### 🧠 AI & Orchestration
* **Google Gemini 2.5 Flash:** The core reasoning engine used for intent parsing and final document verification.
* **Google `text-embedding-004`:** Used to generate high-dimensional mathematical vectors for official scheme documents.
* **LangGraph:** Orchestrates the multi-agent workflow, handling state routing between the Intent Parser, Retriever, Rule Engine, and Verifier nodes.
* **Google GenAI SDK:** The latest official Python client for interacting with Gemini APIs.

### ⚙️ Backend
* **Python 3.9+**
* **FastAPI:** High-performance async API framework handling the streaming endpoints and background tasks.
* **SQLAlchemy:** ORM for managing relational data (Users, Schemes, strict mathematical Eligibility Rules).
* **SQLite:** Local relational database.
* **FAISS (Facebook AI Similarity Search):** Lightning-fast local vector database for storing and querying scheme embeddings without relying on complex PostgreSQL vector extensions.

### 🖥️ Frontend
* **React 18** (Vite)
* **Tailwind CSS v4:** Utility-first CSS framework for a responsive, modern UI.
* **Server-Sent Events (SSE):** Real-time streaming API to provide agentic observability (showing the user what the AI is thinking, step-by-step).

---

## 🏗️ Architecture & End-to-End Workflow

The system is split into two primary phases:

### 1. Ingestion & Indexing Pipeline (Admin Phase)
1. Administrators upload official government scheme guidelines (PDFs) and define strict mathematical eligibility rules (e.g., `age <= 25`, `income < 250000`).
2. The system splits the document into semantic chunks.
3. Chunks are passed through Gemini `text-embedding-004` to generate vectors.
4. Vectors are indexed into FAISS for sub-millisecond similarity search.

### 2. Multi-Agent Analysis Pipeline (User Phase)
1. **Agent 1: Intent Coordinator:** Parses messy natural language queries (e.g., *"I'm a 55 yr old farmer making 1L a year"*) into structured demographic profiles and optimized search keywords.
2. **Agent 2: Hybrid Retriever:** Uses the keywords to perform a vector similarity search in FAISS, heavily filtered by SQL relational constraints (like state/department).
3. **Agent 3: Deterministic Rule Engine:** Bypasses LLM hallucinations by running hard Python logic. Checks the extracted user profile against the strict rules stored in SQLite, deterministically flagging schemes as `LIKELY ELIGIBLE` or `NOT ELIGIBLE`.
4. **Agent 4: Verification Agent:** Acts as an auditor. Takes the Rule Engine's decision and cross-references it against the raw retrieved PDF text to guarantee accuracy and provide specific page citations.

---

## 📚 Related Research & Whitepapers

This architecture is heavily inspired by cutting-edge research in Agentic Workflows and RAG patterns:

1. **Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (Lewis et al., 2020)**
   * *Relevance:* The foundational paper for RAG, which this project builds upon by using FAISS to retrieve relevant government guidelines before generating a response.
   * [Read Paper](https://arxiv.org/abs/2005.11401)

2. **ReAct: Synergizing Reasoning and Acting in Language Models (Yao et al., 2022)**
   * *Relevance:* The inspiration behind the LangGraph agent orchestration, allowing the system to "think" (parse intent), "act" (query FAISS/SQLite), and "observe" (verify against rules).
   * [Read Paper](https://arxiv.org/abs/2210.03629)

3. **Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection (Asai et al., 2023)**
   * *Relevance:* Our "Verification Agent" node directly implements the critique phase proposed in Self-RAG. It forces the LLM to double-check the deterministic rule engine's output against the source text to prevent hallucinations.
   * [Read Paper](https://arxiv.org/abs/2310.11511)

4. **KGLens: A Parameterized Knowledge Graph Solution to Assess What an LLM Does and Doesn't Know**
   * *Relevance:* Influenced our decision to split "soft" knowledge (document embeddings in FAISS) from "hard" rules (deterministic eligibility constraints in SQLite) to ensure zero-shot accuracy for critical metrics like income cutoffs.

---

## 🛠️ Setup & Installation

### 1. Environment Setup
Create a `.env` file in the `backend` directory:
```env
GEMINI_API_KEY="your_google_ai_studio_key"
SECRET_KEY="supersecretkey-change-in-production"
```

### 2. Run the Backend
```bash
cd backend
pip install -r requirements.txt
python seed_real.py # Seeds the SQLite DB and generates FAISS vectors
python -m uvicorn app.main:app --reload
```

### 3. Run the Frontend
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` to access the dashboard! (Test credentials: `test@example.com` / `password123`)
