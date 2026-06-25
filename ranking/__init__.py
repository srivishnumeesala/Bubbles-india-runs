# Technical Breakdown:
# - Centralizes data models using standard python dataclasses.
# - Provides clean containers for candidate metrics, gaps, and bias reports.
# - Enables type enforcement across parsing, embedding, ranking, and UI layers.

from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class GapReport:
    present_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    inferred_skills: list[str] = field(default_factory=list)   # Semantic match but not literal keyword match
    gap_score: float = 0.0                                     # 0–100; higher = fewer gaps

@dataclass
class CandidateResult:
    name: str
    file_path: Path
    fit_score: float              # 0–100, rounded to 2 dp
    rank: int
    gap_report: GapReport

@dataclass
class BiasAuditReport:
    flagged: bool
    proxy_keywords_found: list[str] = field(default_factory=list)
    correlation_summary: str = ""      # Human-readable explanation
    recommendation: str = ""
