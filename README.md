# Digital Guardrails

A working Bal Suraksha hackathon prototype: React + Vite + Tailwind → FastAPI → AI4Bharat IndicBERTv2 → SQLite → a minimal-context guardian alert.

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

Samples in the UI are deliberately labeled as training examples. The service starts with an empty database; any populated local alerts came from actual demo submissions, not fabricated statistics.

## What the model actually does

The primary encoder is **[AI4Bharat/IndicBERTv2-MLM-only](https://huggingface.co/ai4bharat/IndicBERTv2-MLM-only)**, developed by AI4Bharat. The model revision is pinned to `8598f13fe52443bc3fc054fcd665944560145b5c`. See [AI4Bharat's reference implementation](https://github.com/AI4Bharat/IndicBERT).

`backend/ml/train.py` loads the real model through Hugging Face Transformers, mean-pools its masked hidden states, freezes the encoder, and trains a standard-scaled logistic-regression classifier head. **This is supervised training of the head over IndicBERT representations, not end-to-end encoder fine-tuning or zero-shot classification.** The trained encoder, tokenizer, head, dataset hash, and method metadata are saved locally. No MuRIL or other foreign-developed base model is used.

`backend/ml/data.py` contains **102 synthetic, non-explicit examples** covering English, Hindi, Malayalam, Hinglish, and Manglish. Categories:

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

Initial held-out evaluation on **30 synthetic scenarios**:

| Detector | Correct | Macro F1 |
|---|---:|---:|
| IndicBERTv2 + trained head | 23/30 (76.7%) | 0.778 |
| TF-IDF fallback | 26/30 (86.7%) | 0.880 |

Full reports, per-language results, and all mistakes are checked into `backend/ml/evaluation-*.json`. These are smoke results on a tiny dataset, **not a real-world safety benchmark**. The primary model particularly overflags harmless safety advice and quoted reports. Code-mixed Roman text, negation, sarcasm, speaker roles, long-term context, and unfamiliar phrasing need substantially more curated data and independent evaluation. No production accuracy, recall, or calibrated-confidence claim is made.

The API tests cover input validation, supported-language coercion samples, cross-message escalation, conversation separation, review persistence, metadata-only storage, bounded/redacted excerpts, retention, access tokens, and missing alerts. Browser checks cover ingestion → sequence escalation → alert detail → review, plus regional-language interaction and responsive layouts.

## Privacy and scope

- Synthetic-data demo only; no real-platform monitoring or automatic messaging is implemented.
- Tables: `users` (one demo guardian and preferences), `conversations` (pseudonymous metadata and categories only), `alerts` (score, category, short excerpt, explanation, review status).
- A message window accepts up to 2,000 characters / 8 lines. Each nonempty line is analyzed transiently; only the strongest line is eligible for a snippet. The encoder truncates each line to 192 tokens, a known limitation for unusually long inputs.
- Snippets are capped at 140 characters plus an ellipsis; email addresses, phone numbers, and links are redacted. Names and all other identifying details cannot be reliably removed, so real messages should not be entered.
- No full chat logs, analytics trackers, third-party inference calls, or real child names. The input is cleared after successful submission.
- Retention is configurable (1/7/30 days). Cleanup runs on startup and data requests, not a background timer. Disabling snippets clears existing excerpts and suppresses future ones; re-enabling cannot restore cleared text.
- Local demo binds to loopback without a login. Hosted entrypoints require a shared demo access token of at least 24 characters. This is **not** guardian identity or multi-tenant authorization. A production deployment needs consent, account isolation, stronger authentication, encrypted storage, a verified safeguarding process, rate limits, and independent evaluation.
- Single-worker inference serializes updates. PostgreSQL uses the same ORM models with a `postgresql+psycopg://...` connection string, but migration of existing data is a separate operation. SQLite and PostgreSQL-compatible SQL are used; a live PostgreSQL deployment has not been tested here.

## Deployment

The supplied `Dockerfile` trains IndicBERTv2 during the image build; `render.yaml` describes the API and persistent SQLite disk. The requested model exceeds typical free-instance memory budgets; the blueprint uses a paid memory tier. **Review the plan before creating the service. No paid resource has been created by this build.**

1. Deploy the API to Render from this repository using its blueprint, or deploy the Dockerfile on Railway. Provide a persistent volume for SQLite, or use PostgreSQL.
2. Set `DEMO_ACCESS_TOKEN` (Render can generate it), `DATABASE_URL`, and exact `CORS_ORIGINS` for the frontend. `backend.serve` rejects missing/short tokens.
3. Deploy the frontend with Vercel (`vercel.json`) or Netlify (`netlify.toml`). Set `VITE_API_URL=https://YOUR-API-HOST/api` **before the frontend build**. SPA rewrites allow direct alert-detail links.
4. In Settings, enter the shared demo token. It is stored only in that browser tab's session storage and sent as a Bearer header; it is never baked into the frontend build.
5. Check `/api/health` reports `model_kind: indicbert`, then submit a synthetic message through the hosted UI.

The local environment is running and verified. Hosting configurations are provided for later use. Nothing has been deployed, as requested: keep this build local for now.

## Motion and accessibility

Tailwind styles define a calm indigo, green, amber, and muted-red palette. Alert cards fade/lift over 300ms with 70ms stagger; badges and status controls transition over 200ms; buttons have a gentle press response; alert details use a clip reveal. Exactly one main CTA on each product route has subtle pointer magnetism. Keyboard users have visible focus, a skip link, readable risk labels, and semantic controls. All motion and magnetism are disabled with `prefers-reduced-motion`. There is no parallax or scroll-driven storytelling.

