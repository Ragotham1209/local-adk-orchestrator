import json
import os
import subprocess
from pathlib import Path

# Base directories configuration
BASE_DIR = Path(__file__).parent.resolve()
WORKFLOWS_DIR = BASE_DIR / ".agent" / "workflows"
BUILD_LOGS_DIR = BASE_DIR / "build_logs"

def write_local_spec(content: str) -> str:
    """
    Forward Handoff: Write the output of Agent B strictly to `/.agent/workflows/execute_local_spec.md`.
    """
    WORKFLOWS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = WORKFLOWS_DIR / "execute_local_spec.md"
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    return str(file_path)

def read_test_results() -> dict:
    """
    Reverse Handoff (Auditing): Read from `/build_logs/test_results.json`.
    """
    file_path = BUILD_LOGS_DIR / "test_results.json"
    if not file_path.exists():
        return {"error": "test_results.json not found."}
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"error": f"Failed to parse test results: {str(e)}"}

def read_git_diff() -> str:
    """
    Reverse Handoff (Auditing): Read `git diff` outputs.
    """
    try:
        # Assumes git is initialized
        result = subprocess.run(
            ["git", "diff", "HEAD"], 
            cwd=str(BASE_DIR), 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout if result.stdout else "No pending git changes."
    except subprocess.CalledProcessError as e:
        return f"Git diff error: {e.stderr}"
    except Exception as e:
        return f"Error executing git: {str(e)}"

def trigger_circuit_breaker(auto_fix_content: str, is_ui_approved: bool = False) -> dict:
    """
    The Circuit Breaker (MANDATORY): Before Agent C writes an `auto_fix.md` file 
    to the workflows directory, it must halt and request approval.
    
    In a UI context, if `is_ui_approved` is False, we return a payload signaling 
    that the UI needs to prompt the user. 
    """
    if not is_ui_approved:
        return {
            "status": "pending_approval",
            "message": "Circuit Breaker Tripped! User approval is required to write auto_fix.md.",
            "pending_content": auto_fix_content
        }
    
    # If approved, write the file
    WORKFLOWS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = WORKFLOWS_DIR / "auto_fix.md"
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(auto_fix_content)
        
    return {
        "status": "approved",
        "message": f"auto_fix.md successfully written to {file_path}"
    }
