"""Caché de vectores densos: evita recodificar ~14.000 textos (~40s con el
modelo real) en cada arranque. Verifica HIT real (no solo que el resultado sea
determinista — HashingProvider ya lo es de por sí)."""
import numpy as np
import pytest

from src.adapters.retrieval import vector_cache
from src.adapters.retrieval.dense_index import DenseIndex


class _CountingProvider:
    """Envuelve HashingProvider y cuenta cuántas veces se llamó a encode()."""

    def __init__(self, dim=32):
        from src.adapters.embeddings.hashing_provider import HashingProvider
        self._inner = HashingProvider(dim=dim)
        self.encode_calls = 0

    @property
    def dimension(self):
        return self._inner.dimension

    @property
    def name(self):
        return self._inner.name

    def encode(self, texts):
        self.encode_calls += 1
        return self._inner.encode(texts)


@pytest.fixture
def isolated_cache_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(vector_cache, "CACHE_DIR", tmp_path)
    return tmp_path


def test_segundo_build_hace_hit_de_cache_no_recalcula(isolated_cache_dir):
    provider = _CountingProvider()
    texts = ("deserción estudiantil", "student attrition", "optimización logística")

    idx1 = DenseIndex(provider)
    idx1.build(("A", "B", "C"), texts)
    assert provider.encode_calls == 1

    idx2 = DenseIndex(provider)
    idx2.build(("A", "B", "C"), texts)
    assert provider.encode_calls == 1, "el segundo build debió cargar de caché, no recalcular"

    # y los resultados de búsqueda son idénticos entre ambos índices
    assert idx1.search("deserción estudiantil", k=3) == idx2.search("deserción estudiantil", k=3)


def test_cambiar_el_corpus_invalida_la_cache(isolated_cache_dir):
    provider = _CountingProvider()
    idx = DenseIndex(provider)

    idx.build(("A", "B"), ("texto uno", "texto dos"))
    assert provider.encode_calls == 1

    idx.build(("A", "B"), ("texto uno", "texto DISTINTO"))
    assert provider.encode_calls == 2, "un corpus distinto debe recalcular, no reusar caché vieja"


def test_cambiar_el_modelo_invalida_la_cache(isolated_cache_dir):
    provider_a = _CountingProvider(dim=32)
    provider_b = _CountingProvider(dim=64)  # distinto `name` -> distinta clave
    texts = ("mismo texto",)

    DenseIndex(provider_a).build(("A",), texts)
    DenseIndex(provider_b).build(("A",), texts)

    assert provider_a.encode_calls == 1
    assert provider_b.encode_calls == 1  # no reusó la caché de provider_a


def test_load_directo_retorna_none_si_no_hay_cache(isolated_cache_dir):
    assert vector_cache.load("modelo-inexistente", ("x",)) is None


def test_save_y_load_producen_vectores_identicos(isolated_cache_dir):
    vectors = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], dtype="float32")
    vector_cache.save("modelo-x", ("t1", "t2"), vectors)
    loaded = vector_cache.load("modelo-x", ("t1", "t2"))
    assert loaded is not None
    assert np.array_equal(loaded, vectors)
