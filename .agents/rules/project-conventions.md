# Project Conventions — Semantic Resume Ranker
- Language: Python 3.11+, PEP 8, type hints on every function signature
- Test runner: pytest tests/ -v (all tests must pass before Phase advance)
- Commit style: feat(scope): message | fix(scope): message | test(scope): message
- No agent modifies a directory it does not own (see ownership map in AGENTS.md)
- All heavy computation must be wrapped in try/except with structured logging
- No hard-coded strings — all config values live in config/settings.py
- Docstring format: Google-style (Args / Returns / Raises)
- Every new module gets a Technical Breakdown comment block at the top
