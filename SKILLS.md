# Enterprise Development Standards & Skills

This document serves as the local "Knowledge Base" for the Google ADK Orchestrator, establishing foundational enterprise constraints for all generated local specs and AI interactions. **All agents (The Clarifier, The Optimizer, The Auditor) MUST adhere to these rules.**

## 1. Agile & Scope Constraints
- **Single-Sprint Deliverables:** All tasks and generated markdown specifications MUST be strictly scoped to single-sprint deliverables.
  - Break down features into granular, trackable items.
  - If a requested scope exceeds a standard 2-week sprint capacity, halt and request the user to decompose the requirements.
- **Traceability:** Requirements must map directly to entries in the `rtm_state.json` (Requirements Trace Matrix).

## 2. Python Standards
- **Strict Type Hinting:** All Python functions, classes, and methods MUST use explicit type hinting (from the `typing` module where appropriate).
  - Example: `def process_data(input_df: pd.DataFrame) -> dict:`
- **Modular Pipelines:** Application architecture MUST follow modular data pipeline structures. Separation of concerns is mandatory (e.g., IO operations vs. business logic vs. presentation).
- **Logging over Print:** Standard `logging` framework MUST be used exclusively. `print()` statements are explicitly forbidden in production-grade code.
  - Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) must be appropriately mapped.

## 3. SQL & Database Rules
- **Optimized Queries:** SQL interactions must utilize optimized query structures to minimize execution times and resource consumption.
- **Explicit Indexing:** Database schema designs or modifications MUST include explicit indexing strategies for highly queried columns.
- **Prevention of N+1 Queries:** Database access patterns must be bulk-optimized or joined properly to prevent N+1 query performance issues.

## 4. Testing & Validation
- **Pytest Mandate:** The `pytest` framework is the required testing standard for all unit and integration tests.
- **Explicit Data Validation:** Implement data validation steps (e.g., shape checks, type assertions, or using libraries like Pydantic) at the boundaries of data pipelines.
- **Coverage Expectation:** Tests should cover core business logic and expected edge cases.

## 5. DSA & Algorithmic Guardrails
- **Complexity Limits:** Algorithms in data-processing functions with time complexity $O(n^2)$ or worse MUST NOT be permitted unless mathematically unavoidable (and must include explicit algorithmic justification).
- **Big-O Evaluation:** The Auditor Agent uses the `dsa_engine.py` pipeline to mathematically enforce these guardrails during speculative code review.
