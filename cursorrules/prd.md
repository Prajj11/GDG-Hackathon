# Product Requirements Document (PRD)
## Digital Guardrails — AI-Powered Child Safety Monitoring System

**Track:** Bal Suraksha (Track 2) — Child Safety, Protection & Well-being
**Event:** Bit N Build Hackathon
**Version:** 1.0
**Date:** September 11, 2026

---

## 1. Executive Summary

Digital Guardrails is an AI/ML-powered system that detects online grooming and cyberbullying patterns in real time, with a specific focus on regional Indian languages and code-mixed text (e.g., Hinglish, Manglish). It flags risky conversations to parents/guardians via a dashboard without exposing full private conversation content, striking a balance between child protection and privacy.

---

## 2. Problem Statement

### 2.1 The Core Problem
Children and adolescents in India are increasingly active on chat apps, gaming platforms, and social media. This exposes them to two major digital risks:

1. **Online grooming** — predators building trust with children over time, isolating them from guardians, and escalating toward exploitation.
2. **Cyberbullying** — harassment, humiliation, or threats delivered through digital text, often invisible to parents/teachers.

### 2.2 Why Existing Solutions Fall Short
- Most moderation/parental-control tools are **keyword-based** and easily bypassed (typos, slang, emojis, code words).
- They are built and trained predominantly for **English**, missing the reality that most Indian children communicate in **Hindi, regional languages, or code-mixed text**.
- Detection tends to be **reactive** (after harm is reported) rather than **proactive** (flagging risk as it develops).
- Parents and guardians, especially in smaller towns, often lack **awareness or tools** to identify early warning signs of grooming.

### 2.3 Who Is Affected
- Children and adolescents (roughly age 8–17) active on messaging/gaming/social platforms.
- Parents and guardians who want visibility without invasive surveillance.
- Schools and child-welfare NGOs who need early signals to intervene.

### 2.4 Supporting Evidence (to cite in submission)
- NCRB and child helpline (1098 / CHILDLINE) data consistently show rising cases of online child exploitation and cyberbullying in India year over year.
- India's multilingual digital population means a large share of at-risk conversations occur outside English-only moderation coverage.
*(Team should insert the latest specific stats/citations here before submission.)*

---

## 3. Goals & Non-Goals

### 3.1 Goals (Hackathon Scope)
- Detect grooming/cyberbullying **conversation patterns** (not just keywords) in text.
- Support at least **2–3 languages** including one Indian regional language, plus code-mixed text.
- Generate a **risk score** and flag alert for suspicious conversations.
- Provide a **parent/guardian dashboard** showing flagged alerts with minimal exposed content.
- Demonstrate a working end-to-end prototype (frontend + backend + ML inference + DB).

### 3.2 Non-Goals (Out of Scope for Hackathon)
- Full production-scale deployment or integration with real platforms (WhatsApp, Instagram, etc.) — instead, simulate ingestion via a demo chat interface or uploaded/synced chat logs.
- Legal/law-enforcement reporting integration (mentioned as future scope, not built).
- Voice/audio or image-based grooming detection (text-only for MVP).
- Multi-tenant enterprise administration.

---

## 4. User Personas

| Persona | Description | Needs |
|---|---|---|
| **Parent/Guardian** | Wants to protect their child online without reading every message | Simple dashboard, risk alerts, trust that privacy is respected |
| **Child/Teen (indirect user)** | Uses chat/gaming platforms daily | Safety without feeling surveilled or punished |
| **NGO / Child Welfare Worker** (future scope) | Needs aggregated, anonymized signals to intervene at scale | Verified reporting channel, case escalation |

---

## 5. Key Features

### 5.1 Must-Have (MVP for Hackathon)
1. **Conversation Ingestion** — demo interface to simulate incoming chat messages (manual input or sample dataset upload).
2. **Multilingual Pattern Detection Engine** — NLP model (MuRIL/IndicBERT-based) classifying messages/conversation windows for grooming or bullying risk.
3. **Risk Scoring** — numerical/categorical risk level (Low/Medium/High) per conversation.
4. **Alert Dashboard** — React + Tailwind UI showing flagged conversations, risk scores, and minimal necessary context (not full raw chat logs).
5. **Alert Detail View** — shows *why* something was flagged (pattern type: trust-building, isolation request, escalating personal questions, coercive language, etc.) without exposing entire private conversation.

### 5.2 Should-Have (if time permits)
6. Real-time updates via WebSocket instead of polling/refresh.
7. Basic authentication for parent dashboard login.
8. Historical trend view (risk alerts over time).

### 5.3 Could-Have (Future Scope, mention in Slide 6)
9. Direct integration with messaging platform APIs (WhatsApp Business API, gaming SDKs).
10. Verified reporting channel connecting to child helplines/NGOs (ties into "Support Ecosystems" pillar).
11. On-device inference for full privacy preservation.
12. Expansion to more Indian languages and dialects.

---

## 6. Privacy & Ethical Considerations
- The system should flag **patterns and risk scores**, not expose full conversation transcripts to parents by default — reduces surveillance overreach and preserves child trust.
- Only **metadata and flagged snippets** relevant to the risk pattern are stored, not entire chat histories.
- Clearly communicate in the pitch: this is a **safety net**, not a surveillance tool — framing matters for judges and real-world adoption.
- Be prepared to address false positives/negatives directly in the pitch.

---

## 7. Success Metrics (for demo/judging)
- Model correctly flags a set of curated/synthetic grooming and bullying examples across at least 2 languages.
- Dashboard clearly displays risk scores and reasoning in an intuitive, non-technical way.
- End-to-end flow works live in the demo video: message input → detection → dashboard alert.

---

## 8. Constraints
- 48-hour build window.
- Must produce: PPT (6-slide structure), public GitHub repo, working prototype link, 3-minute demo video.
- Team must choose exactly one track (Bal Suraksha selected).

---

## 9. Assumptions
- A small labeled or synthetic dataset of grooming/bullying conversation examples will be created or sourced for demo purposes, since no real private chat data can/should be used.
- SQLite is sufficient for the hackathon demo; architecture will be designed to allow migration to PostgreSQL later.
