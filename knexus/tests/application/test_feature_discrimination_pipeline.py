"""Extiende la discriminación de features (lección L6, MEMORY.md) al pipeline
REAL de Sprint-04 — no a una muestra armada a mano con seeds inyectados, sino a
lo que `descubrir_conexiones` de verdad produce para varias consultas reales.
"""
import collections

import pytest

from src.adapters.embeddings.hashing_provider import HashingProvider
from src.adapters.graph.networkx_store import NetworkXGraphStore
from src.adapters.repository.dataset_repository import DatasetEntityRepository
from src.adapters.retrieval.bm25_index import BM25Index
from src.adapters.retrieval.corpus import build_corpus
from src.adapters.retrieval.dense_index import DenseIndex
from src.application.descubrir_conexiones import descubrir_conexiones

MAX_SINGLE_VALUE_SHARE = 0.90
SAMPLE_NEEDS = ("NEED-001", "NEED-006", "NEED-012", "NEED-015", "NEED-024")


@pytest.fixture(scope="module")
def repo():
    return DatasetEntityRepository()


@pytest.fixture(scope="module")
def pipeline_vectors(repo):
    refs, texts = build_corpus(repo)
    dense = DenseIndex(HashingProvider(dim=256))
    dense.build(refs, texts, use_cache=False)
    lexical = BM25Index()
    lexical.build(refs, texts)
    graph = NetworkXGraphStore(repo)

    rows = []
    for need_id in SAMPLE_NEEDS:
        results = descubrir_conexiones(
            need_id, repo=repo, dense_index=dense, lexical_index=lexical, graph=graph,
        )
        rows.extend((r.entity.entity_type, r.scored.feature_vector) for r in results)
    return rows


# soporte_capacidad sólo puede ser True para PROJECT/THESIS — son los únicos
# tipos con `methods` minado (dataset_repository.METHOD_BEARING_TYPES). Medir
# su discriminación sobre la mezcla completa (mayormente NEED/RESEARCHER vía
# expansión de grafo) mediría la composición del pool, no la regla en sí —
# ya validada en Sprint-03 sobre los 320 proyectos (21.6%/78.4%).
_CAPABILITY_ELIGIBLE_TYPES = ("PROJECT", "THESIS")


@pytest.mark.parametrize("feature_name", (
    "sim_semantica", "compat_metodo", "compat_dominio",
    "densidad_evidencia", "enlace_estructural",
))
def test_pipeline_real_ninguna_feature_casi_constante(pipeline_vectors, feature_name):
    values = [getattr(fv, feature_name) for _, fv in pipeline_vectors]
    counts = collections.Counter(values)
    _, most_common_count = counts.most_common(1)[0]
    share = most_common_count / len(values)
    assert len(counts) > 1, f"{feature_name} tiene un único valor en el pipeline real"
    assert share <= MAX_SINGLE_VALUE_SHARE, (
        f"{feature_name} es casi-constante en el pipeline real: {share:.0%}"
    )


def test_pipeline_real_graph_linked_discrimina_en_ambos_sentidos(pipeline_vectors):
    values = {fv.enlace_estructural for _, fv in pipeline_vectors}
    assert values == {0.0, 1.0}, "enlace_estructural no discrimina en el pipeline real"


def test_pipeline_real_soporte_capacidad_discrimina_entre_candidatos_elegibles(pipeline_vectors):
    eligible = [fv for entity_type, fv in pipeline_vectors if entity_type in _CAPABILITY_ELIGIBLE_TYPES]
    assert eligible, "ningún candidato PROJECT/THESIS llegó al pipeline real"
    values = {fv.soporte_capacidad for fv in eligible}
    assert len(values) > 1, "soporte_capacidad no discrimina ni siquiera entre PROJECT/THESIS"
