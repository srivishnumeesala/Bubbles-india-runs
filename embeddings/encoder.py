# Technical Breakdown:
# - Connects to the cached SentenceTransformer model singleton.
# - Encodes list of texts into L2-normalized embedding vectors.
# - L2-normalization ensures that cosine similarity reduces to a fast dot product: dot(a, b).
# - Implements SHA-256 hash-keyed caching of embeddings to prevent re-encoding identical resumes.
# - Stores cached embeddings as NumPy binary files (.npy) in the cache directory.
# - Provides batch encoding that skips already cached files, only running model inference on new/modified text.

import hashlib
from pathlib import Path
import numpy as np
from typing import Dict, List
from embeddings.model_loader import get_model

def encode_texts(
    texts: List[str],
    batch_size: int = 32,
    show_progress_bar: bool = False,
) -> np.ndarray:
    """Encode a list of texts into L2-normalised embedding vectors.

    Args:
        texts (List[str]): List of cleaned texts.
        batch_size (int, optional): Size of processing batches. Defaults to 32.
        show_progress_bar (bool, optional): Whether to display encoding progress. Defaults to False.

    Returns:
        np.ndarray: Matrix of shape (len(texts), embedding_dim) of float32.
    """
    if not texts:
        return np.empty((0, 384), dtype=np.float32)  # Fallback for empty list

    model = get_model()
    # normalize_embeddings=True outputs L2-normalised vectors
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=show_progress_bar,
        normalize_embeddings=True
    )
    return np.array(embeddings, dtype=np.float32)

def get_cached_embedding(text: str, cache_dir: Path) -> np.ndarray:
    """Return cached embedding if available, else encode and cache.

    Cache key: SHA-256 hash of the cleaned text string.
    Cache file: {cache_dir}/{hash}.npy

    Args:
        text (str): Cleaned text to represent.
        cache_dir (Path): Directory where cache files are located.

    Returns:
        np.ndarray: Vector of shape (embedding_dim,).
    """
    # Create clean string hash
    text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
    cache_path = Path(cache_dir) / f"{text_hash}.npy"

    if cache_path.exists():
        try:
            return np.load(cache_path)
        except Exception:
            # If load fails (e.g. file corrupted), re-encode
            pass

    # Encode single text
    embedding = encode_texts([text])[0]

    # Save to disk
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(cache_path, embedding)
    except Exception:
        # Proceed even if cache write fails
        pass

    return embedding

def encode_batch_with_cache(
    texts: Dict[str, str],
    cache_dir: Path,
    batch_size: int = 32,
) -> Dict[str, np.ndarray]:
    """Encode only uncached texts; load the rest from disk.

    Args:
        texts (Dict[str, str]): Mapping of identifier (e.g. filename) to cleaned text.
        cache_dir (Path): Directory to cache embeddings.
        batch_size (int, optional): Size of processing batches. Defaults to 32.

    Returns:
        Dict[str, np.ndarray]: Mapping of identifier to embedding vector.
    """
    cache_path_obj = Path(cache_dir)
    cache_path_obj.mkdir(parents=True, exist_ok=True)

    results: Dict[str, np.ndarray] = {}
    
    # 1. Identify which texts are already cached vs uncached
    uncached_keys: List[str] = []
    uncached_texts: List[str] = []
    text_hashes: Dict[str, str] = {}

    for key, text in texts.items():
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        text_hashes[key] = text_hash
        file_path = cache_path_obj / f"{text_hash}.npy"
        
        if file_path.exists():
            try:
                results[key] = np.load(file_path)
            except Exception:
                # If loading fails, treat as uncached
                uncached_keys.append(key)
                uncached_texts.append(text)
        else:
            uncached_keys.append(key)
            uncached_texts.append(text)

    # 2. Batch encode the uncached texts
    if uncached_texts:
        encoded_vectors = encode_texts(uncached_texts, batch_size=batch_size)
        for idx, key in enumerate(uncached_keys):
            vec = encoded_vectors[idx]
            results[key] = vec
            
            # Save to cache
            h = text_hashes[key]
            file_path = cache_path_obj / f"{h}.npy"
            try:
                np.save(file_path, vec)
            except Exception:
                pass

    return results
