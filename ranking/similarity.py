# Technical Breakdown:
# - Computes semantic match scores between the job description and candidate resumes.
# - Leverages standard vector dot product (cosine similarity since vectors are L2-normalised).
# - Scales cosine similarities from range [-1, 1] to [0, 100] fit scores.
# - Orders candidates by fit score descending and assigns 1-based rankings.

import numpy as np
from pathlib import Path
from typing import Dict, List
from ranking import CandidateResult, GapReport
from config.settings import RESUME_DIR

def compute_fit_scores(
    jd_embedding: np.ndarray,
    resume_embeddings: Dict[str, np.ndarray],
) -> List[CandidateResult]:
    """Compute cosine similarity between JD and each resume.

    Scales to 0-100 Fit Score (similarity * 100, rounded to 2 dp).
    Returns list sorted by fit_score descending, rank assigned 1-based.

    Args:
        jd_embedding (np.ndarray): JD embedding vector of shape (embedding_dim,).
        resume_embeddings (Dict[str, np.ndarray]): Mapping of filename to resume embedding vector.

    Returns:
        List[CandidateResult]: Sorted list of candidate results.
    """
    results: List[CandidateResult] = []

    # If inputs are empty, return empty list
    if len(resume_embeddings) == 0:
        return results

    # Normalize JD embedding if not already done (for safety)
    jd_norm = np.linalg.norm(jd_embedding)
    if jd_norm > 0:
        jd_vector = jd_embedding / jd_norm
    else:
        jd_vector = jd_embedding

    for filename, embedding in resume_embeddings.items():
        # Normalize resume embedding for safety
        emb_norm = np.linalg.norm(embedding)
        if emb_norm > 0:
            emb_vector = embedding / emb_norm
        else:
            emb_vector = embedding

        # Calculate dot product (equal to cosine similarity for L2-normalised vectors)
        similarity = float(np.dot(jd_vector, emb_vector))
        
        # Scale to 0-100, clipping to be safe
        fit_score = max(0.0, min(100.0, similarity * 100.0))
        fit_score = round(fit_score, 2)
        
        # Determine paths
        file_path = RESUME_DIR / filename
        name = Path(filename).stem.replace("_", " ").title()

        results.append(CandidateResult(
            name=name,
            file_path=file_path,
            fit_score=fit_score,
            rank=-1,  # Temporary placeholder
            gap_report=GapReport()  # Default empty GapReport
        ))

    # Sort results by fit score descending
    results.sort(key=lambda x: x.fit_score, reverse=True)

    # Assign 1-based rank
    for idx, candidate in enumerate(results):
        candidate.rank = idx + 1

    return results
