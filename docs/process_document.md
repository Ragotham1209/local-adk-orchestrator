# Local ADK Orchestrator: Process & A2A Workflow Guide

## Goal
This document outlines the operational process flow of the **Local ADK Orchestrator**, detailing how an engineer moves from an initial idea to a fully integrated, mechanically validated codebase using the Agent-to-Agent (A2A) bidirectional loop.

---

## 1. Requirement Gathering (The Clarification Phase)
**Actor:** User + Agent A (Clarifier)
**Location:** Streamlit UI (`http://localhost:8501`)

1. The engineer opens the local UI and provides a high-level request (e.g., "Build an SCD2 pipeline").
2. Agent A conditionally compares the request against the enterprise rulebook (`SKILLS.md`).
3. If necessary guardrails (like testing frameworks or error-handling standards) are not mentioned by the user, Agent A actively prompts the user to confirm them.
4. As facts are agreed upon, the system extracts these parameters and saves them persistently to the `rtm_state.json` (Requirements Trace Matrix) dynamically visible in the sidebar.

## 2. Context Compression (The Generation Phase)
**Actor:** Agent B (Optimizer)
**Location:** Internal generation

1. Once the engineer is satisfied with the traced requirements, they click **"Approve & Generate Spec"**.
2. Agent B reads the `rtm_state.json` and strips out all conversational fluff.
3. It generates a hyper-dense Markdown specification that outlines exactly what code to write, ensuring downstream token-efficiency.
4. The engineer physically previews this draft spec in the UI window and can make manual text edits.

## 3. The Agent-to-Agent (A2A) Handoff
**Actor:** Local Handoff Engine -> Enterprise IDE
**Location:** File System (`.agent/workflows/`)

1. The engineer clicks **"Finalize Spec & Drop to Enterprise Agent (A2A Handoff)"**.
2. The orchestrator writes the finalized markdown to `/.agent/workflows/execute_local_spec.md`.
3. The engineer flips to their Enterprise IDE (Cursor, VS Code with Copilot, Antigravity).
4. The Enterprise AI Agent reads the `execute_local_spec.md` (consuming minimal tokens) and executes the code generation.

## 4. Execution Logging & Unit Testing
**Actor:** Enterprise IDE
**Location:** User's Application Codebase -> `build_logs/`

1. The Enterprise AI generates the Python scripts and runs the requested unit tests (e.g., `pytest`).
2. The stdout logs, test coverage results, and Git diffs of the resulting work are automatically appended/piped by the IDE into the `build_logs/` directory of the orchestrator.

## 5. The Audit Loop & Circuit Breaker
**Actor:** Agent C (Auditor) + Local AST Engine
**Location:** Streamlit UI

1. Once the logs drop, the UI un-spins and Agent C automatically analyzes the `build_logs/`.
2. Simultaneously, `dsa_engine.py` parses the AST of the generated code to manually flag mechanical failures (e.g., nested `for` loops causing $O(n^2)$ time complexity).
3. If failures or unoptimized logic are detected, the **Auditor Circuit Breaker** trips in the UI, displaying the edge-case warnings.

## 6. Auto-Fix Drop (Loop Conclusion)
**Actor:** User + File System
**Location:** Streamlit UI -> Enterprise IDE

1. The engineer reads the Auditor's report and clicks **"Approve Auto-Fix Drop"**.
2. The Orchestrator generates an `auto_fix.md` specification containing the exact logic required to patch the tests or correct the algorithm.
3. This is dropped back to the file system. The Enterprise Agent consumes the fix, re-executes, and tests run green. The A2A loop successfully closes.
