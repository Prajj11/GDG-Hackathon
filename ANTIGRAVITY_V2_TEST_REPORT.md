# Digital Guardrails — Test report (V2 Verification)

Date: 2026-09-11
Tester / agent: Antigravity AI Agent (Pair Programming with User)
OS / browser / viewport sizes: Windows 11 / Chromium (Playwright automated & browser subagent) / Tested at 1440x1000, 1280x800, 1024x768, 768x1024, 390x844, 320x700
Source commit: `3d1e55c00f9464e0f530ed4bcaaa8cb717924851`
API model / mode: `IndicBERTv2 · trained head` (active), `TF-IDF · fallback classifier` (verified in isolation)
Database: Existing synthetic demo database (`digital_guardrails.db`) + isolated test databases (`scratch/isolated_test.db`, `scratch/auth_test.db`)

---

## Overall result

**PASS** (All core functional, privacy, security, and V2 youth support acceptance criteria passed. Prior issues ISSUE-001 through ISSUE-005 are fully resolved. One minor UI overflow finding on `/settings` at 390px mobile viewport is documented as ISSUE-006, along with held-out model observations).

---

## Commands and results

| Check | Command or steps | Result | Evidence |
|---|---|---|---|
| Frontend Build | `npm run build` | **PASS** | Vite v6.4.3 built cleanly in 3.71s (`tsc -b && vite build`), zero TypeScript or JSX compile errors. Bundle: JS 775.92 kB, CSS 67.07 kB. |
| Formatting Check | `npm run format:check` | **PASS** | Prettier checked `src` and `vite.config.ts`; all files matched code style with zero warnings. |
| API Pytest Suite | `.venv/Scripts/python.exe -m pytest --rootdir=. -c pytest.ini backend/tests -v` | **PASS** | 14 passed in 3.84s. `--basetemp=scratch/pytest_tmp` and `-o cache_dir=scratch/pytest_cache` resolved ISSUE-001 completely on Windows. |
| IndicBERT Evaluation | `python -m backend.ml.evaluate --mode indicbert --output backend/ml/evaluation-indicbert.json` | **PASS** | **28/30 correct (93.3% accuracy)**, Macro F1: **0.928**. Significant increase from earlier 23/30 (76.7%, F1 0.778). |
| Fallback Evaluation | `python -m backend.ml.evaluate --mode baseline --output backend/ml/evaluation-baseline.json` | **PASS** | **29/30 correct (96.7% accuracy)**, Macro F1: **0.968** across held-out synthetic test scenarios. |
| Database & Retention Integrity | `python scratch/test_db_and_retention.py` | **PASS** | `token_is_digest: True` (raw secret never stored in DB; SHA-256 64-hex digest stored); `detection_context_isolated: True` (only pattern and risk level stored); `alert_deletion_sets_null: True` (ON DELETE SET NULL verified on SQLite foreign keys); `retention_cleanup_deletes_expired: True` (expired reports & cascaded routes purged). |
| Guardian Auth & JWT Protection | `python scratch/test_auth_isolated.py` | **PASS** | Single-guardian login verified: wrong password (401), valid login (200 + JWT), protected endpoints require JWT (401 without, 200 with), tampered JWT (401). Guardian JWT cannot access youth support reports (404). Youth portal remains 100% accessible without guardian credentials. |
| Hosted Configuration Guard | `python -c "..."` (isolated with `DG_HOSTED=true`) | **PASS** | Missing/short `DEMO_ACCESS_TOKEN` (<24 chars) raises `RuntimeError` on startup; short `JWT_SECRET` (<32 chars) raises `RuntimeError`. |
| Missing Artifacts & Fallback Mode | `python -c "..."` (isolated with `DETECTOR=indicbert` & missing path / `DETECTOR=baseline`) | **PASS** | Missing checkpoint raises visible `RuntimeError: Train IndicBERT first...`; `DETECTOR=baseline` returns `model_kind: baseline` and `TF-IDF · fallback classifier`. |

---

## Browser scenarios

| Scenario | Input / language / conversation | Expected | Actual | Pass/fail |
|---|---|---|---|---|
| Trust → secrecy escalation | Hinglish: "Tum apni age se bahut mature ho..." then "Mummy papa ko mat batana. Ye humara secret hai. Private chat pe aao." | Step 1: Medium 43/100 (Unusual trust-building). Step 2: High 80/100 with sequence escalation explanation. | Step 1: 43/100, grooming-trust-building. Step 2: 80/100, grooming-isolation-request. Explanation: "Earlier messages showed trust-building, followed now by secrecy. This change increases concern." | **PASS** |
| Repeated harassment | Malayalam/Manglish: "Nee oru mandan aanu..." submitted twice in same thread. | Step 1: Medium 60/100. Step 2: High 78/100 with repetition explanation. | Step 1: 60/100, bullying-harassment. Step 2: 78/100, bullying-harassment (+18 repetition escalation). | **PASS** |
| Neutral input | English: "Hey are we still meeting up for science project homework at 4pm?" | Low risk (<40), neutral, no alert created, conversation count incremented. | Score: 12/100, Low, neutral, confidence 0.973, alert_id: null, no DB alert saved. | **PASS** |
| Review persistence | Alert `480a4723-8ca0-4bf2-9848-f04313ff0528` on `/alerts/:id` | Click "Mark as reviewed" updates UI; state persists across hard page reload. | Status changed to "Reviewed · Mark as unreviewed" and persisted across page refresh. | **PASS** |
| Risk + child filters | Overview dashboard (`/`) with filter buttons and dropdowns | Status filters ("Needs review", "Reviewed", "All alerts") and child/risk dropdowns filter alerts correctly. | Filter panel opened cleanly via "Filters" button (`aria-expanded: true`), filters combined properly. | **PASS** |
| Retention / excerpts redaction | Synthetic text with email, phone number, and URL | Flagged snippet has `[phone]`, `[email]`, `[link]` redaction, bounded to 140 chars. | Snippets redacted in DB; disabling excerpts in Settings purges existing snippets permanently. | **PASS** |
| Mobile overview overflow | 390x844 and 320x700 on Overview (`/`) | **No horizontal scroll or overflow** from cards or chart rails. | **Verified fix**: At 390px, `scrollWidth: 376`, `innerWidth: 376` (`hasOverflow: false`). At 320px, `scrollWidth: 306`, `innerWidth: 306` (`hasOverflow: false`). | **PASS** |
| Youth support portal (`/help`) | Direct navigation to `/help` with no guardian auth | Distinct teal/lavender design, no login required, clear guidance, calm layout. | Rendered `/help` with "You're in control of what you share", no guardian requests. `/support` successfully redirects to `/help`. | **PASS** |
| Immediate danger drawer | "I'm in immediate danger / Talk to someone now" | Immediate 112 (Emergency Services) and 1098 (Childline India) dial links appear with zero API dependency. | Opened drawer with `tel:112` and `tel:1098` links immediately. Closing drawer preserved existing draft. | **PASS** |
| Anonymous report & simulated aid | Step 1: "I'm being pressured or asked for secrets", Step 2: empty or custom text, Medium urgency. | Created report and simulated aid route; receipt displays "Routed · simulation only", explicit "No human or helpline contacted". | HTTP 201, status `routed`, channel `Simulated Child Helpline Endpoint`, clear simulated disclaimer. | **PASS** |
| Context handover ("Open youth support") | Click "Open youth support" from high-risk demo result | Navigates to `/help/report` with pre-filled context matching detection; no raw text/guardian IDs transferred. | Navigated with pre-filled context "Someone is asking me to keep secrets". "Attach earlier safety signal" toggle available and working. | **PASS** |
| Detection context consent | Submit report with context checkbox ON vs OFF | ON: attaches `pattern_type` & `risk_level` only. OFF: `detection_context` is null. | Verified in DB and receipt: ON shows "Earlier safety signal: Shared with your permission". OFF stores null. | **PASS** |
| Receipt secret reveal & recovery | Save private 64-character receipt code, test `/help/status` | Code revealed safely; reloading or entering code on `/help/status` retrieves report. | Code revealed; retrieved on `/help/status` with HTTP 200 and `Cache-Control: no-store`. | **PASS** |
| "Finish and forget this receipt" | Click "Finish and forget this receipt" on confirmation | Session storage cleared, history state cleared, redirects to welcome. | Code cleared from session storage; direct return requires recovery code; stored report retained until 7-day retention expiry. | **PASS** |
| Unauthorized / wrong receipt code | GET `/api/support/reports/:id` with wrong secret, missing token, or guardian JWT | HTTP 404 (or 401 on tampered context token). No unauthenticated list endpoint. | Wrong secret: 404. Missing secret: 404. Guardian JWT: 404. `GET /api/support/reports`: 405 Method Not Allowed. | **PASS** |
| Input validation & bounds | Note length (0, 1500, 1501 chars), malformed tokens, extra fields, XSS | 0 accepted (201), 1500 accepted (201), 1501 rejected (422), invalid token format rejected (422), extra fields forbidden (422), XSS escaped. | 0 chars: 201; 1500 chars: 201; 1501 chars: 422; bad hex token: 422; unexpected fields: 422; XSS handled as plain text safely. | **PASS** |
| Keyboard / accessibility / motion | Skip link, visible focus, reduced motion query | Focus rings visible on skip link and buttons; animations/magnetism disabled under `prefers-reduced-motion`. | Skip link (`#main-content`) works; hidden mobile sidebar sets `visibility: hidden` (not focusable); motion disabled under `@media (prefers-reduced-motion)`. | **PASS** |
| Invalid alert ID handling | Navigate to `/alerts/nonexistent-id-00000000` | Shows informative error instead of blank screen or crash. | Displays friendly empty state: "This alert was not found or its retention period ended." with return link. | **PASS** |

---

## Retest of Previous Issues (ISSUE-001 through ISSUE-005)

### ISSUE-001: Default Pytest Execution Fails with PermissionError on Windows
- **Original Symptom**: `PermissionError: [WinError 5] Access is denied: 'C:\Users\naren\AppData\Local\Temp\pytest-of-naren'`
- **Fix Verified**: `pytest.ini` now configures `addopts = --basetemp=scratch/pytest_tmp -o cache_dir=scratch/pytest_cache`.
- **Retest Result**: **RESOLVED / PASS**. All 14 tests in `backend/tests/test_api.py` passed in 3.84s without permission errors.

### ISSUE-002: IndicBERT Misclassifies Harmless Safety Advice as Grooming Isolation
- **Original Symptom**: `"Teacher ne bola koi photo maange toh mat bhejna aur parents ko batana."` was classified as Medium 66/100 (`grooming-isolation-request`).
- **Retest Result**: **RESOLVED / PASS**. Ingested text returned:
  ```json
  {
    "risk_score": 12,
    "risk_level": "Low",
    "pattern_type": "neutral",
    "confidence": 0.914,
    "alert_id": null
  }
  ```
  Classified as Low (12/100) neutral with zero alert created.

### ISSUE-003: IndicBERT Model Ignores Negation Signals
- **Original Symptom**: `"I am not threatening you and I do not want your private details."` was classified as High 85/100 (`grooming-coercive-language`).
- **Retest Result**: **RESOLVED / PASS**. Ingested text returned:
  ```json
  {
    "risk_score": 12,
    "risk_level": "Low",
    "pattern_type": "neutral",
    "confidence": 0.908,
    "alert_id": null
  }
  ```
  Classified as Low (12/100) neutral with zero alert created.

### ISSUE-004: Quoted Reports of Threatening Messages Trigger False Positives
- **Original Symptom**: `"My friend said someone messaged him: 'Send your photo or I will report you'."` was classified as High 85/100 (`grooming-coercive-language`).
- **Retest Result**: **RESOLVED / PASS**. Ingested text returned:
  ```json
  {
    "risk_score": 12,
    "risk_level": "Low",
    "pattern_type": "neutral",
    "confidence": 0.817,
    "alert_id": null
  }
  ```
  Classified as Low (12/100) neutral with zero alert created.

### ISSUE-005: Gaming Metaphors & Slang Misclassified as Bullying / Harassment
- **Original Symptom**: `"That game was killer! You completely destroyed me in that match."` was classified as Medium 60/100 (`bullying-harassment`).
- **Retest Result**: **RESOLVED / PASS**. Ingested text returned:
  ```json
  {
    "risk_score": 12,
    "risk_level": "Low",
    "pattern_type": "neutral",
    "confidence": 0.946,
    "alert_id": null
  }
  ```
  Classified as Low (12/100) neutral with zero alert created.

---

## New Issues

### ISSUE-006: Settings Page `<select>` Dropdown Causes Minor Horizontal Overflow at 390px Viewport

- **Severity**: Low
- **Route or API endpoint**: `/settings` (Frontend UI)
- **Preconditions**: Mobile screen viewport set to 390px (e.g. iPhone 12/13/14 Pro width)
- **Exact reproduction steps**:
  1. Open browser and resize window to 390x844.
  2. Navigate to `http://127.0.0.1:5173/settings`.
  3. Inspect page horizontal scroll via `document.documentElement.scrollWidth > window.innerWidth`.
- **Expected behavior**: Page width conforms to `376px` (or `390px`) with `scrollWidth <= innerWidth` without horizontal scrollbar.
- **Actual behavior**: `scrollWidth` is `442px` while `innerWidth` is `376px`. The `<select>` element inside the demo access token / retention row exceeds the container padding slightly.
- **Screenshot / console evidence**:
  - `hasOverflow: true` on `/settings` at 390px.
  - Overflowing element: `SELECT` element with options inside `.setting-row`.
- **Repeatability**: 100% repeatable at viewports <= 390px on `/settings`.
- **Suggested area to investigate**: Add `max-width: 100%` and `box-sizing: border-box` to `select` elements inside `.settings-layout .setting-row select` in `src/styles.css`.

---

### ISSUE-007: IndicBERT Held-Out Benchmark Misses Coercive Threat in Malayalam Script (False Negative)

- **Severity**: Medium (Model accuracy / domain limitation)
- **Route or API endpoint**: `python -m backend.ml.evaluate --mode indicbert` / `POST /api/messages/ingest`
- **Preconditions**: Active detector set to `IndicBERTv2 · trained head`
- **Exact reproduction steps**:
  1. Evaluate held-out synthetic test set.
  2. Input text in Malayalam script: `"അനുസരിച്ചില്ലെങ്കിൽ നിന്റെ ഫോട്ടോകൾ കൂട്ടുകാർക്ക് അയച്ചു കൊടുക്കും."`
     (Meaning: "If you do not obey, your photos will be sent to your friends.")
- **Expected behavior**: Classified as `High` risk / `grooming-coercive-language`.
- **Actual behavior**: Classified as `Low` risk (12/100) / `neutral`.
- **Console error / evaluation report evidence**:
  ```json
  {
    "language": "Malayalam",
    "text": "അനുസരിച്ചില്ലെങ്കിൽ നിന്റെ ഫോട്ടോകൾ കൂട്ടുകാർക്ക് അയച്ചു കൊടുക്കും.",
    "expected": "grooming-coercive-language",
    "predicted": "neutral"
  }
  ```
- **Repeatability**: 100% repeatable in held-out benchmark evaluation.
- **Suggested area to investigate**: The synthetic training set (`backend/ml/data.py`) contains Manglish (Romanized Malayalam) and Hindi/English coercion, but lacks sufficient native Malayalam script (`മലയാളം`) coercive blackmail examples in the classifier head training set.

---

## Model observations

### Held-Out Evaluation Benchmark (30 Synthetic Scenarios)

#### 1. IndicBERTv2 + Retrained Supervised Head
- **Overall Accuracy**: **28/30 correct (93.3% accuracy)** (Significant improvement over previous 76.7%)
- **Macro Average**:
  - Precision: **0.948**
  - Recall: **0.920**
  - F1-Score: **0.928**
- **Weighted Average**:
  - Precision: **0.942**
  - Recall: **0.933**
  - F1-Score: **0.932**
- **Per-Category Performance**:
  - `neutral`: Precision 0.909, Recall 1.000, F1 0.952 (10 samples)
  - `bullying-harassment`: Precision 0.833, Recall 1.000, F1 0.909 (5 samples)
  - `grooming-trust-building`: Precision 1.000, Recall 1.000, F1 1.000 (5 samples)
  - `grooming-isolation-request`: Precision 1.000, Recall 0.800, F1 0.889 (5 samples)
  - `grooming-coercive-language`: Precision 1.000, Recall 0.800, F1 0.889 (5 samples)
- **Per-Language Accuracy**:
  - **English**: **100.0%** (8/8)
  - **Hindi**: **100.0%** (6/6)
  - **Manglish**: **100.0%** (5/5)
  - **Hinglish**: **83.3%** (5/6) (1 misclassification: isolation predicted as harassment)
  - **Malayalam**: **80.0%** (4/5) (1 false negative on native Malayalam coercion)

#### 2. TF-IDF Fallback Baseline Classifier
- **Overall Accuracy**: **29/30 correct (96.7% accuracy)**, Macro F1: **0.968**
- **Per-Language Accuracy**: English 87.5% (7/8), Hindi 100.0%, Hinglish 100.0%, Malayalam 100.0%, Manglish 100.0%.
- Single error: `"Unless you obey me, your private pictures go to the entire class."` predicted as neutral.

### Qualitative Observations & Score Calibration
1. **False Positive Mitigation**: The retrained classifier head with 111 synthetic examples successfully eliminated false positives on protective safety advice, quoted reports, friendly gaming slang, and explicit negations.
2. **Review Priority vs Probability**: The numeric risk score (e.g. 12, 43, 60, 78, 80, 85) is an **illustrative review priority score**, not a calibrated statistical probability of harm. A score of 12 (Low) indicates no known high-concern pattern was detected, but does NOT certify that a conversation is unconditionally safe.
3. **Cross-Turn Context Reasoning**: Multi-turn signals operate robustly across message turns:
   - Trust-building followed by secrecy request elevates the score from 43 to 80 (High).
   - Harassment repeated within 24 hours adds +18 points, escalating score from 60 to 78 (High).
   - Signals expire after 24 hours and are strictly scoped to the same child and source metadata.

---

## Untested / blocked

1. **Real Telephony & Public Helplines**: The emergency links `tel:112` and `tel:1098` were inspected in the DOM and confirmed to have valid telephone URIs, but real phone calls were not placed to public authorities or emergency services.
2. **Real Child / Youth Data**: All evaluations and testing flows used synthetic, curated benchmark datasets. No real minors' personal messages or data were processed.
3. **External NGO Aid Endpoint**: The aid dispatch channel operates in `simulated` mode (`Simulated Child Helpline Endpoint`), which produces valid internal simulated receipts. Live external HTTP integration with government or third-party NGO APIs was not connected.
4. **Live PostgreSQL Cluster**: SQLAlchemy models were verified to compile and validate against PostgreSQL dialect specifications via automated tests (`test_models_compile_for_postgres`), but testing was performed on local SQLite.

---

## Changes made by tester

- **Zero Changes to Production Code**: No application source files (`src/`, `backend/`), training data (`backend/ml/data.py`), or production dependencies were modified during the testing run.
- **Test Artifacts Created**:
  - Created test scripts in `scratch/`:
    - `scratch/test_v2_part1.py`
    - `scratch/test_v2_comprehensive_api.py`
    - `scratch/test_db_and_retention.py`
    - `scratch/test_auth_isolated.py`
    - `scratch/run_isolated_auth.py`
  - Created isolated SQLite test databases in `scratch/` (`scratch/isolated_test.db`, `scratch/auth_test.db`), keeping `digital_guardrails.db` preserved.
  - Browser interaction recordings and screenshots captured automatically by the browser subagent in the IDE brain artifacts directory.
