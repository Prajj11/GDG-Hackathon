# Digital Guardrails + Support Ecosystems

Latest verification (September 12, 2026): Codex repaired a global CSS cascade-layer ordering regression and verified the shared UI in development and production. The build, formatting, and 18 API tests pass; responsive checks found no horizontal overflow across nine routes at four viewport widths. See [CODEX_TEST_REPORT.md](CODEX_TEST_REPORT.md) for coverage and remaining model limitations. This supersedes the earlier pending-retest notes below.

A local Bal Suraksha hackathon prototype: React + Vite + Tailwind → FastAPI → AI4Bharat IndicBERTv2 → SQLite → a minimal-context guardian alert, plus an independent anonymous youth report and simulated aid receipt. Antigravity's v2 report records passing core flows, build, formatting, and 14 API tests. Follow-up changes for mobile Settings overflow and model coverage still require retesting; Codex has not run tests, builds, or browser verification for these changes.

## Run locally

Requires Node.js 20.19+ and Python 3.12. Commands below run from the repository root.

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r backend/requirements-ml.txt --extra-index-url https://download.pytorch.org/whl/cpu
npm install

# One-time download and head training; about 1.1 GB of model weights.
$env:HF_HOME = "$PWD/backend/artifacts/hf-cache"
.venv/Scripts/python.exe -m backend.ml.train

# Terminal 1: API. Uses the trained model automatically when artifacts exist.
.venv/Scripts/python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

# Terminal 2: frontend (Vite proxies /api to port 8000)
npm run dev
```

Open **http://127.0.0.1:5173**. API documentation: **http://127.0.0.1:8000/docs**.

For a small offline baseline install only `backend/requirements.txt`, skip training, and set `DETECTOR=baseline`. `DETECTOR=indicbert` requires trained artifacts and fails visibly if they are missing. `auto` selects the trained model when available and otherwise explicitly reports the fallback. There is no random transformer head or external AI API.

On this workspace, dependencies and trained artifacts are already installed. The default backend is currently serving IndicBERTv2; generated weights, databases, and caches are intentionally ignored by Git.

## Three-minute demo

1. Open **Demo panel**, keep **Hinglish**, and analyze **Trust-building**. Expect Medium, 43/100.
2. Without starting a new conversation, analyze **Secrecy request**. The prior category changes this to High, 80/100.
3. Choose **View the guardian alert**: only the short flagged excerpt, explanation, and supportive next steps are shown. Mark it reviewed.
4. Start a new conversation. Switch to **Malayalam** and submit **Harassment** twice: Medium, then High due to repetition.
5. Start a new conversation and submit **Everyday chat**: no alert or message text is saved.
6. Open **Overview**, filter alerts, then inspect **Trends & insights** and **Settings**.
7. Analyze a new secrecy/coercion message in the demo panel, then choose **Open youth support** in its result. A short-lived capability offers a starting choice based on the same IndicBERT signal; no conversation text is passed to the portal.
8. Change or accept the choice, optionally attach the safety signal, choose how soon support is wanted, and submit with or without a message. The receipt says **Routed · simulation only** and explicitly states no human or helpline was contacted.
9. Open `/help` independently in a fresh tab: report without an alert or guardian login. Open **Talk to someone now** to see real help numbers without completing the form. Do not place real calls during the demo.

Samples in the UI are deliberately labeled as training examples. The service starts with an empty database; any populated local alerts came from actual demo submissions, not fabricated statistics.

## What the model actually does

The primary encoder is **[AI4Bharat/IndicBERTv2-MLM-only](https://huggingface.co/ai4bharat/IndicBERTv2-MLM-only)**, developed by AI4Bharat. The model revision is pinned to `8598f13fe52443bc3fc054fcd665944560145b5c`. See [AI4Bharat's reference implementation](https://github.com/AI4Bharat/IndicBERT).

`backend/ml/train.py` loads the real model through Hugging Face Transformers, mean-pools its masked hidden states, freezes the encoder, and trains a standard-scaled logistic-regression classifier head. **This is supervised training of the head over IndicBERT representations, not end-to-end encoder fine-tuning or zero-shot classification.** The trained encoder, tokenizer, head, dataset hash, and method metadata are saved locally. No MuRIL or other foreign-developed base model is used.

`backend/ml/data.py` contains **128 synthetic, non-explicit examples** covering English, Hindi, Malayalam, Hinglish, and Manglish. After Antigravity's v2 report, 17 examples were added: Malayalam coercion and benign sharing/advice, English coercion, and Hinglish isolation and benign privacy contexts. The reported failing sentences were not copied into training. Categories:

- grooming-trust-building
- grooming-isolation-request
- grooming-coercive-language
- bullying-harassment
- neutral

The alternate baseline is character TF-IDF (2–5 grams) + logistic regression trained on exactly the same examples. The frontend and `/api/health` always identify the active detector.

`analyze_message(text)` returns a score, level, category, confidence, explanation, and model identity. FastAPI supplements it with a bounded sequence policy: trust-building followed by isolation, or repeated harassment within 24 hours, raises concern. Only the last 12 category/timestamp signals are retained; **raw previous messages are never stored**. This is a small category-sequence model, not a claim to understand a person's intent or establish their age.

Scores are **illustrative review-priority values, not calibrated probabilities of harm**: neutral 12, trust-building 43, isolation 66, coercion 85, harassment 60. Low confidence caps a non-neutral initial score at 49. Sequence escalation can increase it. Low < 40; Medium 40–74; High ≥ 75. Neutral messages create no alert. The language selector records the intended language; it is not an automatic language detector.

## Validation and known limitations

```powershell
npm run build
.venv/Scripts/python.exe -m pytest backend/tests -q
.venv/Scripts/python.exe -m backend.ml.evaluate --mode baseline --output backend/ml/evaluation-baseline.json
.venv/Scripts/python.exe -m backend.ml.evaluate --mode indicbert --output backend/ml/evaluation-indicbert.json
```

The project includes a `pytest.ini` that keeps pytest temp and cache files under `scratch/`, which avoids Windows user-temp permission problems seen during external testing.

Antigravity's v2 results on **30 known synthetic regression scenarios**, before the latest 128-example training update:

| Detector | Correct | Macro F1 |
|---|---:|---:|
| IndicBERTv2 + trained head | 28/30 (93.3%) | 0.928 |
| TF-IDF fallback | 29/30 (96.7%) | 0.968 |

Full reports, per-language results, and mistakes are recorded in `backend/ml/evaluation-*.json` and `ANTIGRAVITY_V2_TEST_REPORT.md`. The original artifacts call the set held-out, but the Hinglish safety-advice sentence also appears in training and these cases have informed development. Treat the scores as **regression results, not an independent or real-world safety benchmark**. The evaluation script now discloses this scope, source dataset hash, and exact overlap count for future runs. Historical result files are preserved unchanged.

Antigravity verified the four previously reported false positives now return neutral. Remaining v2 observations were a missed Malayalam coercion threat, Hinglish isolation labeled harassment, and one missed English coercion case in the fallback. The expanded training set addresses these coverage areas, but the new artifacts have not been evaluated by Codex; ISSUE-007 must remain pending external retest. New, independently authored multilingual scenarios and fluent-speaker review are needed to assess generalization. Code-mixed Roman text, negation, sarcasm, speaker roles, long-term context, and unfamiliar phrasing remain limitations. No production accuracy, recall, or calibrated-confidence claim is made.

The API tests cover input validation, supported-language coercion samples, cross-message escalation, conversation separation, review persistence, metadata-only storage, bounded/redacted excerpts, retention, access tokens, and missing alerts. Browser checks cover ingestion → sequence escalation → alert detail → review, plus regional-language interaction and responsive layouts.

## Privacy and scope

- Synthetic-data demo only; no real-platform monitoring or automatic messaging is implemented.
- Tables: `users` (one demo guardian and preferences), `conversations` (pseudonymous metadata and categories only), `alerts` (score, category, short excerpt, explanation, review status), `reports` (child-authored choices/optional text and receipt digest), and `aid_routes` (simulated delivery metadata).
- A message window accepts up to 2,000 characters / 8 lines. Each nonempty line is analyzed transiently; only the strongest line is eligible for a snippet. The encoder truncates each line to 192 tokens, a known limitation for unusually long inputs.
- Snippets are capped at 140 characters plus an ellipsis; email addresses, phone numbers, and links are redacted. Names and all other identifying details cannot be reliably removed, so real messages should not be entered.
- No full chat logs, analytics trackers, third-party inference calls, or real child names. The input is cleared after successful submission.
- Retention is configurable (1/7/30 days). Cleanup runs on startup and data requests, not a background timer. Disabling snippets clears existing excerpts and suppresses future ones; re-enabling cannot restore cleared text.
- Local demo binds to loopback without a login by default. Optional single-guardian JWT login uses python-jose and a passlib PBKDF2-SHA256 password hash; see below. Legacy hosted-demo tokens remain supported only when guardian login is not configured. Neither mode implements multi-tenant accounts. A production deployment needs consent, account isolation, encrypted storage, a verified safeguarding process, rate limits, and independent evaluation.
- Single-worker inference serializes updates. PostgreSQL uses the same ORM models with a `postgresql+psycopg://...` connection string, but migration of existing data is a separate operation. SQLite and PostgreSQL-compatible SQL are used; a live PostgreSQL deployment has not been tested here.

## Deployment

The supplied `Dockerfile` trains IndicBERTv2 during the image build; `render.yaml` describes the API and persistent SQLite disk. The requested model exceeds typical free-instance memory budgets; the blueprint uses a paid memory tier. **Review the plan before creating the service. No paid resource has been created by this build.**

1. Deploy the API to Render from this repository using its blueprint, or deploy the Dockerfile on Railway. Provide a persistent volume for SQLite, or use PostgreSQL.
2. Set `DEMO_ACCESS_TOKEN` (Render can generate it), `DATABASE_URL`, and exact `CORS_ORIGINS` for the frontend. `backend.serve` rejects missing/short tokens.
3. Deploy the frontend with Vercel (`vercel.json`) or Netlify (`netlify.toml`). Set `VITE_API_URL=https://YOUR-API-HOST/api` **before the frontend build**. SPA rewrites allow direct alert-detail links.
4. In Settings, enter the shared demo token. It is stored only in that browser tab's session storage and sent as a Bearer header; it is never baked into the frontend build.
5. Check `/api/health` reports `model_kind: indicbert`, then submit a synthetic message through the hosted UI.

Hosting configurations are provided for later use. Nothing has been deployed, as requested: keep this build local for now. Antigravity verified the merged v2 flows; subsequent layout and training changes are pending its retest.

## Motion and accessibility

Tailwind styles define a calm indigo, green, amber, and muted-red palette. Alert cards fade/lift over 300ms with 70ms stagger; badges and status controls transition over 200ms; buttons have a gentle press response; alert details use a clip reveal. Exactly one main CTA on each product route has subtle pointer magnetism. Keyboard users have visible focus, a skip link, readable risk labels, and semantic controls. All motion and magnetism are disabled with `prefers-reduced-motion`. There is no parallax or scroll-driven storytelling.

## Support Ecosystems (v2)

Public routes: `/help`, `/help/report`, `/help/status`, `/help/confirmation/:id`; `/support` redirects to `/help`. These mount independently of the guardian application and never fetch guardian alerts or attach its Bearer token. The portal uses teal/lavender colors, 420ms fade/lift, 80ms choice stagger, gentle press feedback, and exactly one magnetic action: the always-available immediate-help control. Its phone numbers work without the API.

The form starts with choices, allows empty optional text, and never asks for a name, email, phone, or login. Urgency is the child's choice; all submissions can receive support, including independent high-urgency reports without a model flag. Report text is child-authored and is not reclassified, so a neutral model label cannot block help.

The ingestion response's `support_context_token` is a signed, purpose-restricted 30-minute capability. The demo transfers it through router state, which the portal clears after reading. `/api/support/context` exposes only a suggested choice, category, level, and alert reference. A separate unchecked consent box controls linking; the API validates the signature, expiry, alert match, and consent. No guardian/child label, snippet, conversation ID, or raw chat is copied into the report's detection context. `linked_alert_id` becomes null if its alert is deleted. A child who opts in to linking is choosing correlation with that alert; unlinked reports contain no guardian foreign key.

Each submission uses a browser-generated 256-bit random secret. Only its SHA-256 digest is stored in `reports.anonymous_token`. The raw secret is never a URL parameter or included in an aid payload. Repeating a submission with the same secret returns the same report. The browser stores only the most recent report ID/secret in tab-local session storage, with an in-memory fallback; child-authored text is cleared after submission. A private `report-id.secret` recovery code can restore status. Anyone with it can read that status; the UI provides a **Finish and forget this receipt** action. Forgetting removes local access, not the stored report.

Report and route retention is independent of guardian settings: seven days, with cleanup on startup and report requests. Cleanup is lazy, not a scheduled secure-erasure service. Report retrieval returns status metadata, never the submitted text, guardian fields, or receipt digest. No report list is exposed to guardians. Public reporting does not imply network-level anonymity: browsers and server operators may retain history/access logs, and identifying details typed voluntarily cannot be automatically anonymized. Use synthetic content only in this local demo.

| API | Access / behavior |
|---|---|
| `POST /api/support/context` | Short-lived signed capability in body; minimal suggestion only |
| `POST /api/support/reports` | No guardian login; random receipt secret in body, choice, optional text, urgency, optional consented context |
| `GET /api/support/reports/{id}` | Report's private secret in Bearer header; missing/wrong/expired report returns 404 |
| `POST /api/support/reports/{id}/retry` | Same receipt access; idempotent simulated route retry |
| `POST /api/auth/login` | Optional configured guardian username/password → one-hour JWT |

`backend/aid.py` defines the versioned `AidPayload`, `AidProvider` protocol, and `SimulatedAidProvider`. The only implemented provider makes **no network calls**. Submission is committed before attempting routing; failed delivery stays `submitted`, successful mock delivery creates one route and marks `routed`. The report ID is the adapter's idempotency key and `aid_routes.report_id` is unique. No acknowledgement from a real human is ever fabricated.

The crisis panel links to official information for [India's emergency number 112](https://112.gov.in/) and [Child Helpline 1098](https://www.spniwcd.wcd.gov.in/child-helpline), checked September 11, 2026. `tel:` links require the visitor to choose to call. Reports are never automatically sent to these services.

## Optional guardian login

Install updated backend requirements before restarting. Local anonymous support remains available whether guardian login is enabled or not.

In the API terminal, set `GUARDIAN_USERNAME` (default `guardian`), `GUARDIAN_PASSWORD_HASH` (a passlib PBKDF2-SHA256 hash), and a random `JWT_SECRET`. FastAPI reads process environment variables, not `.env` automatically. Generate the hash interactively without putting the password in shell history:

```powershell
$env:GUARDIAN_PASSWORD_HASH = .venv/Scripts/python.exe -c "from getpass import getpass; from passlib.hash import pbkdf2_sha256; print(pbkdf2_sha256.hash(getpass('Guardian password: ')))"
$env:JWT_SECRET = .venv/Scripts/python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
.venv/Scripts/python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Sign in at `/login`; JWTs last one hour and remain in tab-local session storage. This is one configured guardian, not a registration system. With no configured password hash or demo token, loopback demo access stays open. With no configured JWT secret, the local server generates an ephemeral key; restarting expires existing context links. Hosted JWT mode requires an explicit secret of at least 32 characters. Do not commit credentials or enable public hosting as part of this local build.

## Roadmap and pitch

**Phase 1 — Digital Guardrails:** multilingual pattern signals give guardians minimal context to act.

**Phase 2 — Support Ecosystems:** the same signal can gently help a young person start an anonymous report, while independent reporting keeps support available without a guardian alert. The demo completes the flow with an explicitly simulated aid receipt.

**Phase 3 — Physical-Digital Link (future scope only):** with verified institutional partnerships, extend the same versioned payload to a real NGO or authority case-management API. Partner verification, consent/safeguarding procedures, authenticated transport, delivery retries, and genuine acknowledgements must precede real routing. No institutional partnership, live aid integration, or authority notification is implemented or claimed here.

