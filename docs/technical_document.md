# Local ADK Orchestrator: Technical Documentation

## 1. System Overview
The **Local ADK Orchestrator** is a local Python-based application that leverages the Google Agent Development Kit (ADK) and `litellm` gateway to provide an upstream context-engineering layer for AI-assisted development. It acts as a prompt architect that intercepts, clarifies, and conditionally formats system requirements before handing them off to downstream Enterprise IDEs (Cursor, VS Code, Antigravity).

## 2. Core Architecture

The architecture consists of three primary layers:
1. **Frontend (UI Layer):** Built with Streamlit (`app.py`), providing an interactive chat interface, a Requirements Trace Matrix (RTM) visualizer, and manual circuit-breaker approval loops.
2. **Orchestration Layer:** Managed by `orchestrator.py`, routing calls between specialized AI Agents (Clarifier, Optimizer, Auditor) built via Google ADK.
3. **Execution Backend:** Relies on local LLM inference via LM Studio (exposing an OpenAI-compatible API at `http://localhost:1234/v1`) running target models (e.g., `qwen2.5-coder-7b`).

### 2.1 File Structure
```text
local-adk-orchestrator/
├── src/
│   ├── app.py              # Main Streamlit application
│   ├── orchestrator.py     # ADK routing and LLM logic
│   ├── dsa_engine.py       # Complexity AST-parsing rules
│   └── system_io.py        # File and log reading utilities
├── docs/                   # Documentation and Visio diagrams
├── .agent/workflows/       # Output target for A2A handoffs (execute_local_spec.md)
├── build_logs/             # Ingestion target for Enterprise IDE test results
├── rtm_state.json          # Dynamic conversational memory state
├── SKILLS.md               # Static Enterprise Guardrails 
└── README.md
```

## 3. The Multi-Agent System

The Orchestrator utilizes three specialized ADK agents:

### Agent A: The Clarifier
- **Role:** Cross-examines user requirements.
- **Function:** Receives conversational input, references `SKILLS.md` to identify missing architectural dependencies (e.g., Pytest requirements, SCD2 logic), and streams back clarifying questions.

### Agent B: The Optimizer
- **Role:** Generates the structured Markdown Specification.
- **Function:** Reads the accumulated state from `rtm_state.json` and synthesizes the constraints into a dense, token-efficient `execute_local_spec.md` workflow file.

### Agent C: The Auditor
- **Role:** Reviews Enterprise Agent logs and Git diffs.
- **Function:** Ingests data from `build_logs/` after downstream execution. Uses `dsa_engine.py` (an AST parser) to mechanically scan the generated code structures for Big-O violations (e.g., $O(n^2)$ degraded nested loops), alerting the user via the Circuit Breaker if an `auto_fix.md` drop is required.

## 4. Technical Dependencies
- **Streamlit:** UI rendering.
- **Google ADK:** Agent routing and framework definitions.
- **LiteLLM:** Normalizes API calls to abstract the underlying model endpoint.
- **Python `ast` Library:** Native abstract syntax tree parsing for mechanical code validation.

## 5. Network Dynamics
The application operates fully completely air-gapped on `localhost`. 
- Streamlit serves on `localhost:8501`.
- API configurations proxy via `litellm` straight to `http://localhost:1234/v1` (LM Studio).
- No external internet LLM API calls are required unless explicitly configured.
