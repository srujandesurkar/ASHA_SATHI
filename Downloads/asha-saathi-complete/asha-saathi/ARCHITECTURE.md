# ASHA Saathi – Architecture & Technical Specification

## System Overview

ASHA Saathi is an AI voice field register built for Accredited Social Health Activists (ASHA workers) in India. It converts unconstrained, Indic code-mixed speech dictation into structured public-health visit records with zero typing, performs real-time deterministic danger sign triage, and maintains follow-up task registers.

---

## 1. High-Level Architecture Diagram (Mermaid)

```mermaid
flowchart TD
    subgraph Client["Mobile-First Field Frontend (React + TS + Tailwind)"]
        UI["Field Register UI"]
        MIC["Large Mic Button / AudioWorklet (16kHz PCM)"]
        REV["Structured Review & Spoken Evidence Card"]
        ALT["High-Contrast Danger Sign Alert Banner"]
    end

    subgraph VoiceGateway["Voice Service Layer (WebSocket & REST)"]
        WSS["WebSocket Stream Router (/api/voice/stream)"]
        DISC["First-Turn AI Disclosure Engine"]
        TTS["Timbre Audio Synthesizer (/api/voice/readback)"]
    end

    subgraph GnaniLayer["Gnani AI Platform"]
        PRISMA["Gnani Prisma v3.0 Streaming STT<br/>(Indic Code-Mix + Keyterm Prompting)"]
        TIMBRE["Gnani Timbre TTS<br/>(Natural Indic Speech Synthesis)"]
        DEMO["Gnani Demo Mode Simulator<br/>(Fallback when credentials unset)"]
    end

    subgraph CoreEngine["Backend Intelligence (FastAPI + Python 3.13)"]
        EXT["Smart Visit Extraction Engine<br/>(Evidence Linking + Rule Validation)"]
        SHIELD["Danger Shield Engine<br/>(Deterministic IMNCI / MoHFW Rulebook)"]
        ORCH["Voice Conversational Orchestrator<br/>(Spoken Correction & Confirmation)"]
    end

    subgraph Storage["Persistence & Privacy (SQLite + DPDP Compliant)"]
        DB[(Async SQLite Database)]
        SYNTH["Synthetic Beneficiary Store"]
        TASKS["Follow-Up Task Manager"]
    end

    MIC -->|Audio Chunks| WSS
    WSS --> PRISMA
    PRISMA -.->|Live Transcript Tokens| WSS
    WSS --> EXT
    EXT --> SHIELD
    SHIELD --> ALT
    EXT --> REV
    ORCH --> TTS
    TTS --> TIMBRE
    TIMBRE -.->|Spoken Read-Back Audio| UI

    REV -->|Spoken Confirmation 'Haan save karo'| DB
    DB --> SYNTH
    DB --> TASKS
```

---

## 2. Voice Session State Machine

```mermaid
stateDiagram-v2
    [*] --> Idle: ASHA worker opens app
    Idle --> Intro: Tap 'Voice Visit' button
    Intro --> Listening: Assistant introduces as AI in Hindi/English
    Listening --> Extracting: Worker speaks visit notes ('Stop' or silence)
    Extracting --> DangerCheck: Streaming text parsed into fields
    
    state DangerCheck {
        [*] --> EvaluateRules
        EvaluateRules --> PositiveDanger: High-risk symptom matched
        EvaluateRules --> SafeRecord: No danger signs or explicit negation
    }

    PositiveDanger --> AlertSpoken: Speak immediate PHC referral in worker language
    AlertSpoken --> Readback: Read extracted fields aloud
    SafeRecord --> Readback: Read extracted fields aloud
    
    Readback --> AwaitingResponse: 'Is this correct? Say Haan save karo or speak correction'
    
    AwaitingResponse --> FieldCorrection: Worker speaks 'No, weight is 2.8 kilo'
    FieldCorrection --> ReadbackModified: Update ONLY changed field & re-read change
    ReadbackModified --> AwaitingResponse
    
    AwaitingResponse --> ConfirmedSave: Worker speaks 'Haan save karo' / 'Yes confirm'
    ConfirmedSave --> TaskGenerated: Record committed + Follow-up tasks scheduled
    TaskGenerated --> [*]: Audio discarded, session closed
```

---

## 3. Core Component Roles

1. **Gnani Service Layer (`app/services/gnani_service.py`)**:
   - Manages Prisma streaming STT WebSockets and Timbre synthesis REST APIs.
   - Inject official healthcare keyterms (`IFA goli`, `ANC`, `HBNC`, `Pentavalent`, `BCG`, `pasli chalna`, `garam bukhar`).
   - Labeled Demo Mode: Provides high-fidelity offline simulation without mocking fake API responses.
2. **Smart Extraction Engine (`app/services/extraction_service.py`)**:
   - Extracts: `beneficiary_id`, `visit_type`, `visit_date`, `weight_kg`, `vaccinations_due`, `vaccinations_completed`, `anc_pnc_details`, `next_visit_date`.
   - Links every field to exact spoken source evidence with confidence score.
   - Enforces zero hallucination: preserves missing fields as `null` and prompts worker for voice clarification.
3. **Danger Shield Engine (`app/services/danger_shield.py`)**:
   - Separate, deterministic, rule-based danger sign detector.
   - Versioned vocabulary (`V1.2`) mapped to MoHFW and IMNCI protocols.
   - Windowed negation analysis (`nahi hai`, `no fever`, `theek se pee raha`) preventing false positives.
   - Generates emergency spoken prompts in Hindi and English.
4. **Voice Orchestrator (`app/services/voice_orchestrator.py`)**:
   - Generates first-turn AI disclosure.
   - Constructs natural spoken read-back sentences.
   - Modifies ONLY target field during voice corrections ("No, weight is 2.8 kg").
   - Enforces spoken confirmation before database insertion.
