# UI and release review

The latest account and casework UI uses a shared blue-gray palette, larger login
controls, and plain-language headings. Credential autofill and claims of real
dispatch or established legal compliance were removed. Case referral simulations
remain labeled as simulations.

## Security fixes

- Unknown accounts cannot sign in; `demo123` no longer bypasses password checks.
- Casework reads and updates require an NGO session and enforce the account's area.
- Hosted registration remains available for the configured prototype account flow; organization verification is still a deployment responsibility.
- Hosted guardian login is limited to the configured guardian username.
- Synthetic case seeding is opt-in and disabled on hosted instances.
- Restarting preserves the guardian's snippet preference.

## Required before real-world use

This remains a prototype, not a production-certified safeguarding service.
Guardian records still belong to a shared workspace. Account ownership must be
enforced throughout ingestion, alerts, settings, and retention before allowing
multiple guardian accounts. Existing NGO accounts need administrator verification;
public self-registration does not establish an organization's legitimacy.

Add login throttling, account recovery, audit records, verified aid partnerships,
operational incident procedures, and independent multilingual model evaluation.
Review database migrations, backups, report retention and access logs. The hosted
classifier is the disclosed fallback, not IndicBERT. Confirm all changes in a
staging deployment before collecting sensitive real reports.

No live deployment was performed as part of this review.
