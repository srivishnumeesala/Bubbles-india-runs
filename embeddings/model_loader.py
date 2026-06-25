# Technical Breakdown:
# - Loads the SentenceTransformer embedding model from the Hugging Face hub or local cache.
# - Pinned to the model specified in config/settings.py (default: all-MiniLM-L6-v2).
# - Uses functools.lru_cache(maxsize=1) to load the model exactly once per process.
# - Prevents reloading the SBERT weights across Streamlit script rerun cycles.

from functools import lru_cache
from config.settings import MODEL_NAME

@lru_cache(maxsize=1)
def get_model() -> "SentenceTransformer":
    from sentence_transformers import SentenceTransformer
    """Return the singleton SentenceTransformer model.

    Returns:
        SentenceTransformer: Loaded SBERT model.
    """
    # Load SentenceTransformer model
    model = SentenceTransformer(MODEL_NAME)
    return model
