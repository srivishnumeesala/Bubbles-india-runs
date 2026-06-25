"""
Central configuration — all magic strings live here.
Loaded from environment variables with sensible defaults.
Academic supervisor: change MODEL_NAME to swap the embedding model.
"""

# Technical Breakdown:
# - Loads settings from .env file using python-dotenv.
# - Provides fallback defaults to ensure stability even without .env.
# - Parses string values to float/Path types where required.
# - Autocreates all output/cache/logging directories at load time to avoid FileNotFoundError downstream.

from pathlib import Path
from dotenv import load_dotenv
import os

# Identify root directory of the project
ROOT_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(dotenv_path=ROOT_DIR / ".env")

MODEL_NAME: str = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")

# Paths relative to project root by default
RESUME_DIR: Path = ROOT_DIR / Path(os.getenv("RESUME_DIR", "data/resumes"))
JD_DIR: Path = ROOT_DIR / Path(os.getenv("JD_DIR", "data/job_descriptions"))
OUTPUT_DIR: Path = ROOT_DIR / Path(os.getenv("OUTPUT_DIR", "data/outputs"))
CACHE_DIR: Path = ROOT_DIR / Path(os.getenv("CACHE_DIR", "data/cache"))
LOG_DIR: Path = ROOT_DIR / Path(os.getenv("LOG_DIR", "data/logs"))
LOG_FILE: Path = LOG_DIR / "failed_files.log"

THRESHOLD: float = float(os.getenv("THRESHOLD", "60.0"))
BIAS_DELTA_THRESHOLD: float = float(os.getenv("BIAS_DELTA_THRESHOLD", "10.0"))
INFERRED_SIMILARITY_THRESHOLD: float = float(os.getenv("INFERRED_SIMILARITY_THRESHOLD", "0.75"))
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# Predefined keywords for gap analysis/JD parsing if not extracted
DEFAULT_KEYWORD_CATEGORIES: dict[str, list[str]] = {
    "tech_stack": [
        "python", "java", "c++", "javascript", "typescript", "golang", "rust", "sql", "nosql",
        "react", "angular", "vue", "node", "django", "flask", "fastapi", "spring", "docker",
        "kubernetes", "aws", "gcp", "azure", "pytorch", "tensorflow", "scikit-learn", "pandas",
        "numpy", "spark", "hadoop", "git", "ci/cd"
    ],
    "soft_skills": [
        "communication", "leadership", "teamwork", "problem solving", "critical thinking",
        "time management", "adaptability", "mentoring", "collaboration", "agile"
    ],
    "certifications": [
        "aws certified", "gcp certified", "azure certified", "pmp", "csm", "scrum master",
        "cissp", "ceh"
    ],
    "education": [
        "bachelor", "master", "phd", "computer science", "engineering", "data science",
        "mathematics", "physics"
    ]
}

# Demographic and institutional proxy keywords for bias auditing
DEMOGRAPHIC_PROXY_TERMS: dict[str, list[str]] = {
    "institution_prestige": [
        "harvard", "oxford", "cambridge", "mit", "stanford",
        "ivy league", "oxbridge", "russell group", "iit"
    ],
    "graduation_year": [
        r"\b(19[6-9]\d|200\d|201[0-5])\b"   # Flags graduation years that imply age
    ],
    "cultural_name_markers": [],  # Left empty by default — requires expert review to populate
}

# Ensure directories exist at import time
for _dir in [RESUME_DIR, JD_DIR, OUTPUT_DIR, CACHE_DIR, LOG_DIR]:
    _dir.mkdir(parents=True, exist_ok=True)
