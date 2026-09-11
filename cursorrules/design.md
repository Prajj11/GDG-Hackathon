# Design Document
## Digital Guardrails — Product & UX Design

**Track:** Bal Suraksha (Track 2)
**Version:** 1.0

---

## 1. Design Philosophy

Digital Guardrails is designed around three principles:

1. **Protective, not invasive** — the product should feel like a safety net, not surveillance. Parents see risk signals and reasoning, not raw private conversations.
2. **Calm, trustworthy visual language** — this is a sensitive, emotionally charged space (child safety). The UI should feel reassuring and clear, avoiding alarming or gamified visuals.
3. **Clarity over complexity** — a non-technical parent should understand a risk alert in seconds, without needing to interpret ML jargon.

---

## 2. Target Users & Design Implications

| User | Design Implication |
|---|---|
| Parent/Guardian (often non-technical) | Simple language, clear risk levels (Low/Medium/High), minimal clicks to understand "what happened and what should I do" |
| Child (indirect, never logs in) | Nothing in the product design should feel punitive or expose the child directly; product should support conversations, not just punishment |
| NGO/Support worker (future) | Aggregated, anonymized views — separate from parent-facing detail |

---

## 3. Core User Flows

### 3.1 Flow: Parent Views a New Alert
1. Parent logs into dashboard.
2. Dashboard home shows a list/feed of alerts sorted by recency and risk level.
3. Parent taps an alert card.
4. Alert detail view shows: risk level, pattern type (e.g., "Trust-building followed by request to move to private chat"), a short flagged snippet (minimal, not full conversation), and suggested next steps (e.g., "Talk to your child," "Learn more about grooming red flags," "Contact a verified support channel").

### 3.2 Flow: Parent Reviews Dashboard Trends
1. Parent navigates to a "Trends" or "Overview" tab.
2. Sees a simple chart of alert counts over time (by risk level).
3. Can filter by child profile (if multiple children are monitored) and by pattern type.

### 3.3 Flow: Simulated Ingestion (Demo Mode for Hackathon)
1. Judge/demo user inputs or uploads sample conversation text via a demo panel.
2. System processes and returns a risk classification.
3. New alert appears live on the dashboard (via WebSocket or refresh).

---

## 4. Information Architecture

```
App
├── Login / Auth
├── Dashboard (Home)
│   ├── Alert Feed (list of cards: risk level, pattern type, timestamp)
│   └── Summary Stats (total alerts, breakdown by risk level)
├── Alert Detail View
│   ├── Risk Level & Score
│   ├── Pattern Type & Explanation
│   ├── Flagged Snippet (minimal context)
│   └── Suggested Next Steps / Resources
├── Trends / Insights
│   └── Chart: Alerts over time, by risk level / pattern type
├── Demo Ingestion Panel (for hackathon demo purposes)
└── Settings
    └── Child Profiles, Notification Preferences
```

---

## 5. Visual Design Direction

### 5.1 Tone
- Calm, protective, trustworthy — think safety and care, not alarm-fatigue red banners everywhere.
- Avoid clinical/cold "security dashboard" aesthetics; aim for warmth balanced with clarity.

### 5.2 Color System (Tailwind-based)
| Purpose | Color Direction |
|---|---|
| Primary brand | Deep indigo/blue — trust, safety |
| Risk: Low | Soft green |
| Risk: Medium | Amber/yellow |
| Risk: High | Muted red (not neon/alarming) — firm but not panic-inducing |
| Background | Neutral off-white / soft gray for light mode |
| Accent | A single warm accent (e.g., teal) for CTAs like "View Resources" |

*(Map directly to Tailwind's default palette where possible — e.g., `indigo-600`, `emerald-500`, `amber-500`, `rose-500`, `slate-50` — to keep implementation fast.)*

### 5.3 Typography
- Clean, highly legible sans-serif (e.g., Inter, or system font stack) — prioritize readability for non-technical parents over stylistic flourish.
- Clear hierarchy: large risk-level labels, medium-weight section headers, readable body text for explanations.

### 5.4 Components
- **Alert Card** — compact, shows risk badge (color-coded pill), pattern type, timestamp, one-line summary.
- **Risk Badge** — color-coded pill component (Low/Medium/High) reused across dashboard and detail views for consistency.
- **Explanation Panel** — plain-language description of *why* something was flagged, avoiding raw ML terminology (e.g., say "This message showed signs of an adult trying to isolate the child from trusted people" rather than "isolation_request: 0.87").
- **Resource/CTA Block** — links or suggestions for next steps (talk to child, learn about grooming signs, contact verified support).

---

## 6. Accessibility Considerations
- Color is never the only signal for risk level — always paired with text labels ("High Risk", not just red).
- Sufficient contrast ratios for text on colored badges/backgrounds.
- Dashboard usable via keyboard navigation for accessibility compliance.
- Language simplicity — avoid jargon, since target users span varying literacy/tech-familiarity levels across India.

---

## 7. Content & Microcopy Principles
- Never use language that shames the child or implies wrongdoing on their part.
- Always frame alerts around the *external* risk (e.g., a predator's behavior), not the child's actions.
- Explanation text should be short, calm, and actionable — no walls of technical text.

---

## 8. Wireframe Sketch (Textual)

**Dashboard Home**
```
┌─────────────────────────────────────────────┐
│  Digital Guardrails         [Child: Aditi ▾] │
├─────────────────────────────────────────────┤
│  Summary: 2 High • 3 Medium • 5 Low (7 days) │
├─────────────────────────────────────────────┤
│  ⚠ High   | Trust-building pattern | 2h ago  │
│  ⚠ Medium | Harassment language     | 1d ago │
│  ✓ Low    | Mild teasing detected   | 2d ago │
└─────────────────────────────────────────────┘
```

**Alert Detail**
```
┌─────────────────────────────────────────────┐
│  ⚠ High Risk — Trust-Building / Isolation    │
├─────────────────────────────────────────────┤
│  What we noticed:                            │
│  "An adult contact encouraged the child to   │
│   keep the conversation secret and move to   │
│   a private platform."                       │
│                                               │
│  Suggested next steps:                       │
│  • Talk with your child calmly               │
│  • Review grooming warning signs             │
│  • Contact a verified support channel        │
└─────────────────────────────────────────────┘
```

---

## 9. Design Deliverables for Hackathon Demo
- Login screen
- Dashboard home (alert feed + summary stats)
- Alert detail view
- Demo ingestion panel (to show detection live during the 3-minute video)
- (Optional, time permitting) Trends/insights view
