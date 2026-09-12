# Digital Guardrails — Test Report

Date: 2026-09-11
Tester / agent: Antigravity AI
OS / browser / viewport sizes: Windows 11 / Chromium / 1440x900, 1024x768, 768x1024, 390x844, 320x700
Source commit (or working tree snapshot): Working tree snapshot (`C:\Users\naren\Videos\GDG-Hackathon`)
API model / mode: `IndicBERTv2 · trained head` (`AI4Bharat/IndicBERTv2-MLM-only`, revision `8598f13f...`) + fallback `TF-IDF · fallback classifier`
Database: Existing synthetic demo SQLite database (`digital_guardrails.db`) + isolated scratch test databases

## Overall result

PARTIAL

> [!NOTE]
> **Summary**: All core application features, frontend build, formatting, API endpoints, privacy redaction rules, cross-message sequence escalation, mobile responsive layout fixes, keyboard navigation, and accessibility standards passed verification. The `PARTIAL` rating is assigned because:
> 1. Default `pytest` execution fails on Windows with a `PermissionError` on standard `temp` directory unless explicit `--basetemp` parameters are passed.
> 2. The primary IndicBERTv2 classification model exhibits false positive misclassifications on novel inputs involving harmless safety advice, quoted threats, negation, and gaming slang.

---

## Commands and results

| Check | Command or steps | Result | Evidence |
|---|---|---|---|
| Build | `npm run build` | PASS | `vite build` generated static bundle (`dist/`) cleanly in 3.54s without TypeScript or Rollup errors. |
| Formatting | `npm run format:check` | PASS | Prettier checked `src` and `vite.config.ts`; all files match style guide. |
| API tests | `.venv/Scripts/python.exe -m pytest backend/tests -q --tb=short --basetemp="scratch/pytest_tmp"` | PASS | 14/14 tests passed in 2.93s when explicitly setting `--basetemp`. (Default temp path fails with Windows `PermissionError`). |
| IndicBERT evaluation | `.venv/Scripts/python.exe -m backend.ml.evaluate --mode indicbert --output scratch/evaluation-indicbert.json` | PASS | Held-out 30 synthetic scenarios: 23/30 correct (76.7% accuracy, Macro F1 0.778). |
| Fallback evaluation | `.venv/Scripts/python.exe -m backend.ml.evaluate --mode baseline --output scratch/evaluation-baseline.json` | PASS | Held-out 30 synthetic scenarios: 26/30 correct (86.7% accuracy, Macro F1 0.880). |

---

## Browser scenarios

| Scenario | Input / language / conversation | Expected | Actual | Pass/fail |
|---|---|---|---|---|
| Trust → secrecy | Hinglish: Trust building -> Secrecy in same conversation | Initial Medium 43/100; Escalates to High 80/100 with sequence explanation | Initial Medium 43 (grooming-trust-building); Escalated to High 80 (grooming-isolation-request) with explanation: *"Earlier messages showed trust-building, followed now by secrecy. This change increases concern."* | PASS |
| Repeated harassment | Malayalam: Harassment submitted twice in same conversation | Initial Medium 60/100; Escalates to High 78/100 on second submission | Initial Medium 60 (bullying-harassment); Escalated to High 78 on second send with explanation: *"A similar harassment signal was detected earlier in this conversation within 24 hours."* | PASS |
| Neutral input | English, Hindi, Malayalam, Hinglish, Manglish neutral chat | Low risk (12/100, neutral); No alert created; Message text cleared | Low risk (12/100, neutral); No alert saved in DB; Input field cleared; Message counter incremented | PASS |
| Review persistence | Mark alert as reviewed on detail view -> return to Overview & refresh | Review status updates to "Reviewed"; Persists across browser reload | State changed to `reviewed: true`; Card badge changed to "Reviewed"; Persisted after F5 refresh | PASS |
| Risk + child filters | Filter alerts on Overview page by risk level & review status | Cards filter dynamically; Summary counts match DB records | Filter buttons ("Needs review", "Reviewed", "High risk") update list correctly; Empty state shown when no match | PASS |
| Retention / excerpts | Synthetic text with email, phone number, and URL | Excerpt redacted; Turning snippets off purges existing excerpts | Phone (`[phone]`), Email (`[email]`), Link (`[link]`) redacted in snippet; Toggling snippets off in Settings cleared DB snippets permanently | PASS |
| Mobile overview overflow | 390px and 320px viewport widths on `/` (Overview) | No horizontal scrolling or overflow; Cards wrap cleanly | `hasHorizontalOverflow: false` on both 390px and 320px; Single-column layout renders cleanly | PASS |
| Other responsive routes | 1440, 1024, 768, 390, 320px on `/demo`, `/trends`, `/settings`, `/resources` | Clean responsive layout across all breakpoints | Zero horizontal overflow detected across all 5 viewports on all 5 routes | PASS |
| Keyboard / reduced motion | Tab key navigation; `prefers-reduced-motion` media query | Visible focus rings; 1 magnetic CTA per route; Motion disabled on reduced motion | Focus rings visible on skip link, nav items, buttons; Exactly 1 `.magnetic` CTA per screen; Animations/magnetism disabled under `prefers-reduced-motion` | PASS |
| Offline / authorization errors | `DG_HOSTED=true` mode test | Short access token rejects startup; Invalid token returns 401 | Startup rejected with exit code 3 for token <24 chars; HTTP 401 returned for requests lacking valid Bearer header | PASS |

---

## Issues

### ISSUE-001: Default Pytest Execution Fails with PermissionError on Windows

- **Severity**: Medium
- **Route or API endpoint**: Backend Test Suite (`pytest backend/tests`)
- **Preconditions**: Windows operating system with standard user environment
- **Exact reproduction steps**:
  1. Open PowerShell terminal in repository root.
  2. Run `.venv/Scripts/python.exe -m pytest backend/tests -q --tb=short`
- **Expected behavior**: Tests execute using system temp directory without permission errors.
- **Actual behavior**: `PermissionError: [WinError 5] Access is denied: 'C:\\Users\\naren\\AppData\\Local\\Temp\\pytest-of-naren'`
- **Screenshot / console error**:
  ```
  E PermissionError: [WinError 5] Access is denied: 'C:\\Users\\naren\\AppData\\Local\\Temp\\pytest-of-naren'
  PytestCacheWarning: could not create cache path C:\Users\naren\Videos\GDG-Hackathon\.pytest_cache\v\cache\nodeids
  ```
- **Repeatability**: 100% repeatable on Windows without explicit temp flags.
- **Suggested area to investigate**: Update `pytest.ini` or test runner docs to specify `--basetemp` and `-o cache_dir` within workspace.

---

### ISSUE-002: IndicBERT Classifier Misclassifies Harmless Safety Advice as Grooming Isolation

- **Severity**: Medium
- **Route or API endpoint**: `POST /api/messages/ingest`
- **Preconditions**: Active detector set to `IndicBERTv2 · trained head`
- **Exact reproduction steps**:
  1. Submit Hinglish message: `"Teacher ne bola koi photo maange toh mat bhejna aur parents ko batana."`
- **Synthetic input**: Safety advice teaching children not to share photos.
- **Expected behavior**: Classified as `Low` risk / `neutral` (score < 40).
- **Actual behavior**: Classified as `Medium` risk (66/100) / `grooming-isolation-request`.
- **Screenshot / console error**:
  ```json
  {
    "risk_score": 66,
    "risk_level": "Medium",
    "pattern_type": "grooming-isolation-request",
    "explanation": "Language suggests isolating the child from trusted adults..."
  }
  ```
- **Repeatability**: 100%
- **Suggested area to investigate**: Model training dataset (`backend/ml/data.py`) lacks negative/educational samples containing protective advice keywords ("teacher", "parents", "don't send").

---

### ISSUE-003: IndicBERT Model Ignores Negation Signals

- **Severity**: Medium
- **Route or API endpoint**: `POST /api/messages/ingest`
- **Preconditions**: Active detector set to `IndicBERTv2 · trained head`
- **Exact reproduction steps**:
  1. Submit English message: `"I am not threatening you and I do not want your private details."`
- **Synthetic input**: Explicit statement of non-threat.
- **Expected behavior**: Classified as `Low` risk / `neutral`.
- **Actual behavior**: Classified as `High` risk (85/100) / `grooming-coercive-language`.
- **Repeatability**: 100%
- **Suggested area to investigate**: Logistic regression head over frozen IndicBERT embeddings focuses on trigger words ("threatening", "private details") without semantic negation context.

---

### ISSUE-004: Quoted Reports of Threatening Messages Trigger False Positives

- **Severity**: Low
- **Route or API endpoint**: `POST /api/messages/ingest`
- **Preconditions**: Active detector set to `IndicBERTv2 · trained head`
- **Exact reproduction steps**:
  1. Submit English message: `"My friend said someone messaged him: 'Send your photo or I will report you'."`
- **Synthetic input**: Child reporting a threat to a friend.
- **Expected behavior**: Classified as `Low` risk / `neutral`.
- **Actual behavior**: Classified as `High` risk (85/100) / `grooming-coercive-language`.
- **Repeatability**: 100%
- **Suggested area to investigate**: Add quoted reporting patterns to training synthetic dataset.

---

### ISSUE-005: Gaming Metaphors & Slang Misclassified as Bullying / Harassment

- **Severity**: Low
- **Route or API endpoint**: `POST /api/messages/ingest`
- **Preconditions**: Active detector set to `IndicBERTv2 · trained head`
- **Exact reproduction steps**:
  1. Submit English message: `"That game was killer! You completely destroyed me in that match."`
- **Synthetic input**: Harmless friendly gaming chatter.
- **Expected behavior**: Classified as `Low` risk / `neutral`.
- **Actual behavior**: Classified as `Medium` risk (60/100) / `bullying-harassment`.
- **Repeatability**: 100%
- **Suggested area to investigate**: Include gaming slang and sports metaphors in neutral dataset examples.

---

## Model observations

### Held-Out Evaluation Benchmark (30 Synthetic Scenarios)
- **IndicBERTv2 + Supervised Head**: 23/30 correct (**76.7% accuracy**, Macro F1: **0.778**)
- **TF-IDF + Logistic Regression Fallback**: 26/30 correct (**86.7% accuracy**, Macro F1: **0.880**)

### Per-Language Held-Out Accuracy (IndicBERTv2)
- **English**: 62.5% (5/8)
- **Hindi**: 83.3% (5/6)
- **Hinglish**: 50.0% (3/6)
- **Malayalam**: 100.0% (5/5)
- **Manglish**: 100.0% (5/5)

### Key Observations
1. **Training Samples vs Novel Inputs**: Training samples (102 synthetic examples) achieve 100% classification. However, novel unseen inputs containing negation ("am not"), safety advice ("teacher ne bola"), quoted reports, or gaming metaphors ("killer", "destroyed") reliably trigger false positives.
2. **Score Interpretation**: Scores (e.g. 12, 43, 60, 80, 85) represent **illustrative review-priority levels**, not calibrated statistical probabilities of real-world harm. Low confidence caps initial scores at 49.
3. **Sequence Escalation**: Cross-message logic correctly elevates risk score when trust-building is followed by secrecy (+37 points) or when harassment is repeated within 24 hours (+18 points).

---

## Untested / blocked

- **Live PostgreSQL Production Setup**: PostgreSQL connection string mapping (`postgresql+psycopg://...`) exists in ORM configuration, but live testing was performed exclusively on SQLite.
- **Background Retention Cron**: Data retention cleanup is executed on API request startup/invocation rather than a background daemon thread.

---

## Changes made by tester

- **Application Code & Training Data**: Zero changes made. No source files or dataset files modified.
- **Database & Model Checkpoints**: Preserved `digital_guardrails.db` and IndicBERT model checkpoints intact.
- **Test Automation Artifacts**: Generated temporary test scripts (`scratch/test_comprehensive.py`, `scratch/test_hosted_token.py`, `scratch/test_settings_retention.py`) and result outputs in `scratch/`.
