# Architecture Document
## Digital Guardrails — System Architecture

**Track:** Bal Suraksha (Track 2)
**Version:** 1.0

---

## 1. Architecture Overview

Digital Guardrails follows a **modular, layered architecture** with a clear separation between the frontend (parent dashboard), backend API layer, ML inference engine, and data storage. The design is intentionally simple for a 48-hour build but structured so each layer could scale independently in a real deployment.

```
                        ┌─────────────────────────┐
                        │   React + Tailwind UI    │
                        │   (Parent Dashboard)     │
                        └────────────┬─────────────┘
                                     │ REST / WebSocket
                                     ▼
                        ┌─────────────────────────┐
                        │      FastAPI Backend     │
                        │  (Auth, API, Orchestration)│
                        └───────┬─────────┬────────┘
                                │         │
                 ┌──────────────┘         └───────────────┐
                 ▼                                         ▼
      ┌────────────────────┐                  ┌───────────────────────┐
      │  ML Inference Layer │                  │  Database (SQLite /   │
      │  (MuRIL / IndicBERT │                  │  PostgreSQL via       │
      │  pattern classifier)│                  │  SQLAlchemy/SQLModel) │
      └────────────────────┘                  └───────────────────────┘
```

---

## 2. Component Breakdown

### 2.1 Frontend — React.js + Tailwind CSS
**Responsibilities:**
- Parent/guardian login and dashboard.
- Display list of flagged conversations with risk level badges (Low/Medium/High).
- Alert detail view showing flagged pattern type and minimal context (not full chat).
- (Optional) Live-updating alert feed via WebSocket.

**Key Libraries:**
- React (Vite) — app shell and routing
- Tailwind CSS — styling
- React Router — navigation between Dashboard / Alert Detail / Settings
- Axios — API communication
- Recharts / Chart.js — risk trend visualizations
- Socket.io-client (optional) — real-time alert push

---

### 2.2 Backend — FastAPI (Python)
**Responsibilities:**
- Expose REST endpoints for: message ingestion, alert retrieval, dashboard data, authentication.
- Orchestrate calls to the ML inference layer.
- Persist conversations, risk scores, and alerts to the database.
- (Optional) Push real-time alerts via WebSocket.

**Key Libraries:**
- FastAPI — API framework
- Uvicorn — ASGI server
- Pydantic — data validation/schemas
- SQLAlchemy or SQLModel — ORM (keeps SQLite ↔ PostgreSQL portable)
- python-jose / passlib — JWT auth & password hashing (if login implemented)
- python-socketio or FastAPI native WebSockets — real-time push (optional)

**Core API Endpoints (example):**
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/messages/ingest` | Submit a message/conversation window for analysis |
| GET | `/api/alerts` | Retrieve list of flagged alerts |
| GET | `/api/alerts/{id}` | Retrieve details of a specific alert |
| POST | `/api/auth/login` | Parent/guardian login |
| GET | `/api/dashboard/summary` | Aggregated stats for dashboard (counts, trends) |

---

### 2.3 ML Inference Layer
**Responsibilities:**
- Classify incoming text/conversation windows for grooming or bullying risk patterns.
- Support multilingual and code-mixed input (Hindi, English, one regional language minimum).
- Return a structured result: risk score + pattern label (e.g., "trust-building", "isolation request", "coercive language", "harassment").

**Approach:**
- Primary model: **MuRIL** or **IndicBERT** (pretrained on Indian languages), fine-tuned or used with few-shot/zero-shot classification for pattern detection.
- Fallback/baseline: **scikit-learn** classifier (e.g., logistic regression / SVM on TF-IDF or embeddings) if transformer fine-tuning is too time-costly within 48 hours.
- Inference exposed as an internal Python function/module called directly by FastAPI (same process) for hackathon simplicity — avoids extra network hop of a separate microservice.

**Data flow for a single message/conversation window:**
1. Text received by backend → preprocessed (cleaning, language detection).
2. Passed to ML module → returns risk score (0–1) and pattern label(s).
3. If risk score exceeds threshold → alert record created in DB.
4. Dashboard queries/receives the new alert.

---

### 2.4 Database Layer — SQLite (dev) / PostgreSQL (production-ready path)
**Responsibilities:**
- Store conversation metadata, flagged snippets (not full raw logs), risk scores, and alert history.
- Store user accounts (parents/guardians) if auth is implemented.

**Design Choice:**
- Use **SQLAlchemy** or **SQLModel** as the ORM layer so the exact same models/queries work against SQLite locally and PostgreSQL in a scaled deployment — only the connection string changes.
- SQLite (`digital_guardrails.db`) used for the hackathon demo: zero external setup, file-based, fast to iterate.

**Simplified Schema:**

```
users
├── id (PK)
├── name
├── email
├── hashed_password
└── created_at

conversations
├── id (PK)
├── user_id (FK -> users.id)   -- guardian/account owner
├── child_label               -- e.g., "Child 1" (no PII required)
├── source_platform           -- e.g., demo/simulated
└── created_at

alerts
├── id (PK)
├── conversation_id (FK -> conversations.id)
├── risk_score
├── risk_level                -- Low / Medium / High
├── pattern_type               -- e.g., grooming:isolation-request, bullying:harassment
├── flagged_snippet            -- minimal context, not full chat
└── created_at
```

---

## 3. Real-Time vs Batch Processing (Design Decision)
Two approaches were considered:

| Approach | Description | Hackathon Fit |
|---|---|---|
| **Real-time inference** | Messages analyzed as they are typed/sent via WebSocket | Higher complexity, needs low-latency inference and persistent connections |
| **Batch/simulated ingestion** | Messages or chat logs submitted (manually or via upload) and analyzed on submission | Simpler, realistic to fully complete and demo within 48 hours |

**Decision for hackathon MVP:** Batch/simulated ingestion via a demo input form or sample dataset upload, with the architecture designed so a WebSocket-based real-time layer could be added later without major rework (the ML inference and alerting logic remain identical — only the trigger mechanism changes).

---

## 4. Deployment Architecture

```
Frontend (React/Tailwind)  --->  Vercel / Netlify
Backend (FastAPI)          --->  Render / Railway
Database (SQLite file)     --->  Bundled with backend service (demo)
                                  (swap to managed PostgreSQL for production)
```

- Frontend and backend are deployed as separate services and communicate over HTTPS REST (and optionally WebSocket).
- Environment variables manage API base URLs, secrets, and DB connection strings — never committed to the repository.

---

## 5. Security & Privacy by Design
- No plaintext secrets/API keys committed to the public GitHub repo (per hackathon rules).
- Only flagged snippets — not full conversation logs — are persisted, minimizing sensitive data at rest.
- Passwords hashed (e.g., via `passlib`) if authentication is implemented.
- Clear separation between raw ingested text (processed transiently) and stored alert data (minimal, purposeful).

---

## 6. Scalability Path (Post-Hackathon)
1. Move ML inference to a dedicated microservice (e.g., FastAPI service or serverless function) so it can scale independently of the main API.
2. Migrate from SQLite to managed PostgreSQL.
3. Add a message queue (e.g., Redis/RabbitMQ) between ingestion and inference for high-throughput real-time processing.
4. Integrate with real platform APIs (WhatsApp Business API, gaming chat SDKs) as ingestion sources.
5. Add on-device/edge inference options to further strengthen privacy guarantees.
