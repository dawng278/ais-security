import re
from typing import Any, Dict, List, Tuple
from app.firewall.prototypes import PROMPT_INJECTION_PROTOTYPES

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    MODEL_AVAILABLE = True
    IMPORT_ERROR = ""
except Exception as e:
    MODEL_AVAILABLE = False
    IMPORT_ERROR = str(e)
    print(f"Warning: sentence-transformers or numpy not available ({e}). Embedding detector running in fallback mode.")

_MODEL_CACHE = None
_MODEL_LOAD_ERROR = ""


def get_embedding_model():
    global _MODEL_CACHE, _MODEL_LOAD_ERROR
    import os
    if not MODEL_AVAILABLE or os.environ.get("OFFLINE_MODE") == "true":
        return None
    if _MODEL_CACHE is None:
        try:
            # Load lightweight multilingual model
            _MODEL_CACHE = SentenceTransformer(MODEL_NAME)
            _MODEL_LOAD_ERROR = ""
        except Exception as e:
            _MODEL_LOAD_ERROR = str(e)
            print(f"Warning: Failed to load SentenceTransformer model ({e}).")
            _MODEL_CACHE = None
    return _MODEL_CACHE


def get_embedding_detector_health(load_model: bool = False) -> Dict[str, Any]:
    if not MODEL_AVAILABLE:
        return {
            "configured_state": "enabled",
            "dependency_state": "missing",
            "model_load_state": "not_attempted",
            "runtime_state": "unavailable",
            "model_name": MODEL_NAME,
            "fallback_reason": IMPORT_ERROR or "sentence-transformers or numpy not available",
        }

    model = get_embedding_model() if load_model else _MODEL_CACHE
    if model is not None:
        return {
            "configured_state": "enabled",
            "dependency_state": "available",
            "model_load_state": "loaded",
            "runtime_state": "healthy",
            "model_name": MODEL_NAME,
            "fallback_reason": "",
        }

    if _MODEL_LOAD_ERROR:
        return {
            "configured_state": "enabled",
            "dependency_state": "available",
            "model_load_state": "failed",
            "runtime_state": "unavailable",
            "model_name": MODEL_NAME,
            "fallback_reason": _MODEL_LOAD_ERROR,
        }

    return {
        "configured_state": "enabled",
        "dependency_state": "available",
        "model_load_state": "not_loaded",
        "runtime_state": "warming",
        "model_name": MODEL_NAME,
        "fallback_reason": "model has not been loaded in this process",
    }


def chunk_text(text: str, window_size: int = 3, stride: int = 2) -> List[str]:
    """Splits long essays into overlapping sentence chunks."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return [text]
    
    chunks = []
    for i in range(0, len(sentences), stride):
        chunk = " ".join(sentences[i:i+window_size])
        if chunk:
            chunks.append(chunk)
    return chunks if chunks else [text]


def compute_semantic_similarity(text: str) -> Tuple[float, str]:
    """Calculates max cosine similarity between text chunks and attack prototypes."""
    model = get_embedding_model()
    if model is None:
        # Fallback keyword overlap heuristic if embedding model fails to load
        text_lower = text.lower()
        matches = [p for p in PROMPT_INJECTION_PROTOTYPES if p in text_lower]
        score = 0.85 if matches else 0.1
        return score, matches[0] if matches else ""

    chunks = chunk_text(text)
    try:
        chunk_embeddings = model.encode(chunks, normalize_embeddings=True)
        proto_embeddings = model.encode(PROMPT_INJECTION_PROTOTYPES, normalize_embeddings=True)

        # Cosine similarity matrix: shape (num_chunks, num_prototypes)
        sim_matrix = np.dot(chunk_embeddings, proto_embeddings.T)
        max_idx = np.unravel_index(np.argmax(sim_matrix), sim_matrix.shape)
        
        max_score = float(sim_matrix[max_idx])
        matched_proto = PROMPT_INJECTION_PROTOTYPES[max_idx[1]]
        return round(max_score, 4), matched_proto
    except Exception as e:
        print(f"Embedding calculation error: {e}")
        return 0.1, ""
