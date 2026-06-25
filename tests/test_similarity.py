# Technical Breakdown:
# - Tests similarity computation and candidate scoring.
# - Validates sorting order and 1-based ranking.
# - Asserts exact similarity boundaries (identical vectors = 100.0, orthogonal vectors = 0.0).

import pytest
import numpy as np
from ranking.similarity import compute_fit_scores

def test_compute_fit_scores_identical():
    """Test that identical embeddings yield a score of 100.0."""
    jd_vector = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    resume_embeddings = {
        "candidate_perfect.pdf": np.array([1.0, 0.0, 0.0], dtype=np.float32)
    }
    
    results = compute_fit_scores(jd_vector, resume_embeddings)
    assert len(results) == 1
    assert results[0].fit_score == 100.0
    assert results[0].rank == 1

def test_compute_fit_scores_orthogonal():
    """Test that orthogonal embeddings yield a score of 0.0."""
    jd_vector = np.array([1.0, 0.0], dtype=np.float32)
    resume_embeddings = {
        "candidate_orthogonal.pdf": np.array([0.0, 1.0], dtype=np.float32)
    }
    
    results = compute_fit_scores(jd_vector, resume_embeddings)
    assert len(results) == 1
    assert results[0].fit_score == 0.0
    assert results[0].rank == 1

def test_compute_fit_scores_sorting_and_ranking():
    """Test sorting by score and correct rank assignment."""
    jd_vector = np.array([1.0, 0.0], dtype=np.float32)
    resume_embeddings = {
        "low_fit.pdf": np.array([0.2, 0.98], dtype=np.float32),      # similarity = 0.2
        "high_fit.pdf": np.array([0.9, 0.436], dtype=np.float32),    # similarity = 0.9
        "mid_fit.pdf": np.array([0.5, 0.866], dtype=np.float32)      # similarity = 0.5
    }
    
    results = compute_fit_scores(jd_vector, resume_embeddings)
    assert len(results) == 3
    
    # Check sorting order: high -> mid -> low
    assert results[0].name == "High Fit"
    assert results[0].rank == 1
    assert results[0].fit_score == 90.0
    
    assert results[1].name == "Mid Fit"
    assert results[1].rank == 2
    assert results[1].fit_score == 50.0
    
    assert results[2].name == "Low Fit"
    assert results[2].rank == 3
    assert results[2].fit_score == 20.0
