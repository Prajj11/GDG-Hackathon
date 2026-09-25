# Digital Guardrails + Support Ecosystems (Bal Suraksha)

[![Live Demo](https://img.shields.io/badge/Live%20Demo-digital--guardrails.antideploy.com-4F46E5?style=for-the-badge&logo=google-chrome&logoColor=white)](https://digital-guardrails.antideploy.com)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/Frontend-React%2019%20%2B%20Vite-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![AI4Bharat IndicBERT](https://img.shields.io/badge/Model-AI4Bharat%20IndicBERTv2-FF6F00?style=for-the-badge&logo=huggingface&logoColor=white)](https://huggingface.co/ai4bharat/IndicBERTv2-MLM-only)
[![Tailwind CSS v4](https://img.shields.io/badge/Styling-Tailwind%20CSS%20v4-38BDF8?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)

> **Privacy-first, multilingual child online safety & safeguarding support ecosystem for Indian languages.**  
> Powered by fine-tuned **AI4Bharat IndicBERTv2** representations, privacy-preserving behavioral sequence escalation, an independent anonymous youth support portal, and district Child Welfare Committee (CWC) triage workspaces.

---

## 🌐 Live Deployment

The full-stack application (React frontend, FastAPI backend, and pre-trained IndicBERTv2 inference engine) is live and ready to test:

🔗 **[https://digital-guardrails.antideploy.com](https://digital-guardrails.antideploy.com)**

* **Interactive Sandbox & Demo**: [https://digital-guardrails.antideploy.com/demo](https://digital-guardrails.antideploy.com/demo)
* **Anonymous Youth Support Portal**: [https://digital-guardrails.antideploy.com/help](https://digital-guardrails.antideploy.com/help)
* **Secure Portal Login**: [https://digital-guardrails.antideploy.com/login](https://digital-guardrails.antideploy.com/login)
* **Interactive API Documentation**: [https://digital-guardrails.antideploy.com/docs](https://digital-guardrails.antideploy.com/docs) *(available on API host)*

---

## 🔑 Demo & Evaluation Credentials

You can sign in using any of the pre-configured role-based accounts below to inspect the dedicated guardian and caseworker workflows:

| Role | Username | Password | Opens | Description & District |
|:---|:---|:---|:---|:---|
| **Parent / Guardian** | `guardian` | `demo123` | **Guardian dashboard** (`/`) | Family safety overview, alerts feed, minimal snippet inspection, risk trends, and retention settings. |
| **Caseworker / NGO** | `cwc_southdelhi` | `demo123` | **Caseworker workspace** (`/physical-link`) | South Delhi Child Welfare Committee triage, risk review, case status tracking, and notes. |
| **Caseworker / NGO** | `mumbai_cwc` | `demo123` | **Mumbai caseworker workspace** (`/physical-link`) | Mumbai Suburban Child Protection Unit queue and youth report dispatch management. |
| **Caseworker / NGO** | `bengaluru_cwc` | `demo123` | **Bengaluru caseworker workspace** (`/physical-link`) | Bengaluru Urban Child Welfare Committee queue with district incident coordination. |

> [!TIP]
> **No Login Required for Youth Reporting:** Young people can visit [`/help`](https://digital-guardrails.antideploy.com/help) directly from any device. The youth portal operates independently of guardian accounts, requests **zero** personally identifiable information (PII), generates a client-side recovery secret, and provides immediate emergency contacts (**1098 Childline** and **112**).

---

## 💡 The Core Problem & Solution

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           THE CHALLENGE IN INDIA                             │
│  • Rapid digital adoption among minors across vernacular & code-mixed text   │
│  • Predatory grooming follows subtle behavioral arcs: Trust → Isolation →    |
│  Coercion │                                                                  |
│  • Intrusive spyware surveillance destroys parent-child trust                │
│  • Isolated children have no safe, stigma-free bridge to seek guidance       │
└──────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    DIGITAL GUARDRAILS (BAL SURAKSHA)                         │
│                                                                              │
│  1. Privacy-First Detection (AI4Bharat IndicBERTv2)                          │
│     • Multilingual detection (Hindi, Hinglish, Malayalam, Manglish, English) │
│     • Evaluates message intent with 50.89% neutral class calibration         │
│     • Temporal sequence escalation: flags subtle grooming progressions       │
│                                                                              │
│  2. Minimal-Context Guardian Alerts                                          │
│     • NEVER stores or displays full raw chat histories                       │
│     • Displays only bounded snippets (≤140 chars) with regex PII redaction   │
│     • Actionable conversation starters & positive reinforcement tips         │
│                                                                              │
│  3. Anonymous Youth Support Ecosystem                                        │
│     • Child-led, zero-login, self-selected urgency reporting                 │
│     • Zero cross-contamination with guardian surveillance credentials        │
│     • Cryptographic secret receipts & verified emergency helpline links      │
│                                                                              │
│  4. Caseworker / CWC Physical-Digital Link                                   │
│     • Localized incident queues for Child Welfare Committees & NGOs          │
│     • Non-punitive triage, audit trails, and simulated aid dispatch          │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Key Feature Workspaces

### 1. 🛡️ Guardian Dashboard (`/`)
* **Minimal-Context Safety Alerts**: Instead of spying on entire chats, parents receive concise alerts containing only the highest-risk snippet, category explanation, and risk score.
* **Supportive Guidance**: Each alert includes context-aware talking points to help parents open a calm, supportive dialog without alarming the child.
* **Aggregated Trends & Insights (`/trends`)**: Weekly severity histograms, pattern breakdowns (Grooming vs. Cyberbullying), and activity timelines without exposing private interactions.
* **Strict Retention Controls (`/settings`)**: Configurable data retention windows (1, 7, or 30 days) with automatic cryptographic scrub on expiry.

### 2. 🤝 Independent Youth Support Portal (`/help`)
* **Zero-PII Anonymous Reporting**: Young people can report distress without revealing their name, phone number, school, or account login.
* **Child-Led Urgency**: The child chooses whether their situation feels Low, Medium, or Immediate.
* **Client-Side Secret Receipts**: Generates a 256-bit SHA-256 private receipt code so the child can return to track case status without creating an account.
* **Direct Emergency Lifelines**: Instant, one-tap access to [National Emergency (112)](https://112.gov.in/) and [Child Helpline (1098)](https://www.spniwcd.wcd.gov.in/child-helpline).

### 3. 🏢 Caseworker & NGO Workspace (`/physical-link`)
* **Multi-District Queue Management**: Dedicated workspaces for South Delhi, Mumbai Suburban, and Bengaluru Urban Child Welfare Committees.
* **Triage & Incident Management**: Caseworkers can review anonymized incident descriptions, update case statuses (`under_review`, `assigned`, `action_taken`), and append verified case notes.
* **Simulated Aid Dispatch**: Testable routing protocol demonstrating how reports can be safely handed off to institutional emergency partners.

### 4. 🧪 Interactive Demo Sandbox (`/demo`)
* **Pre-Loaded Test Scenarios**: One-click testing across all 5 supported languages and dialects (English, Hindi, Hinglish, Malayalam, Manglish).
* **Multi-Turn Grooming Arc Simulation**:
  1. *Step 1*: Submit a **Trust-Building** message (*"You are so mature for your age..."*) $\rightarrow$ Model flags Medium risk (43/100).
  2. *Step 2*: Submit an **Isolation Request** (*"Don't tell your mom about our chats..."*) $\rightarrow$ Temporal escalation elevates risk to **High (80/100)**.
* **Capability Handoff**: Demonstrates how a flagged safety signal can generate a signed, 30-minute capability token enabling a young person to launch support without passing chat text.

---

## 🤖 AI/ML Detection Engine & Dataset

The core machine learning engine is built upon **[AI4Bharat/IndicBERTv2-MLM-only](https://huggingface.co/ai4bharat/IndicBERTv2-MLM-only)**, an Indian foundation model specifically pre-trained on diverse Indic language corpora.

### Detection Taxonomy
1. `neutral` — Everyday teen conversation, school banter, sports, and benign questions.
2. `grooming-trust-building` — Excessive flattery, gift promises, and establishing special emotional dependency.
3. `grooming-isolation-request` — Encouraging secrecy, deleting chat logs, and isolating the child from parents/friends.
4. `grooming-coercive-language` — Threats of leaking private pictures/messages, ultimatums, and psychological blackmail.
5. `bullying-harassment` — Targeted insults, derogatory slurs, humiliation, and repeated harassment.

### Dataset Composition (790 Balanced Conversations)
To eliminate false alarms that cause parental notification fatigue, the training corpus is calibrated to **50.89% neutral content**:
* **340 Real-World Research Samples**: Ethically sourced from peer-reviewed academic datasets:
  * **HASOC 2020** (Hindi Devanagari hate speech & offensive content)
  * **BullyExplain** (Hinglish cyberbullying comments with human-annotated rationales)
  * **DravidianLangTech** (Malayalam and Manglish YouTube comment benchmarks)
  * **COMI-LINGUA** (Clean code-mixed conversational baseline dialogue)
* **450 Grounded Synthetic Grooming Arcs**: Multi-turn dialogue progressions modeled after academic grooming progression frameworks (PAN12 corpus methodology).

### Rigorous Evaluation Results (Held-Out Test Set)

| Metric | AI4Bharat IndicBERTv2 (Primary) | TF-IDF Baseline (Offline Fallback) | Advantage / Delta |
|:---|:---|:---|:---|
| **Overall Accuracy** | **73.95%** (88/119) | 66.39% (79/119) | **+7.56%** higher accuracy |
| **Macro F1-Score** | **0.6915** | 0.5295 | **+16.20%** semantic boost |
| **Weighted F1-Score** | **0.7365** | 0.6357 | **+10.08%** class balance |
| **Harmful Missed Rate (FNR)** | **18.97%** | **48.28%** | **Catches 2.5x more predatory threats** |
| **Neutral False Positive Rate** | **21.31%** | 9.84% *(due to severe neutral bias)* | Prevents parental alarm fatigue |
| **Inference Latency (CPU)** | **34.60 ms** (P50: 32.7ms, P95: 44.1ms) | 0.45 ms | Ultra-fast real-time webhook throughput |

> Detailed data cards and benchmark breakdowns are documented in [`backend/ml/DATA_CARD.md`](backend/ml/DATA_CARD.md) and [`backend/ml/MODEL_EVALUATION_REPORT.md`](backend/ml/MODEL_EVALUATION_REPORT.md).

---

## 🔒 Privacy & Safeguarding Architecture

Digital Guardrails is engineered with privacy as a foundational architectural boundary:

1. **Zero Full-Text Chat Storage**: Raw conversational turns are processed entirely in-memory and immediately discarded. Neither the database nor the disk logs store message bodies.
2. **Strict Regex Redaction**: Before generating guardian excerpts, text passes through redaction pipelines stripping phone numbers, email addresses, and URLs.
3. **Bounded Snippet Windows**: Only lines meeting suspicious thresholds produce snippets, capped at a maximum of 140 characters.
4. **Temporal Context Separation**: The backend preserves only the last 12 categorized timestamps for sequence escalation; prior message contents are never retained.
5. **No Cross-Role Data Leakage**: The child's anonymous reporting portal is isolated from guardian accounts. Guardians cannot view youth reports, and children do not have access to guardian alert logs.
6. **PBKDF2-SHA256 & JWT Authentication**: All administrative and caseworker endpoints are protected with industry-standard cryptographic password hashing and time-bound bearer tokens.

---

## 💻 Local Development Setup

### Prerequisites
* **Node.js**: `v20.19.0+`
* **Python**: `3.12+`
* **Git**

### One-Click Launch (Windows)
Run the automated launcher script from the project root:
```powershell
.\run.bat
```
This script checks the virtual environment, installs any missing dependencies, starts the FastAPI backend (port 8000), launches the Vite frontend (port 5173), and automatically opens your browser.

---

### Step-by-Step Manual Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/Prajj11/GDG-Hackathon.git
cd GDG-Hackathon
```

#### 2. Backend Environment & Model Setup
```powershell
# Create Python virtual environment
python -m venv .venv

# Activate environment
.\.venv\Scripts\Activate.ps1

# Install PyTorch and backend requirements
pip install -r backend/requirements-ml.txt --extra-index-url https://download.pytorch.org/whl/cpu

# Train and cache the IndicBERTv2 classifier head (one-time; ~1.1 GB model cache)
$env:HF_HOME = "$PWD/backend/artifacts/hf-cache"
python -m backend.ml.train
```

#### 3. Frontend Installation
```powershell
npm install
```

#### 4. Run the Development Servers
Open two terminal windows:

**Terminal 1 — Backend (FastAPI):**
```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — Frontend (Vite):**
```powershell
npm run dev
```

* **Frontend App**: [http://127.0.0.1:5173](http://127.0.0.1:5173)
* **Interactive API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **API Health Status**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

## 🧪 Running Automated Tests & Validation

```powershell
# 1. Type check and build frontend
npm run build

# 2. Run backend test suite (FastAPI + Auth + Support + Data tests)
.\.venv\Scripts\python.exe -m pytest backend/tests -q

# 3. Evaluate baseline TF-IDF model
.\.venv\Scripts\python.exe -m backend.ml.evaluate --mode baseline --output backend/ml/evaluation-baseline.json

# 4. Evaluate fine-tuned IndicBERTv2 model
.\.venv\Scripts\python.exe -m backend.ml.evaluate --mode indicbert --output backend/ml/evaluation-indicbert.json

# 5. Measure real-time CPU latency
.\.venv\Scripts\python.exe -m backend.ml.benchmark_latency
```

---

## 📡 Key API Endpoints

| Method | Endpoint | Access | Purpose |
|:---|:---|:---|:---|
| `POST` | `/api/analyze` | Public / Token | Evaluates multi-turn messages, applies sequence escalation, and generates alerts if risk exceeds threshold. |
| `GET` | `/api/health` | Public | Returns detector identity (`indicbert` vs `baseline`), uptime, and database health. |
| `POST` | `/api/auth/login` | Public | Authenticates guardians and caseworkers; returns a 1-hour signed JWT. |
| `GET` | `/api/alerts` | Guardian JWT | Fetches redacted alert records, filtered by severity and review status. |
| `PATCH`| `/api/alerts/{id}/review` | Guardian JWT | Marks an alert as reviewed by the parent. |
| `POST` | `/api/support/context` | Capability Token | Validates short-lived signed capability token for youth portal handoff. |
| `POST` | `/api/support/reports` | Anonymous Child | Submits an anonymous report with a browser-generated secret hash. |
| `GET` | `/api/support/reports/{id}` | Secret Bearer | Retrieves status of an anonymous report using the private secret. |
| `GET` | `/api/ngo/reports` | Caseworker JWT | Fetches district-filtered incident reports for CWC triage. |
| `PATCH`| `/api/ngo/reports/{id}/status`| Caseworker JWT | Updates incident status and logs caseworker case notes. |

---

## 📂 Project Structure

```
GDG-Hackathon/
├── app/                         # Lightweight demo package
├── backend/                     # FastAPI core backend service
│   ├── artifacts/               # Cached model weights & tokenizer files
│   ├── ml/                      # Machine learning engine & training pipeline
│   │   ├── benchmark_latency.py # Inference profiling script
│   │   ├── build_dataset.py     # Hybrid dataset compilation script
│   │   ├── data.py              # Synthetic grooming training examples
│   │   ├── DATA_CARD.md         # Academic data card & schema specs
│   │   ├── dataset.json         # Unified 790-conversation safety corpus
│   │   ├── detector.py          # IndicBERTv2 & TF-IDF runtime detector
│   │   ├── evaluate.py          # Rigorous multi-metric evaluation script
│   │   ├── MODEL_EVALUATION_REPORT.md # In-depth evaluation report
│   │   └── train.py             # Head training & representation extractor
│   ├── tests/                   # Integration and unit tests
│   ├── aid.py                   # Aid provider protocol & simulated dispatcher
│   ├── auth.py                  # JWT authentication & PBKDF2 password hashing
│   ├── database.py              # SQLAlchemy ORM models & seed accounts
│   ├── main.py                  # FastAPI route controllers & lifespan hooks
│   ├── requirements.txt         # Core dependencies (lightweight)
│   ├── requirements-ml.txt      # PyTorch & Transformers dependencies
│   └── support.py               # Anonymous youth support routes
├── public/                      # Static assets & icons
├── src/                         # React 19 + TypeScript frontend application
│   ├── api.ts                   # Type-safe Axios client & API interfaces
│   ├── App.tsx                  # Main router, Guardian dashboard, and CWC views
│   ├── GuardianLogin.tsx        # Role-based sign-in & registration portal
│   ├── Support.tsx              # Public anonymous youth help portal
│   ├── index.css                # Custom theme & typography styling
│   └── main.tsx                 # Application entry point
├── Dockerfile                   # Production container specification
├── package.json                 # Node dependencies & Vite scripts
├── run.bat                      # Windows one-click launcher script
└── README.md                    # Project documentation
```

---

## 🏛️ Safeguarding & Institutional Disclaimer

Digital Guardrails (Bal Suraksha) is a hackathon prototype designed for ethical child online safety research and demonstration purposes:
* In this prototype, **aid routing is explicitly simulated**; no live distress calls or unauthorized notifications are dispatched to emergency response teams.
* Official emergency resources provided in the app link to real, verified helplines: **112** (National Emergency Response System) and **1098** (Childline India).
* Transitioning this prototype to institutional production requires accredited Child Welfare Committee (CWC) API integrations, strict multi-party consent frameworks, verified safeguarding audits, and end-to-end encryption.
