import json
import os
from pathlib import Path
import litellm

# Ensure litellm routes to LM Studio correctly
litellm.api_base = "http://localhost:1234/v1"
litellm.api_key = "lm-studio" # mock key
MODEL_NAME = "openai/qwen2.5-coder-7b" # litellm format for custom base

# Import internal modules
try:
    import system_io
    import dsa_engine
except ImportError:
    pass

BASE_DIR = Path(__file__).parent.parent.resolve()

def read_skills() -> str:
    skills_path = BASE_DIR / "SKILLS.md"
    if skills_path.exists():
        with open(skills_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def read_rtm() -> str:
    rtm_path = BASE_DIR / "rtm_state.json"
    if rtm_path.exists():
        with open(rtm_path, "r", encoding="utf-8") as f:
            return f.read()
    return "{}"

class Orchestrator:
    def __init__(self):
        self.skills_context = read_skills()

    def run_clarifier(self, messages: list) -> str:
        """
        Agent A (The Clarifier): Reads SKILLS.md. Instructed strictly to ask 1-3 
        architectural cross-questions based on user input to align with defined skills.
        It must not write application code.
        """
        system_prompt = (
            "You are The Clarifier, an expert architectural agent. "
            "Your ONLY role is to read the user's request and ask 1-3 architectural cross-questions "
            "to align their request with the project standards.\n\n"
            "PROJECT STANDARDS (SKILLS.md):\n"
            f"{self.skills_context}\n\n"
            "DO NOT write any application code. Keep questions highly technical and concise."
        )
        
        formatted_messages = [{"role": "system", "content": system_prompt}] + messages
        
        response = litellm.completion(
            model=MODEL_NAME,
            messages=formatted_messages,
            stream=False # Stream handled in UI if needed, or return block
        )
        return response.choices[0].message.content

    def run_clarifier_stream(self, messages: list):
        """
        Streaming version of clarifier for UI enhancement.
        """
        system_prompt = (
            "You are The Clarifier. Ask 1-3 architectural cross-questions based on user input to align with standards.\n"
            "DO NOT write any application code. Be concise.\n\n"
            f"STANDARDS:\n{self.skills_context}"
        )
        formatted_messages = [{"role": "system", "content": system_prompt}] + messages
        
        response = litellm.completion(
            model=MODEL_NAME,
            messages=formatted_messages,
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def run_optimizer(self) -> str:
        """
        Agent B (The Optimizer): Reads rtm_state.json and SKILLS.md. 
        Outputs a dense, token-efficient markdown file. Reference rules from SKILLS.md.
        """
        rtm_data = read_rtm()
        system_prompt = (
            "You are The Optimizer. Your role is to generate a hyper-optimized markdown specification. "
            "Read the provided RTM Matrix and project standards. Output dense, token-efficient markdown. "
            "Reference specific rules from SKILLS.md rather than writing redundant boilerplate.\n\n"
            f"PROJECT STANDARDS:\n{self.skills_context}\n\n"
            f"RTM STATE (Requirements Matrix):\n{rtm_data}\n\n"
            "Generate the final Master Spec markdown now."
        )
        
        response = litellm.completion(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": system_prompt}]
        )
        
        spec_content = response.choices[0].message.content
        return spec_content

    def run_auditor(self) -> dict:
        """
        Agent C (The Auditor): Parses test_results.json and git diff.
        Applies mathematical guardrails from dsa_engine.
        Returns evaluation and potentially trips circuit breaker.
        """
        test_results = system_io.read_test_results()
        git_diff = system_io.read_git_diff()
        
        system_prompt = (
            "You are The Auditor. Review the git diff and test results. "
            f"{dsa_engine.BIG_O_AUDIT_PROMPT_CONSTRAINT}\n"
            "Generate an auto_fix.md proposal if there are errors or complexity violations. "
            "If everything passes, indicate SUCCESS."
        )
        
        user_prompt = (
            f"GIT DIFF:\n{git_diff}\n\n"
            f"TEST RESULTS:\n{json.dumps(test_results, indent=2)}\n\n"
            "Write the review and proposed auto-fix."
        )
        
        response = litellm.completion(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
        )
        
        output = response.choices[0].message.content
        
        # Auditor completes, return for circuit breaker check
        return {"auditor_output": output, "status": "review_complete"}
