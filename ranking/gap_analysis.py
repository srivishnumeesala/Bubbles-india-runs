# Technical Breakdown:
# - Performs analysis of skills gaps by comparing Job Description (JD) keywords against resume content.
# - Leverages spaCy noun chunks to extract noun phrases from the JD and combines them with a predefined tech-term list.
# - Classifies each skill as:
#   (a) PRESENT: Literal match found in the resume.
#   (b) INFERRED: Not literally present, but semantic similarity (keyword vector vs. resume vector) >= threshold.
#   (c) ABSENT: No literal or semantic match found.
# - Calculates an overall gap_score based on weighted scores (Present=100%, Inferred=50%, Missing=0%).
# - Caches keyword embeddings in memory to accelerate classification.

import re
import numpy as np
from typing import Dict, List, Literal
from ranking import GapReport
from embeddings.encoder import encode_texts
from config.settings import DEFAULT_KEYWORD_CATEGORIES, INFERRED_SIMILARITY_THRESHOLD

# Lazy load spaCy model
_nlp = None

def _get_nlp():
    global _nlp
    if _nlp is None:
        import spacy
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Auto-download if missing
            import subprocess
            import sys
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], capture_output=True)
            _nlp = spacy.load("en_core_web_sm")
    return _nlp

# In-memory cache for keyword embeddings to prevent redundant encoding calls
_keyword_cache: Dict[str, np.ndarray] = {}

def get_keyword_embedding(keyword: str) -> np.ndarray:
    """Get the cached embedding of a keyword, or encode it if missing."""
    if keyword not in _keyword_cache:
        emb = encode_texts([keyword])[0]
        _keyword_cache[keyword] = emb
    return _keyword_cache[keyword]

def extract_jd_keywords(jd_text: str) -> Dict[str, List[str]]:
    """Extract domain keywords from JD grouped by category.

    Uses spaCy noun chunks combined with default keyword lists in config/settings.py.

    Args:
        jd_text (str): Raw text of the job description.

    Returns:
        Dict[str, List[str]]: Dictionary mapping categories to lists of keywords.
    """
    nlp = _get_nlp()
    doc = nlp(jd_text.lower())
    
    extracted: Dict[str, List[str]] = {
        "tech_stack": [],
        "soft_skills": [],
        "certifications": [],
        "education": []
    }

    # 1. Match predefined terms from central configuration
    for category, keywords in DEFAULT_KEYWORD_CATEGORIES.items():
        for kw in keywords:
            # Match keyword with word boundaries to avoid partial word overlaps (e.g. 'go' matching 'django')
            # For keywords like 'c++', '.net', 'ci/cd', word boundaries can be tricky, so try word boundary
            # and fallback to simple matching if punctuation is in keyword.
            if any(char in kw for char in ['+', '#', '.', '/']):
                # Contain punctuation, search with exact substring check with surrounding spaces or start/end
                pattern = r'(?:^|\s|[.,()\/])' + re.escape(kw) + r'(?:$|\s|[.,()\/])'
            else:
                pattern = r'\b' + re.escape(kw) + r'\b'

            if re.search(pattern, jd_text.lower()):
                if kw not in extracted[category]:
                    extracted[category].append(kw)

    # 2. Match noun chunks dynamically to identify additional skills
    ignore_nouns = {
        "role", "team", "experience", "candidate", "client", "position", "company", 
        "description", "year", "years", "knowledge", "ability", "skills", "developer", 
        "engineer", "we", "us", "job", "responsibilities", "requirements", "details",
        "duties", "application", "resume", "work", "environment"
    }

    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.strip().lower()
        # Clean double spaces
        chunk_text = re.sub(r'\s+', ' ', chunk_text)
        
        # Only check short noun chunks (1-2 words) that don't match stopwords
        if 2 < len(chunk_text) < 30 and len(chunk_text.split()) <= 2:
            # Skip if it is a stopword or contains digits
            if nlp.vocab[chunk_text].is_stop or any(char.isdigit() for char in chunk_text):
                continue
                
            if chunk_text in ignore_nouns:
                continue

            # Check if this term was already caught by predefined categories
            found = False
            for cat in extracted:
                if chunk_text in extracted[cat]:
                    found = True
                    break
            
            if not found:
                # Dynamically classify under tech_stack as default
                extracted["tech_stack"].append(chunk_text)

    # Sort each list alphabetically
    for cat in extracted:
        extracted[cat] = sorted(list(set(extracted[cat])))

    return extracted

def classify_keyword(
    keyword: str,
    resume_text: str,
    resume_embedding: np.ndarray,
    threshold_inferred: float = INFERRED_SIMILARITY_THRESHOLD,
) -> Literal["present", "absent", "inferred"]:
    """Classify keyword presence in resume text.

    Args:
        keyword (str): The keyword to check.
        resume_text (str): The cleaned text of the resume.
        resume_embedding (np.ndarray): Embedding vector of the resume.
        threshold_inferred (float): Cosine similarity threshold for inference.

    Returns:
        Literal["present", "absent", "inferred"]: Classification.
    """
    keyword_lower = keyword.lower()
    resume_lower = resume_text.lower()

    # 1. Check PRESENT: Literal check
    # Check with word boundaries or substring match (handling c++, .net, etc.)
    if any(char in keyword_lower for char in ['+', '#', '.', '/']):
        pattern = r'(?:^|\s|[.,()\/])' + re.escape(keyword_lower) + r'(?:$|\s|[.,()\/])'
    else:
        pattern = r'\b' + re.escape(keyword_lower) + r'\b'

    if re.search(pattern, resume_lower):
        return "present"

    # 2. Check INFERRED: Semantic check using cosine similarity
    try:
        kw_vector = get_keyword_embedding(keyword_lower)
        
        # Norms
        kw_norm = np.linalg.norm(kw_vector)
        res_norm = np.linalg.norm(resume_embedding)
        
        if kw_norm > 0 and res_norm > 0:
            sim = float(np.dot(kw_vector, resume_embedding) / (kw_norm * res_norm))
        else:
            sim = 0.0

        if sim >= threshold_inferred:
            return "inferred"
    except Exception:
        # Fallback if encoding fails
        pass

    return "absent"

def build_gap_report(
    jd_keywords: Dict[str, List[str]],
    resume_text: str,
    resume_embedding: np.ndarray,
) -> GapReport:
    """Build a full GapReport for one candidate.

    Args:
        jd_keywords (Dict[str, List[str]]): Extracted JD keywords by category.
        resume_text (str): Candidate's cleaned resume text.
        resume_embedding (np.ndarray): Candidate's resume embedding.

    Returns:
        GapReport: The built GapReport.
    """
    # Flatten JD keywords to a single unique list
    all_keywords = set()
    for keywords in jd_keywords.values():
        all_keywords.update(keywords)

    present_skills = []
    missing_skills = []
    inferred_skills = []

    for kw in all_keywords:
        status = classify_keyword(kw, resume_text, resume_embedding)
        if status == "present":
            present_skills.append(kw)
        elif status == "inferred":
            inferred_skills.append(kw)
        else:
            missing_skills.append(kw)

    # Sort alphabetically
    present_skills.sort()
    missing_skills.sort()
    inferred_skills.sort()

    # Calculate gap score
    total = len(all_keywords)
    if total > 0:
        score = (len(present_skills) * 1.0 + len(inferred_skills) * 0.5) / total * 100.0
        gap_score = round(max(0.0, min(100.0, score)), 2)
    else:
        gap_score = 100.0

    return GapReport(
        present_skills=present_skills,
        missing_skills=missing_skills,
        inferred_skills=inferred_skills,
        gap_score=gap_score
    )
