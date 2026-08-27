"""Caché en disco de vectores densos: evita recodificar los ~14.000 textos del
corpus (~40s con el modelo real) en cada arranque. Clave = modelo + hash del
contenido del corpus, así que un dataset o un modelo distinto invalida solo.
"""
import hashlib
import pathlib

import numpy as np

CACHE_DIR = pathlib.Path(__file__).resolve().parents[3] / ".cache" / "vectors"


def _cache_key(model_name: str, texts: tuple) -> str:
    digest = hashlib.sha256()
    digest.update(model_name.encode("utf-8"))
    for text in texts:
        digest.update(b"\x00")
        digest.update(text.encode("utf-8"))
    return digest.hexdigest()[:16]


def _cache_path(model_name: str, texts: tuple) -> pathlib.Path:
    safe_model = "".join(c if c.isalnum() else "_" for c in model_name)
    return CACHE_DIR / f"{safe_model}_{_cache_key(model_name, texts)}.npy"


def load(model_name: str, texts: tuple):
    """Retorna el array cacheado, o None si no hay caché válida para esta
    combinación exacta de modelo + contenido del corpus."""
    path = _cache_path(model_name, texts)
    if not path.exists():
        return None
    return np.load(path)


def save(model_name: str, texts: tuple, vectors: np.ndarray) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _cache_path(model_name, texts)
    np.save(path, vectors)
