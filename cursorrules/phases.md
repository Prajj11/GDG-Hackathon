# Build Phases & Timeline
## Digital Guardrails — 48-Hour Hackathon Execution Plan

**Track:** Bal Suraksha (Track 2)
**Duration:** 48 hours (Sept 11, 12:00 PM → Sept 13, 12:00 PM)
**Version:** 1.0

---

## 1. Guiding Principle
Build the **smallest end-to-end working slice first** (ingestion → detection → alert → dashboard display), then layer polish and secondary features on top. Never leave the project in a state where the core flow is broken — always have a demoable version.

---

## 2. Phase Breakdown

### Phase 0 — Setup & Planning (Hour 0–3)
**Goal:** Environment ready, team aligned, dataset direction chosen.

- [ ] Finalize problem framing and confirm track submission (Bal Suraksha).
- [ ] Set up GitHub repo (public, with `.gitignore` for secrets/env files).
- [ ] Scaffold frontend: `React (Vite) + Tailwind CSS`.
- [ ] Scaffold backend: `FastAPI` project structure with Uvicorn.
- [ ] Set up SQLite DB with SQLAlchemy/SQLModel models (`users`, `conversations`, `alerts`).
- [ ] Decide on dataset approach: source a small existing labeled dataset (grooming/cyberbullying text corpus) or hand-craft a synthetic dataset of ~50–100 example conversations across 2–3 languages (Hindi, English, one regional language).
- [ ] Assign ownership: Frontend / Backend+DB / ML / Deployment+Docs (adjust to team size).

**Deliverable:** Repo skeleton running locally (empty but functional frontend ↔ backend ping).

---

### Phase 1 — Core Detection Engine (Hour 3–14)
**Goal:** ML module that takes text input and returns a risk score + pattern label.

- [ ] Preprocess/prepare dataset (clean, label by pattern type: grooming-trust-building, grooming-isolation, grooming-coercion, bullying-harassment, neutral).
- [ ] Set up multilingual model: load **MuRIL** or **IndicBERT** via Hugging Face Transformers.
- [ ] Implement classification approach:
  - Option A: Fine-tune lightly on the small labeled dataset (time permitting).
  - Option B (fallback): Zero/few-shot classification or a `scikit-learn` baseline (TF-IDF + logistic regression) if fine-tuning proves too slow.
- [ ] Wrap inference in a clean Python function: `analyze_message(text) -> {risk_score, risk_level, pattern_type}`.
- [ ] Unit test the function against sample inputs across languages.

**Deliverable:** Standalone, testable inference function producing sensible outputs on sample text (before wiring into the API).

---

### Phase 2 — Backend API & Database Integration (Hour 10–20, overlapping Phase 1)
**Goal:** FastAPI endpoints wired to the ML module and database.

- [ ] Implement `/api/messages/ingest` — accepts text/conversation, calls ML module, stores conversation + alert (if risk exceeds threshold) in DB.
- [ ] Implement `/api/alerts` and `/api/alerts/{id}` — retrieve alert list and details.
- [ ] Implement `/api/dashboard/summary` — aggregated counts by risk level.
- [ ] (If time allows) Implement basic auth (`/api/auth/login`) with JWT.
- [ ] Write Pydantic schemas for clean request/response validation.
- [ ] Test all endpoints via FastAPI's built-in Swagger UI (`/docs`).

**Deliverable:** Fully functional backend, testable via Swagger UI independent of frontend.

---

### Phase 3 — Frontend Dashboard (Hour 14–28, overlapping Phase 2)
**Goal:** React + Tailwind UI consuming the backend API.

- [ ] Build Login screen (if auth implemented) — otherwise skip to Dashboard with a mock/default user.
- [ ] Build Dashboard Home: alert feed (cards) + summary stats, pulling from `/api/alerts` and `/api/dashboard/summary`.
- [ ] Build Alert Detail view: risk level, pattern explanation (plain language), flagged snippet, suggested next steps.
- [ ] Build Demo Ingestion Panel: simple form/textarea where a sample message/conversation can be submitted to `/api/messages/ingest` live, for demo purposes.
- [ ] Style with Tailwind per `design.md` (risk badges, calm color palette, clear typography).
- [ ] (Optional) Add Trends/Insights view with Recharts/Chart.js.
- [ ] (Optional) Add WebSocket live-update for new alerts instead of manual refresh.

**Deliverable:** Working frontend fully integrated with backend, demonstrating the complete flow live.

---

### Phase 4 — Integration Testing & Bug Fixing (Hour 28–36)
**Goal:** Ensure the full pipeline works reliably end-to-end.

- [ ] Full end-to-end test: submit sample messages across all target languages → verify correct risk classification → verify alert appears correctly on dashboard.
- [ ] Fix edge cases: empty input, very short text, mixed-language input, neutral/benign messages (should NOT be flagged — check false positive rate).
- [ ] Cross-check that no secrets/API keys are committed to the repo.
- [ ] Polish error handling (API failures shown gracefully in UI, not blank screens).

**Deliverable:** Stable, demo-ready application with no critical bugs in the core flow.

---

### Phase 5 — Deployment (Hour 32–38, overlapping Phase 4)
**Goal:** Live, working prototype link.

- [ ] Deploy frontend to Vercel or Netlify.
- [ ] Deploy backend (FastAPI) to Render or Railway.
- [ ] Configure environment variables (API base URL, secrets) properly — none hardcoded or committed.
- [ ] Verify deployed frontend correctly talks to deployed backend (CORS configured correctly in FastAPI).
- [ ] Smoke-test the live prototype link end-to-end.

**Deliverable:** Publicly accessible working prototype link.

---

### Phase 6 — PPT, Video & Documentation (Hour 36–46)
**Goal:** Complete all required hackathon submission materials.

- [ ] Build the 6-slide PPT per the mandated structure:
  1. Title Slide
  2. Problem Statement (use `prd.md` Section 2)
  3. Solution (use `prd.md` Sections 4–5)
  4. Technology & Implementation (use `architecture.md`)
  5. Feasibility, Scalability & Impact (use `prd.md` + `architecture.md` Section 6)
  6. Prototype & Future Scope (screenshots/GIFs from the working app + `prd.md` Section 5.3)
- [ ] Record the 3-minute prototype demo video:
  - 0:00–0:30 — Problem framing
  - 0:30–1:30 — Live demo: submit a message → detection → dashboard alert
  - 1:30–2:30 — Walkthrough of key screens (dashboard, alert detail, trends)
  - 2:30–3:00 — Tech stack recap + future scope
- [ ] Write the GitHub README: project overview, problem, solution, tech stack, setup/run instructions, team info.
- [ ] Final check: repo is public, no secrets committed, README is clear and complete.

**Deliverable:** PPT, video, and README ready for submission.

---

### Phase 7 — Final Submission (Hour 46–48)
**Goal:** Submit everything correctly on Unstop (or designated platform) before the deadline.

- [ ] Double-check all four required submissions: PPT, public GitHub repo link, working prototype link, 3-minute video.
- [ ] Verify GitHub link is entered in the correct field on Unstop.
- [ ] Submit with buffer time before the 12:00 PM deadline (aim to finish by hour ~46–47, not the last minute).

**Deliverable:** Complete, on-time submission.

---

## 3. Risk Mitigation / Contingency Plan

| Risk | Mitigation |
|---|---|
| Fine-tuning the multilingual model takes too long | Fall back to zero-shot classification or a scikit-learn baseline classifier |
| Real-time WebSocket integration is too complex | Ship batch/simulated ingestion only (already the planned MVP scope) |
| Dataset is too small/unbalanced, causing poor demo results | Hand-craft a curated, small, clearly illustrative demo dataset — quality over scale for a hackathon demo |
| Deployment issues late in the timeline | Start deployment by Hour 32, not Hour 45 — leaves buffer to debug CORS/env issues |
| Team runs out of time for polish | Prioritize: (1) working core flow, (2) PPT + video, (3) visual polish — in that order |

---

## 4. Suggested Team Role Split (adjust to actual team size)
- **ML/Data:** Dataset prep + model integration (Phase 1)
- **Backend:** API + DB (Phase 2)
- **Frontend:** Dashboard UI (Phase 3)
- **Docs/Deploy/PM:** Deployment, README, PPT, video editing, timeline tracking (Phases 5–7, supporting throughout)
