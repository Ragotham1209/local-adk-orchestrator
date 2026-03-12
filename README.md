# Enterprise Local ADK Orchestrator
### Google ADK | Streamlit | LM Studio | Spec-Driven Development

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit)
![LiteLLM](https://img.shields.io/badge/LiteLLM-Proxy-orange?logo=pyo)
![Google ADK](https://img.shields.io/badge/Agent%20Dev%20Kit-Google-4285F4?logo=google)
![License](https://img.shields.io/badge/License-MIT-green)

A production-grade local Python orchestration pipeline utilizing Streamlit for the UI and the Google Agent Development Kit (ADK) for AI routing. 

This framework operates as a **Local Agent** that cross-examines user requirements, enforces enterprise coding standards (`SKILLS.md`), and drops highly structured markdown specs. It initiates an **Agent-to-Agent (A2A) continuous loop** where downstream **Enterprise Agents** (Antigravity, Cursor, VS Code) consume the specs, execute the code, and drop results/logs back into the system. The Local Agent then automatically reads these logs, audits unit test or simulation edge-case failures, and dynamically drops fix specs back to the Enterprise Agent until the task is complete.

---

## Architecture

<p align="center">
  <img src="docs/architecture.png" alt="System Architecture" width="850"/>
</p>

---

## Key Features

| Layer | Feature | Detail |
|-------|---------|--------|
| **Interface** | Streamlit Real-Time Chat | Streamed inference tokens with sliding window arrays keeping memory restricted to the System Prompt + last 4 turns. |
| **Logic** | Multi-Agent Hub | Routing requests between Agent A (Clarifier), Agent B (Optimizer), and Agent C (Auditor) via API. |
| **State** | Trace Memory | User requirements are explicitly captured into `rtm_state.json` avoiding context loss. |
| **Governance** | Enterprise Standard Guardrails | Constrains LLM outputs strictly to rules parsed from the static `SKILLS.md` registry. |
| **Validation** | DSA Compliance Engine | Mathematical constraint engine using AST parsing over Git outputs to physically block algorithms with $O(n^2)$ time complexity. |
| **Execution** | Active Circuit Breaker | Proactive `system_io.py` stops Agent C from emitting auto-fixes without explicit `Y/N` User UI override. |

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit | Real-time chat & spec preview dashboard |
| **Orchestration** | Google ADK & Python | Defines modular Clarifier, Optimizer, and Auditor tools |
| **LLM Gateway** | LiteLLM | Normalizes API requests to the physical local LLM |
| **Local Inference** | LM Studio (`qwen2.5-coder-7b`) | VRAM-loaded inference execution running zero cloud cost |
| **A2A Middleware** | File System Handoffs | Asynchronous communication bridge syncing Specs and Logs between agents |
| **Rule Engine** | `ast` and Python Subprocess | Git diff structural evaluation against time-complexity limits |
| **Output Intercept** | Markdown (`.md`) Specs | Bridging files generated explicitly for downstream AI context windows |

---

## Project Structure

```
local-adk-orchestrator/
|-- src/                           # Core operational python modules
|   +-- app.py                     # Streamlit frontend, chat loop, circuit breaker UI
|   +-- orchestrator.py            # ADK and litellm routing layer (Agents A, B, C)
|   +-- dsa_engine.py              # Big-O mathematical guardrails & DAG evaluator
|   +-- system_io.py               # Audit log reader and file system operations
|-- build_logs/                    # Temporary testing artifacts evaluated by Auditor
|-- .agent/workflows/              # Forward-handoff spec generation bay
|   +-- execute_local_spec.md      # Final output consumed by downstream IDEs
|-- docs/                          # Documentation and diagramming
|   +-- architecture.png           # Blueprint rendering
|-- SKILLS.md                      # Foundational engineering rules engine
|-- rtm_state.json                 # Auto-generated requirements trace memory
+-- .gitignore
```

---

## Quick Start

### Prerequisites
- Python 3.9+
- Local local LLM setup instance (e.g. LM Studio running `qwen2.5-coder-7b` actively rendering to `http://localhost:1234/v1`)
- Git CLI

### 1. Project Initialization
```bash
python -m venv venv
# Linux/macOS
source venv/bin/activate 
# Windows PowerShell
.\venv\Scripts\activate

pip install streamlit google-adk litellm gitpython
```

### 2. Launch Local Environment
Starting the Streamlit UI immediately boots the system bindings.
```bash
streamlit run src/app.py
```

---

## The Agent-to-Agent (A2A) Continuous Loop

```
1. Local Agent (Optimizer) --> Drops initial Spec logic constraints
  --> 2. Enterprise Agent (IDE) reads Spec and writes/executes Code
    --> 3. Enterprise Agent drops test results and edge-case logs to `build_logs/`
      --> 4. Local Agent (Auditor) automatically reads `build_logs/`
        --> 5. Local Agent drops `auto_fix.md` specs for simulation misses
          --> 6. Enterprise Agent picks up fixes. Loop continues until tests pass.
```

---

## Guardrails & Complexity Enforcement

Agent C (The Auditor) triggers independent evaluations checking structural commits over simply matching code diffs:
1. Validates standard `pytest` coverage execution and simulation results dropped by the Enterprise Agent.
2. Reconstructs git additions physically checking for inner nested-loop complexity flags via `dsa_engine.py` allowing deterministic fail states before the A2A loop completes.

---

**Built by [Ragotham Kanchi](https://github.com/Ragotham1209)**
