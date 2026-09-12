# Codex verification — UI repair and local prototype

Date: September 12, 2026. User explicitly authorized Codex to resume testing.

## Result

The reported globally disoriented UI was reproduced and repaired. Production build, formatting, and all 18 API integration tests pass. Browser checks cover guardian and youth routes across desktop, tablet, and mobile sizes. This is local prototype verification, not certification of real-world safeguarding accuracy.

## Root cause and changes

`Support.tsx` imported its own stylesheet before `main.tsx` loaded the main Tailwind stylesheet. That stylesheet declared the `components` cascade layer first. Tailwind's later `base` layer then took precedence and reset component margins and padding. The dashboard lost its sidebar offset and spacing throughout the product.

The app now has one CSS entry point: `styles.css` imports Tailwind first, then `support.css`. Removed the separate import in `Support.tsx` and the circular stylesheet reference. This establishes consistent layer ordering in both development and production. Also enabled sidebar vertical scrolling for short viewports and restored the mobile filter button's accessible name.

Before repair, browser-computed `.main-shell` margin, `.brand` margin, navigation padding, and main padding were all zero. After repair, the production desktop page reports a 238px sidebar offset, brand margin `36px 27px 48px`, and navigation padding `14px 12px`. Screenshots before and after were visually inspected in this task.

## Executed checks

| Check | Result |
|---|---|
| `npm run build` | PASS, including TypeScript compilation; final rebuild after accessibility/sidebar changes passed |
| `npm run format:check` | PASS |
| `.venv/Scripts/python.exe -m pytest -q` | PASS: 18 tests, including four new anonymous-support integration tests |
| Development route dimensions | PASS: nine routes at 1440, 768, 390, and 320px; no horizontal overflow detected |
| Production preview | PASS: desktop computed spacing, mobile alert detail, demo analysis, and youth context handover |
| Mobile visual inspection | PASS: Settings retention layout, support step two, immediate-help panel, sidebar navigation, and alert detail |
| Anonymous report UI | PASS: empty optional message accepted, simulated receipt shown, receipt reload works |
| Immediate help | PASS: opens without submitting; 112/1098 links present, focus moves to heading, no horizontal overflow; no real calls placed |
| Detection handover | PASS: trust-building sample produces Medium 43/100, support receives the matching optional suggested context |
| Browser console | No error entries returned for the final test tab |

The nine routes in the viewport sweep were `/`, `/settings`, `/trends`, `/demo`, `/resources`, `/help`, `/help/report`, `/help/status`, and `/login`. Alert detail and generated report confirmation were checked separately at 390px. Temporary viewport overrides were reset at the end.

The new tests in `backend/tests/test_support.py` exercise receipt-secret hashing and access isolation, idempotent submission, explicit linking consent and alert matching, foreign-key nulling after alert deletion, simulated routing failure/retry, note bounds, rejection of unexpected fields, and seven-day expiry. They use disposable SQLite databases and the baseline detector. Browser demo analysis used IndicBERT.

## Model regression results

Both modes were evaluated against the existing 30-case known synthetic regression set using the 128-example training revision (`ccb045db4fc1e55f2102afca2ccd396b366843262274a2bc21ca63496092ac15`).

| Detector | Correct | Macro F1 | Remaining category error |
|---|---:|---:|---|
| IndicBERTv2 | 29/30 | 0.960 | Hinglish isolation classified as harassment |
| TF-IDF fallback | 29/30 | 0.960 | Malayalam isolation classified as coercion |

The previously reported Malayalam coercion false negative is no longer in the IndicBERT errors. Evaluation outputs are in ignored `scratch/codex-evaluation-indicbert.json` and `scratch/codex-evaluation-baseline.json`. The set contains one exact training overlap and has informed development; these scores are not an independent accuracy estimate. No further model training or tuning was performed during this UI repair.

## Limits and environment

The build emits a non-blocking bundle-size warning. Pytest reports two dependency deprecation warnings. No real helpline calls, external aid routing, deployment, or live PostgreSQL testing were performed. This pass does not claim exhaustive keyboard, screen-reader, reduced-motion, or every-browser coverage.

The local API was started because it was unavailable at initial browser inspection. Dev UI: `http://127.0.0.1:5173/`. API: `http://127.0.0.1:8000/`. Production preview was used on port 4173 for verification. Browser testing created one empty synthetic anonymous report and one synthetic trust-building alert; existing preferences and records were preserved.
