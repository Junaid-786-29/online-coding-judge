"""
AST-based static validation for user-submitted Python source code.
Acts as an application-level defense-in-depth screening layer before spawning subprocesses.

NOTE: Static analysis is NOT a substitute for kernel/container-level isolation (e.g. gVisor, Docker).
It provides an early rejection mechanism for known unsafe standard imports.
"""

import ast
from app.core.security_config import BLOCKED_MODULES


def validate_python_source(source_code: str) -> str | None:
    """
    Statically inspect Python source code for forbidden module imports.
    Returns an error message string if blocked imports are found, or None if safe.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_module = alias.name.split(".")[0].lower()
                if root_module in BLOCKED_MODULES:
                    return f"Importing restricted module '{alias.name}' is prohibited."

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_module = node.module.split(".")[0].lower()
                if root_module in BLOCKED_MODULES:
                    return f"Importing from restricted module '{node.module}' is prohibited."

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "__import__":
                if node.args and isinstance(node.args[0], ast.Constant):
                    mod_name = str(node.args[0].value).split(".")[0].lower()
                    if mod_name in BLOCKED_MODULES:
                        return f"Dynamic import of restricted module '{mod_name}' is prohibited."

    return None
