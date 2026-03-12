import ast
import re
from typing import Dict, List, Set, Any

# ==========================================
# 1. AST Parser for Git Diffs
# ==========================================
class CodeChangeSummarizer(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
        self.classes = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.functions.append(node.name)
        self.generic_visit(node)
        
    def visit_ClassDef(self, node: ast.ClassDef):
        self.classes.append(node.name)
        self.generic_visit(node)

def summarize_ast_changes(file_content: str) -> dict:
    """
    A simple structural summarizer using AST
    In production, this would diff the AST of the old vs new file.
    """
    try:
        tree = ast.parse(file_content)
        summarizer = CodeChangeSummarizer()
        summarizer.visit(tree)
        return {"functions": summarizer.functions, "classes": summarizer.classes}
    except Exception as e:
        return {"error": str(e)}

def parse_logical_diff(git_diff_output: str) -> str:
    """
    Summarize a raw git diff into logical changes rather than raw text diffs.
    In a real scenario, this would extract the changed files and parse them with AST to find precise logical changes.
    Here we simulate the logical summary by extracting function names from unified diff headers.
    """
    logical_changes = []
    
    # Very naive regex to find function/class definitions in diff additions
    added_funcs = re.findall(r"^\+\s*def\s+([a-zA-Z_]\w*)\s*\(", git_diff_output, re.MULTILINE)
    if added_funcs:
        logical_changes.append(f"Added/Modified Functions: {', '.join(added_funcs)}")
        
    return "\n".join(logical_changes) if logical_changes else "No structural logical changes detected."

# ==========================================
# 2. Topological Sort (DAG Router)
# ==========================================
def topological_sort(tasks: Dict[str, List[str]]) -> List[str]:
    """
    Perform a topological sort on a DAG of tasks.
    tasks: dict where key is task name, value is list of dependencies.
    """
    visited: Set[str] = set()
    temp_mark: Set[str] = set()
    order: List[str] = []

    def visit(node: str):
        if node in temp_mark:
            raise ValueError(f"Cyclic dependency detected involving task: {node}")
        if node not in visited:
            temp_mark.add(node)
            for dependency in tasks.get(node, []):
                visit(dependency)
            temp_mark.remove(node)
            visited.add(node)
            order.append(node)

    for task in tasks:
        if task not in visited:
            visit(task)

    return order

# ==========================================
# 3. Big-O Evaluator Constants & Logic
# ==========================================

# Direct String injection for the Auditor agent
BIG_O_AUDIT_PROMPT_CONSTRAINT = (
    "CRITICAL GUARDRAIL: You must mathematically audit all data-processing functions. "
    "Flag any algorithm with time complexity O(n^2) or worse. Provide explicit logical justification "
    "if such complexity is unavoidable. Do not pass the audit if an O(n^2) approach can be optimized to O(n log n) or O(n)."
)

def evaluate_nested_loops_ast(file_content: str) -> bool:
    """
    A very naive AST based check to flag potential O(n^2) logic via nested loops in the same function.
    Returns True if potential O(n^2) is found, False otherwise.
    """
    class LoopVisitor(ast.NodeVisitor):
        def __init__(self):
            self.has_nested = False
            self.loop_depth = 0

        def visit_For(self, node: ast.For):
            self.loop_depth += 1
            if self.loop_depth >= 2:
                self.has_nested = True
            self.generic_visit(node)
            self.loop_depth -= 1

        def visit_While(self, node: ast.While):
            self.loop_depth += 1
            if self.loop_depth >= 2:
                self.has_nested = True
            self.generic_visit(node)
            self.loop_depth -= 1

    try:
        tree = ast.parse(file_content)
        visitor = LoopVisitor()
        visitor.visit(tree)
        return visitor.has_nested
    except Exception:
        return False
