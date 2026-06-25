---
name: python-type-enforcer
description: Enforces type hints on every function signature for Python modules.
---
# Python Type Enforcer Skill

## Instructions
1. For all Python function declarations, always provide explicit parameter and return type annotations.
2. Example:
   ```python
   def extract_pdf(path: Path) -> str:
       ...
   ```
3. Avoid using `Any` where possible. Instead, define strict union types or standard typing classes like `dict`, `list`, `tuple`, `Callable`, `Literal`.
4. Include docstrings in Google style outlining `Args`, `Returns`, and `Raises`.
