# Data Card — Digital Guardrails Unified Multilingual Safety Corpus (Real + Synthetic)

## 1. Overview & Dataset Summary
* **Dataset Name**: Digital Guardrails Unified Multilingual Safety Corpus (v3.0)
* **Creation Date**: September 12, 2026
* **Scope**: Pre-integration child online safety, online grooming detection, and multilingual cyberbullying recognition.
* **Corpus Composition**: **Hybrid (Real-World Research Datasets + Synthetic Grooming Arcs)**
  - **Real Public Research Data**: 340 entries (43.0%)
  - **Synthetic Grooming & Nuance Arcs**: 450 entries (57.0%)
* **Total Conversations**: **790**
* **Languages**: English, Hindi, Hinglish (code-mixed Hindi-English), Malayalam, and Manglish (code-mixed Malayalam-English).
* **Format**: Structured JSON ([dataset.json](file:///c:/Users/naren/Videos/GDG-Hackathon/backend/ml/dataset.json)) and CSV ([dataset.csv](file:///c:/Users/naren/Videos/GDG-Hackathon/backend/ml/dataset.csv)).

---

## 2. Unified Schema Specification

Every entry adheres to this unified schema preserving data origin and explainability:
```json
{
  "conversation_id": "real_bullyexplain_hinglish_0001",
  "language": "Hinglish",
  "script": "mixed",
  "pattern_label": "bullying_harassment",
  "pattern_type_canonical": "bullying-harassment",
  "risk_level": "Medium",
  "turns": [
    { "speaker": "A", "text": "cleaned text..." }
  ],
  "window_text": "A: cleaned text...",
  "target_text": "cleaned text...",
  "source_dataset": "BullyExplain-Hinglish",
  "origin": "real",
  "rationale": "Direct personal insult targeting user appearance."
}
```

---

## 3. Label Definitions & Class Balance

Targeting false-positive suppression, the `neutral` class is calibrated to **50.89%** of the combined corpus:

| Pattern Label | Canonical API Label | Real Count | Synthetic Count | Total Count | Percentage | Risk Level | Description |
|---|---|---|---|---|---|---|---|
| `neutral` | `neutral` | 200 | 202 | **402** | **50.89%** | Low | Everyday teenage talk, homework, gaming slang, clean Hinglish, safety advice, negations. |
| `bullying_harassment` | `bullying-harassment` | 140 | 60 | **200** | **25.32%** | Medium | Insults, humiliation, exclusionary tactics, aggressive social comments from HASOC/BullyExplain/Dravidian. |
| `grooming_trust_building` | `grooming-trust-building` | 0 | 64 | **64** | **8.10%** | Medium | Excessive flattery ("so mature for your age"), unconditional gifts, creating exclusive emotional dependency. |
| `grooming_isolation_request` | `grooming-isolation-request` | 0 | 64 | **64** | **8.10%** | High | Secrecy from parents/teachers, deleting chat logs, switching to private/unmonitored apps, meeting alone. |
| `grooming_coercive_language` | `grooming-coercive-language` | 0 | 60 | **60** | **7.59%** | High | Blackmail, countdown ultimatums, threat of leaking private pictures/chats to school or parents. |
| **Total** | | **340** | **450** | **790** | **100.0%** | | |

---

## 4. Sourced Real Datasets & Academic Citations

Real-world datasets were ethically sourced from peer-reviewed academic benchmarks:

### 1. HASOC 2020 (Hindi Subtask)
* **Source**: Forum for Information Retrieval Evaluation (FIRE 2020 / 2021)
* **Citation**: Mandl, T., Modha, S., Kumar M, A., Chakravarthi, B. R. et al. (2020). *Overview of the HASOC track at FIRE 2020: Hate Speech and Offensive Content Identification in Indo-European Languages*. CEUR Workshop Proceedings.
* **License**: Research & Academic Evaluation Use.
* **Contribution**: 90 Hindi examples (45 Hate/Offensive `HOF` $\rightarrow$ `bullying_harassment`, 45 Non-offensive `NOT` $\rightarrow$ `neutral`).

### 2. BullyExplain (Hindi-English Code-Mixed)
* **Source**: Jha et al. (2022 / 2023)
* **Citation**: Jha, P., Maity, K., et al. (2023). *BullyExplain: An Explainable Cyberbullying Detection Dataset for Hindi-English Code-Mixed Text*.
* **License**: Open Academic Research License.
* **Contribution**: 85 Hinglish examples (50 `bullying_harassment` with extracted plain-language rationales, 35 clean `neutral`).
* **Explainability Utility**: Extracted rationales inform the plain-language safety explanation templates in Digital Guardrails alert views.

### 3. DravidianLangTech / OffensEval-Dravidian (Malayalam Subtask)
* **Source**: EACL 2021 DravidianLangTech Shared Task (Hugging Face `community-datasets/offenseval_dravidian`)
* **Citation**: Chakravarthi, B. R., et al. (2021). *Findings of the Shared Task on Offensive Language Identification in Tamil, Malayalam, and Kannada*. EACL 2021.
* **License**: Creative Commons Attribution 4.0 International (CC BY 4.0).
* **Contribution**: 90 Malayalam/Manglish examples (45 `bullying_harassment`, 45 `neutral`).

### 4. COMI-LINGUA (Hinglish Clean Text)
* **Source**: Lingo IIT Gandhinagar (`lingo-iitgn/COMI-LINGUA`)
* **License**: MIT / Academic Open Source.
* **Contribution**: 75 clean, filtered non-toxic code-mixed Hinglish conversational examples mapped directly to `neutral`.

---

## 5. Synthetic Grooming Portion (PAN12 Grounded)

* **Methodological Basis**: Academic child exploitation literature models grooming as a sequential progression:
  $$\text{Target Selection} \longrightarrow \text{Trust Building} \longrightarrow \text{Isolation / Secrecy} \longrightarrow \text{Coercive Escalation}$$
* **Safeguarding Safeguard**: No conversations involve real children or illicit materials. Examples are framed exclusively as classifier pattern training templates.
* **Multi-Turn Dynamics**: 3–5 dialogue turns demonstrating conversational context and gradual boundary crossing.
* **Tricky Benign Contrasts**:
  - *Parent check-ins* ("Where are you? Come home for dinner.") labeled `neutral`.
  - *Gaming combat banter* ("Killer shot! You completely destroyed me.") labeled `neutral`.
  - *School safety guidance* ("Teacher said never share passwords.") labeled `neutral`.

---

## 6. Language & Script Breakdown

| Language | Primary Script | Script Tag | Total Examples | Real Proportion | Synthetic Proportion |
|---|---|---|---|---|---|
| **Hinglish** | Romanized Latin | `mixed` | 250 (31.6%) | 160 (64.0%) | 90 (36.0%) |
| **Hindi** | Native Devanagari | `native` | 185 (23.4%) | 90 (48.6%) | 95 (51.4%) |
| **Manglish** | Romanized Latin | `mixed` | 150 (19.0%) | 74 (49.3%) | 76 (50.7%) |
| **English** | Latin | `roman` | 105 (13.3%) | 0 (0.0%) | 105 (100.0%) |
| **Malayalam** | Native Malayalam | `native` | 100 (12.7%) | 16 (16.0%) | 84 (84.0%) |
| **Total** | | | **790** (100%) | **340** (43.0%) | **450** (57.0%) |
