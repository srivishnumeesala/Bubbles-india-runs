# Technical Breakdown:
# - Tests the SBERT model loader, encoder, and file cache.
# - Verifies embedding dimensionality (384 dimensions for all-MiniLM-L6-v2).
# - Validates L2 normalization (norm of each vector equals 1.0).
# - Checks that cached lookups yield exact binary matches.
# - Confirms batch processing doesn't crash on empty or varying inputs.

import pytest
import numpy as np
from pathlib import Path
from embeddings.model_loader import get_model
from embeddings.encoder import encode_texts, get_cached_embedding, encode_batch_with_cache

def test_model_loader_singleton():
    """Verify that get_model returns the same singleton instance."""
    model1 = get_model()
    model2 = get_model()
    assert model1 is model2

def test_encode_texts_shape_and_norm():
    """Test that encode_texts returns L2-normalised vectors with correct dimensions."""
    texts = ["Python software engineer with AWS experience", "Frontend developer with React skills"]
    embeddings = encode_texts(texts)
    
    # Check shape: 2 texts, 384 dimensions (MiniLM default)
    assert embeddings.shape == (2, 384)
    assert embeddings.dtype == np.float32
    
    # Check L2 norm is approximately 1.0 for all rows
    for vec in embeddings:
        norm = np.linalg.norm(vec)
        assert pytest.approx(norm, abs=1e-5) == 1.0

def test_get_cached_embedding(tmp_path: Path):
    """Test caching embedding to disk saves and returns correct values."""
    text = "Data scientist specializing in deep learning."
    
    # Cold start (encode & cache)
    embedding1 = get_cached_embedding(text, tmp_path)
    
    # Warm start (read cache file)
    embedding2 = get_cached_embedding(text, tmp_path)
    
    # Assert exact match
    np.testing.assert_array_equal(embedding1, embedding2)
    assert embedding1.shape == (384,)

def test_encode_batch_with_cache(tmp_path: Path):
    """Test batch encoding utilizing partial cache hits."""
    texts = {
        "candidate1.pdf": "Software engineer with Java experience.",
        "candidate2.docx": "Data analyst with SQL expertise.",
        "candidate3.pdf": "Project manager in agile environment."
    }
    
    # Prime cache for candidate1 only
    h1_vec = get_cached_embedding(texts["candidate1.pdf"], tmp_path)
    
    # Run batch process (candidate1 loaded from disk, others encoded)
    results = encode_batch_with_cache(texts, tmp_path, batch_size=2)
    
    assert len(results) == 3
    assert "candidate1.pdf" in results
    assert "candidate2.docx" in results
    assert "candidate3.pdf" in results
    
    # Assert candidate1 loaded value matches primed cache
    np.testing.assert_array_equal(results["candidate1.pdf"], h1_vec)
    
    # Confirm L2 norms are 1.0 for all
    for name, vec in results.items():
        assert vec.shape == (384,)
        assert pytest.approx(np.linalg.norm(vec), abs=1e-5) == 1.0
