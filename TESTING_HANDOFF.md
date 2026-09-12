# Antigravity testing handoff — Digital Guardrails

Latest status: the user reauthorized Codex testing. On September 12, 2026, Codex reproduced and fixed the global CSS layer-order regression, ran the build and formatting checks, passed 18 API tests, and verified responsive UI and the support flow. See [CODEX_TEST_REPORT.md](CODEX_TEST_REPORT.md). The earlier instructions to avoid Codex testing and pending-retest notes below are historical.

## Current follow-up after the v2 report

`ANTIGRAVITY_V2_TEST_REPORT.md` records passing core v2 flows, build, formatting, and 14 API tests, with ISSUE-001 through ISSUE-005 resolved. Codex has read that report and made the following **unverified follow-up changes**; the earlier handoff sections below are retained as historical/full-regression instructions.

- **ISSUE-006:** Settings rows now wrap, text columns can shrink, and the retention selector is bounded to its container. Retest `/settings` at 320, 360, and 390px and 200% zoom, including retention, excerpt toggle, and long explanatory text. Confirm no horizontal scrolling and controls remain usable.
- **ISSUE-007:** Expanded the training set from 111 to 128 examples, including six native Malayalam coercion scenarios and three benign Malayalam contrasts, plus English coercion and Hinglish isolation/privacy contexts. The actual failing evaluation sentences were not added to training. IndicBERT's head was retrained; no predictions or evaluation were run by Codex. Retest the reported Malayalam false negative, the remaining Hinglish category error, and the fallback's English false negative. **Do not mark these fixed merely because training finished.**
- Recheck the four previously resolved benign messages and ordinary native Malayalam conversation/sharing/advice. Add independently authored, fluent-speaker-reviewed scenarios: direct vs quoted threats, coercion expressed through demands and consequences, secrecy vs benign privacy, and malicious requests wrapped in negation or friendly wording. Keep these new cases out of training and report them separately.
- The prior 28/30 IndicBERT and 29/30 fallback scores are historical. The 30-case set is a **known synthetic regression set**, not fully held-out: one Hinglish safety-advice case is also in training, and development has used the known cases. `evaluate.py` now reports this limitation, exact training overlap, and source dataset provenance. Do not claim generalization from this set.
- Restart the local API if needed to load the new trained head. Run the frontend build, formatting check, existing API tests, both model evaluations, and the focused UI/model retests yourself. Preserve the existing v2 report and save findings to **ANTIGRAVITY_V2_RETEST_REPORT.md**; include model artifact metadata and clearly separate regressions from newly authored cases.

Codex has not run tests, builds, type checks, inference checks, evaluations, or browser QA for this follow-up. Training and source formatting are implementation work only. Keep all activity local and use synthetic data.

## V2 priority: merged support flow (new, unverified)

The project now includes **Digital Guardrails + Support Ecosystems**. Codex implemented the following changes without running tests, builds, type checks, evaluations, or browser QA. Test these additions first, then run the existing guardian/ML regression sections below. Preserve `ANTIGRAVITY_TEST_REPORT.md` as prior evidence; write the new findings to **ANTIGRAVITY_V2_TEST_REPORT.md**. Do not edit implementation files or train models to match test inputs.

Install updated backend requirements and restart the API before testing; new dependencies are python-jose and passlib. The current workspace already has them installed. Use a separate temporary database/process for destructive, auth, retention, and provider-failure scenarios. Do not delete the existing demo database, call real helplines, send real messages, or deploy anything.

### V2 acceptance flows

1. Open `/help` in a fresh browser context with no guardian token. Confirm a distinct teal/lavender support interface, no login/name/email/phone requirement, and no requests to guardian alerts/summary/settings. `/support` should redirect to `/help`.
2. Start a report, choose any starting option, continue, leave text empty, choose urgency, submit. Expect one report and one simulated aid route, confirmation **Routed · simulation only**, and explicit **no human or helpline contacted** messaging. Repeat as High urgency with no alert; support must not depend on AI approval or guardian access.
3. In `/demo`, analyze a synthetic high-risk pattern. Confirm the guardian alert still appears. Click **Open youth support** from the result. Verify an appropriate choice is suggested from the same model category; no raw text, snippet, guardian label, or conversation ID crosses into the portal. Change the choice to ensure the suggestion is optional.
4. Submit with the context checkbox **off**. In the database, `linked_alert_id` and `detection_context` must be null. Repeat with a new report and checkbox **on**: the signature and linked alert must match; only pattern/level should appear in `detection_context`, and the aid payload must not contain guardian IDs, receipt secrets, or chat text.
5. Open **I'm in immediate danger / Talk to someone now** at welcome, choice, details, and receipt stages. Verify 112 and 1098 appear immediately without submission/API dependency. Inspect `tel:112` and `tel:1098` links without activating real calls. Opening/closing help must preserve the draft. Check focus moves to the help heading and the state change remains calm.
6. Reload the confirmation in the same tab. Confirm receipt-authorized status loads. Reveal/save the private receipt code, then restore it in a fresh tab through `/help/status`. A wrong code, missing Bearer token, or guardian Bearer token must never retrieve the report. No unauthenticated report list should exist.
7. Use **Finish and forget this receipt**. Confirm session storage no longer contains the code, route history state contains no receipt/context secrets, and opening the old URL without a code requires recovery. Stored report should remain until retention expires; forgetting must not claim to delete it.
8. Check note length (0 and 1500 accepted; 1501 rejected by API), invalid urgency/context, malformed secrets, and unexpected identifying fields (rejected by API). Submit literal `<script>`/HTML-like synthetic text and confirm it never executes.
9. Rapid clicks and retries with the same anonymous secret must yield one report/route. After an uncertain timeout, retry should return the original report, not another one. Existing receipt tokens must not be overwritten in a way that exposes submitted text in browser storage.
10. Simulate API unavailability: preserve draft and choice, show a useful error, leave emergency numbers usable. Use an isolated test provider that raises during routing: report remains `submitted`, confirmation says pending, retry using its receipt succeeds once and creates one route. Never show `acknowledged` or imply human contact for the simulated provider.

### Privacy / expiry / authentication

- Check raw report secrets are 32 random bytes represented as 64 hex characters. The database stores only SHA-256 digests in `anonymous_token`. Raw secrets travel in POST bodies for creation and Bearer headers for status; never URL paths/queries, logs added by application code, aid payloads, or guardian API responses.
- Guardian Axios credentials must not accompany `/api/support/*` calls. Youth pages should not mount or poll guardian components. Reports contain no guardian foreign key; explicit alert linking is the only optional correlation.
- Tamper with, expire, or mismatch the 30-minute support context JWT; reject linking without storing a report. A guardian JWT must not work as a context capability, or vice versa. The child must still be able to uncheck linking and submit independently.
- Confirm guardian alert retention deletes an expired linked alert without deleting the report or violating a foreign key (`linked_alert_id` becomes null). Report status remains available to its owner until its independent seven-day expiry.
- Backdate an isolated report over seven days, trigger a report request/startup, and confirm report plus route deletion. Guardian retention/snippet preferences must not delete report text or expose it in summaries.
- Success responses for support data must have `Cache-Control: no-store`. Check API status outputs contain no report text or token digest. The UI discloses browser history/server access-log limits instead of promising network-level anonymity.
- Configure `GUARDIAN_PASSWORD_HASH`, `GUARDIAN_USERNAME`, `JWT_SECRET` in an isolated backend process per README. Verify `/login`, correct/incorrect password, Unicode usernames, JWT expiry/tampering, sign out, and protected guardian endpoints. `/help` and all normal anonymous report creation/status operations must work without guardian auth. Legacy shared demo token must not bypass configured guardian login.
- Check hosted-mode configuration fails with missing/short required keys, while keeping the test process bound to loopback. This does not authorize deployment.

### UI / accessibility / report evidence

- Test direct route loads and navigation at 360px, 390px, 768px, and 1440px, plus 200% zoom. Check long recovery codes and errors for overflow.
- Keyboard: skip link, focus on each step and immediate-help heading, native radio arrow keys, checkbox, back/change buttons, status recovery, disabled submitting state, and visible focus.
- With reduced motion enabled, no fade/lift/magnetic movement remains. Otherwise youth steps should use approximately 420ms fade/lift, 80ms choice stagger, gentle press, and one magnetic control (immediate help); ordinary choices and submit are not magnetic.
- Verify guardian alert/review/sequence flows still work and privacy text is accurate. Do not treat previous build/ML scores as evidence that v2 passed.
- Run `npm run build`, `npm run format:check`, and `.venv/Scripts/python.exe -m pytest`. For new API test fixtures, reload `backend.auth` and `backend.support` after changing environment and reloading `backend.database`, or prefer separate processes; auth config is read at module import.
- Also retest original ISSUE-001 through ISSUE-005 and unseen malicious variations of benign phrases. Re-run evaluation only in Antigravity; distinguish prior training examples from independent evaluation.
- For each issue provide severity, reproduction, expected/actual, exact request/status/response (redact receipt secrets and credentials), browser console evidence, and screenshots when useful. Report passed/failed/blocked separately and identify model mode, environment, and remaining limitations. Keep generated test data/evidence under ignored `scratch/` where practical.

Do not call real emergency numbers or send data to NGOs/authorities. The only delivered routing implementation is simulated; Physical-Digital Link remains future scope.

## Instructions for the tester

Test the existing implementation and produce a report. Do not silently change application code, alter training examples to fit evaluation cases, deploy the application, or use any real child's messages. Use synthetic inputs only. Report issues with reproduction steps, expected behavior, actual behavior, and evidence.

The user requested that Codex stop testing and delegate verification to Antigravity. No new tests or browser checks have been run after that instruction. After Antigravity's first report, Codex made source fixes for the reported Windows pytest temp/cache issue and IndicBERT false positives. Those follow-up fixes are **unverified by Codex** and should be retested in Antigravity.

Keep the application local. The frontend should run at `http://127.0.0.1:5173/` and the API at `http://127.0.0.1:8000/`. Both were left running. If browser changes appear stale, hard-refresh or restart the local Vite server; do not assume hot reload applied the final CSS. The browser viewport was temporarily changed during earlier checks; use explicit desktop/mobile sizes in your own run.

## Existing evidence, not a substitute for your run

- The production frontend build previously passed.
- 14 API tests previously passed inside the normal workspace environment.
- A separate elevated test run encountered Windows permissions on pytest's temporary directory; the normal run passed. Do not confuse the environmental error with a product assertion failure.
- IndicBERTv2 downloaded successfully. Its classifier head has now been retrained on 111 synthetic examples after adding neutral safety-advice, negation, quoted-report, and gaming-slang samples.
- Browser interaction previously demonstrated trust → secrecy escalation, Hindi coercion, Malayalam harassment, repeated-harassment escalation, neutral messages producing no alert, review persistence, and alert filtering.
- The last mobile check found horizontal overflow. Source now sets zero minimum widths on grid children and uses `minmax(0, 1fr)` in single-column layouts. **Verify this fix first.**
- Previous small held-out synthetic evaluation: IndicBERTv2 23/30 correct (macro F1 0.778), fallback 26/30 (macro F1 0.880). Those numbers predate the latest false-positive fixes and should be regenerated by Antigravity before being treated as current.

## 1. Startup, build, and model identity

From the repository root:

```powershell
npm run build
npm run format:check
.venv/Scripts/python.exe -m pytest
```

The final small JSX change may require formatting; report formatting findings separately from runtime failures.

If the servers need restarting, use two terminals:

```powershell
# API
.venv/Scripts/python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
# Frontend, in the other terminal
npm run dev
```

If the virtual environment is absent, follow README.md. Do not overwrite a running server or delete the existing demo database just to establish a test fixture.

Check:

- `/api/health` returns `status: ok`, `model_kind: indicbert`, and a model label identifying IndicBERTv2.
- UI footer and demo result identify the same model.
- Missing model artifacts with `DETECTOR=indicbert` must fail visibly; `DETECTOR=baseline` must explicitly identify the fallback. Run alternative-mode checks in an isolated process/database without modifying or moving the existing checkpoint.
- Directly opening each route works: `/`, `/demo`, `/trends`, `/settings`, `/resources`, and a real `/alerts/{id}`.
- Invalid alert IDs show a useful error rather than a blank screen.

## 2. Main demonstration flow

Use fresh conversations so previous sample signals cannot affect results.

1. Open Demo panel → Hinglish → Trust-building → Analyze message.
   - Expected: Medium, 43/100; trust-building category; short explanation; an alert link; input cleared.
2. Stay in the same conversation. Choose Secrecy request → Analyze message.
   - Expected: High, 80/100; sequence escalation explanation; a new guardian alert.
3. Open that alert.
   - Expected: only a short flagged excerpt, score, explanation, next steps, and model attribution. No full conversation history.
4. Mark reviewed, return to Overview, refresh, and reload the page.
   - Expected: review status and summary remain consistent with the database.
5. Start a new conversation → Malayalam → Harassment. Submit the sample twice.
   - Expected: Medium 60, then High 78 with a repetition explanation.
6. Start a new conversation → Everyday chat.
   - Expected: Low, neutral; no alert record or message text retained; analyzed-message count increases.
7. Repeat representative scenarios in English, Hindi, and Manglish.
   - Distinguish training-sample checks from new, unseen phrasing. Record misclassifications instead of assuming unseen examples must match sample accuracy.
8. Change child/source and confirm a fresh conversation starts. Prior signals must not carry across conversation IDs.

Record response times for the first request and subsequent requests. Check empty input, spaces-only input, overlong input, more than eight lines, and rapid repeated clicks. No duplicate client submission should occur while the analyze button is busy.

## 3. Dashboard and trends

- Alerts are sorted by descending concern score, then recency.
- All alerts / Needs review / Reviewed filters behave correctly.
- Risk and child filters combine correctly, including an empty-result state.
- The mobile filter icon has the accessible name `Filters`.
- Refresh does not erase data or reset review states.
- Counts agree with retained database records; reviewed high-risk alerts do not count as high-risk items awaiting review.
- Trends show the last seven UTC dates; totals and level categories agree with saved alerts.
- A fresh database shows honest empty states rather than fabricated sample statistics.
- Backend unavailability and invalid access tokens produce useful errors.

## 4. Privacy, persistence, and access

Use isolated test data for settings that delete snippets or expire records.

- Users, conversations, and alerts use SQLAlchemy models; there is no raw-chat table.
- Neutral input is absent from saved database fields.
- Conversation signals contain only categories and timestamps, bounded to twelve entries; sequence escalation ignores signals older than 24 hours.
- Snippets contain at most 140 characters plus an optional ellipsis. Verify email, phone, and URL redaction.
- Multi-line windows save only one selected flagged-line excerpt, never all lines.
- Turning excerpts off clears existing excerpts and suppresses new ones. Re-enabling does not restore cleared text.
- Changing retention to 1/7/30 days purges expired alerts when a data request or startup triggers cleanup. This is request-triggered cleanup, not a background timer.
- Conversation IDs cannot be reused with conflicting child/source metadata (HTTP 409).
- Test hosted access with `DG_HOSTED=true` in an isolated process: missing or short demo tokens must prevent startup; an incorrect bearer token must receive 401. Do not expose the service publicly.
- No API keys, tokens, `.env` files, checkpoint files, or SQLite databases are tracked in Git.

## 5. Responsive behavior, accessibility, and motion

Check 1440×1000, 1024×768, 768×1024, 390×844, and 320×700. Test with the feed populated with Hindi and Malayalam snippets.

- **No horizontal overflow on Overview**, especially from alert cards or the chart rail. Check all other routes too.
- Alert titles, labels, scores, and controls remain readable without overlaps or clipping.
- Mobile navigation opens/closes and does not leave hidden sidebar links keyboard-focusable.
- Keyboard-only use: visible focus, skip link, form labels, filter controls, review action, and navigation.
- 200% text/browser zoom remains usable.
- Risk levels and review statuses use text as well as color.
- Alerts fade/lift with stagger; controls give gentle press feedback; detail uses a clip reveal.
- Exactly one primary CTA per route has pointer magnetism. Touch and keyboard use must not depend on the effect.
- Reduced-motion preference disables animation and magnetism.
- Check browser console errors, network failures, and React warnings. The Recharts bundle-size warning from Vite is a performance note, not automatically a functional failure.

## 6. Model evaluation

```powershell
.venv/Scripts/python.exe -m backend.ml.evaluate --mode indicbert --output backend/ml/evaluation-indicbert.json
.venv/Scripts/python.exe -m backend.ml.evaluate --mode baseline --output backend/ml/evaluation-baseline.json
```

Record per-language precision/recall or the supplied report, false positives, false negatives, and any differences from the checked-in reports. Include novel neutral, quoted, negated, code-mixed, and risk-pattern examples in a separate exploratory section. Do not mix training examples into an accuracy claim. Do not imply that a numeric score is the probability of harm or that Low means safe.

Known scope limits to report accurately: frozen encoder + trained head (not full encoder fine-tuning); small synthetic dataset; no true sender/age verification; no real platform integration; one demo guardian rather than production authentication; 192-token truncation per line; no live PostgreSQL verification.

## Report format

Use TEST_REPORT_TEMPLATE.md. Prioritize reproducible functional/privacy failures over subjective polish. Include the exact test commands and environment. Do not fix failures in the report-producing run unless the user separately asks you to; Codex will use the findings for the next development pass.
