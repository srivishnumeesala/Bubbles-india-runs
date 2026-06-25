# AGENTS.md — Semantic Resume Ranker

## Global Conventions
- Python style: PEP 8, type hints on every function
- Test command: pytest tests/ -v
- Commit style: feat(scope): message
- Log file for errors: data/logs/failed_files.log

## Agent Ownership Map
| Agent     | Owned Directories                          |
|-----------|--------------------------------------------|
| Planner   | / (root only — AGENTS.md, README, requirements, .env.example) |
| Parser    | parsers/                                   |
| Embedder  | embeddings/                                |
| Ranker    | ranking/                                   |
| UI        | ui/                                        |
| Tester    | tests/                                     |

## Phase Gate Rule
Each agent MUST run pytest on its owned test file(s) and paste the full terminal
output as a Verification Artifact before the next agent starts.

## Antigravity-Specific Notes
- Use st.cache_resource for ModelLoader singleton
- Use st.cache_data for encode_texts
- All spinner text: st.spinner("Analysing…")
- Browser agent verifies localhost:8501 after ui/ phase
