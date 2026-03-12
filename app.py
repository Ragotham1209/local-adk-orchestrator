import streamlit as st
import json
import os
from pathlib import Path
from orchestrator import Orchestrator
import system_io

BASE_DIR = Path(__file__).parent.resolve()
HISTORY_FILE = BASE_DIR / ".chat_history.json"
RTM_FILE = BASE_DIR / "rtm_state.json"

st.set_page_config(page_title="Local ADK Orchestrator", layout="wide")

def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(messages):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f)

def load_rtm():
    if RTM_FILE.exists():
        with open(RTM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_rtm(rtm_state):
    with open(RTM_FILE, "w", encoding="utf-8") as f:
        json.dump(rtm_state, f, indent=2)

def extract_and_update_rtm(user_input: str):
    """
    Naively extract keywords into RTM state based on user input for demonstration.
    In a fully robust pipeline, another background LLM call extracts structured facts.
    """
    current_rtm = load_rtm()
    if "recorded_facts" not in current_rtm:
        current_rtm["recorded_facts"] = []
    
    # Just append user statements as facts for now
    current_rtm["recorded_facts"].append(user_input)
    save_rtm(current_rtm)

# --------------------------
# UI Initialization
# --------------------------
st.title("Local ADK Orchestrator")

if "messages" not in st.session_state:
    st.session_state.messages = load_history()
if "draft_spec" not in st.session_state:
    st.session_state.draft_spec = None
if "draft_approved" not in st.session_state:
    st.session_state.draft_approved = False
if "auditor_output" not in st.session_state:
    st.session_state.auditor_output = None

orch = Orchestrator()

# Sidebar: RTM State & Actions
with st.sidebar:
    st.header("Trace Matrix (RTM)")
    current_rtm = load_rtm()
    st.json(current_rtm)
    
    st.header("Actions")
    if st.button("Approve & Generate Spec", type="primary"):
        with st.spinner("Agent B (The Optimizer) is generating spec..."):
            st.session_state.draft_spec = orch.run_optimizer()

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        save_history([])
        save_rtm({})
        st.rerun()

# --------------------------
# Main Chat Layout
# --------------------------
chat_container = st.container()
prompt = st.chat_input("Answer Clarifier's questions or describe features...")

# Render Chat History
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Handle User Input
if prompt:
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_history(st.session_state.messages)
    extract_and_update_rtm(prompt) # Record fact in background
    
    # Sliding Window: System prompt (handled in Orchestrator) + last 4 turns limits
    # Last 4 turns = 2 user prompts + 2 assistant responses (4 objects)
    sliding_window = st.session_state.messages[-4:] if len(st.session_state.messages) >= 4 else st.session_state.messages
    
    with chat_container:
        with st.chat_message("assistant"):
            try:
                response_stream = orch.run_clarifier_stream(sliding_window)
                full_response = st.write_stream(response_stream)
            except Exception as e:
                full_response = f"Connection Error (Is LM Studio running?): {str(e)}"
                st.error(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    save_history(st.session_state.messages)
    st.rerun() # Refresh sidebar RTM

# --------------------------
# Optimization & Audit Workflow Layers
# --------------------------
if st.session_state.draft_spec and not st.session_state.draft_approved:
    st.markdown("---")
    st.subheader("Draft Spec Preview (Agent B)")
    edited_spec = st.text_area("Adjust constraints before final commit to execute_local_spec.md:", 
                               value=st.session_state.draft_spec, height=400)
    
    if st.button("Finalize Spec & Trigger Auditor"):
        system_io.write_local_spec(edited_spec)
        st.success("Spec successfully written to .agent/workflows/execute_local_spec.md")
        st.session_state.draft_approved = True
        
        with st.spinner("Agent C (The Auditor) is reviewing code complexity..."):
            audit_result = orch.run_auditor()
            st.session_state.auditor_output = audit_result["auditor_output"]
        st.rerun()

if st.session_state.auditor_output:
    st.markdown("---")
    st.subheader("Auditor Agent Circuit Breaker")
    st.info("The Auditor found the following insights after parsing git diff and test results:")
    st.markdown(st.session_state.auditor_output)
    
    st.warning("Agent C requests to write 'auto_fix.md'. Do you approve this operation?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✔ Approve Auto-Fix", use_container_width=True):
            result = system_io.trigger_circuit_breaker(st.session_state.auditor_output, is_ui_approved=True)
            st.success(result["message"])
            st.session_state.auditor_output = None
            
    with col2:
        if st.button("✖ Reject", use_container_width=True):
            st.error("Circuit Breaker Tripped: Operation manually aborted by User.")
            st.session_state.auditor_output = None
