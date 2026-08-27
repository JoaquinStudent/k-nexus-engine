"""Pipeline completo (Sprint-04): recuperación híbrida + reranking, offline
(HashingProvider, sin red). Los tests marcados `slow` validan con BM25/denso
reales adicionales cuando aplica."""
import pytest

from src.adapters.embeddings.hashing_provider import HashingProvider
from src.adapters.graph.networkx_store import NetworkXGraphStore
from src.adapters.repository.dataset_repository import DatasetEntityRepository
from src.adapters.retrieval.bm25_index import BM25Index
from src.adapters.retrieval.corpus import build_corpus
from src.adapters.retrieval.dense_index import DenseIndex
from src.application.descubrir_conexiones import descubrir_conexiones
from src.domain.scoring import compute_score


@pytest.fixture(scope="module")
def repo():
    return DatasetEntityRepository()


@pytest.fixture(scope="module")
def pipeline(repo):
    refs, texts = build_corpus(repo)
    dense = DenseIndex(HashingProvider(dim=256))
    dense.build(refs, texts, use_cache=False)
    lexical = BM25Index()
    lexical.build(refs, texts)
    graph = NetworkXGraphStore(repo)
    return {"repo": repo, "dense_index": dense, "lexical_index": lexical, "graph": graph}


def test_need001_devuelve_resultados_rankeados(pipeline):
    results = descubrir_conexiones("NEED-001", **pipeline)
    assert results
    assert [r.rank for r in results] == list(range(1, len(results) + 1))
    scores = [r.scored.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_prj004_aparece_con_compat_metodo_vivo_y_evidencia_trazable(pipeline):
    results = descubrir_conexiones("NEED-001", **pipeline)
    prj004 = next(r for r in results if r.entity.entity_id == "PRJ-004")
    assert prj004.scored.feature_vector.compat_metodo is not None
    assert prj004.scored.feature_vector.compat_metodo > 0
    assert prj004.evidence.entity_id == "PRJ-004"
    assert prj004.evidence.field_name
    assert prj004.evidence.source_file
    assert prj004.evidence_text  # el texto del campo, no solo su referencia


def test_rrf_no_contamina_el_score(pipeline):
    """★ Invariante central del sprint: el score final es EXCLUSIVAMENTE
    compute_score(feature_vector) — el rrf_score de fusión nunca entra ahí."""
    results = descubrir_conexiones("NEED-001", **pipeline)
    assert results
    for connection in results:
        assert connection.scored.score == compute_score(connection.scored.feature_vector)


def test_need_no_se_autoincluye_en_sus_resultados(pipeline):
    results = descubrir_conexiones("NEED-001", **pipeline)
    assert all(r.entity.entity_id != "NEED-001" for r in results)


def test_texto_libre_infiere_senal_y_no_revienta(pipeline):
    results = descubrir_conexiones("predicción y prevención de deserción estudiantil", **pipeline)
    assert results
    # con problem_type inferido, compat_metodo debe poder salir de N/A para
    # candidatos con método real minado.
    assert any(r.scored.feature_vector.compat_metodo is not None for r in results)


def test_graph_linked_surge_en_produccion_sin_seeds_a_mano(pipeline):
    """Cierra el pendiente de Sprint-03: los seed_ids salen del propio
    pipeline (top-K de la pasada 1), no de un `seed_ids=(...)` inyectado a
    mano en un test."""
    results = descubrir_conexiones("NEED-001", **pipeline)
    researchers_linked = [
        r for r in results
        if r.entity.entity_type == "RESEARCHER" and r.scored.feature_vector.enlace_estructural == 1.0
    ]
    assert researchers_linked, "ningún investigador quedó enlazado en producción"
    for r in researchers_linked:
        assert r.scored.relation_type == "investigador_complementario"


def test_top_features_son_datos_no_prosa(pipeline):
    results = descubrir_conexiones("NEED-001", **pipeline)
    prj004 = next(r for r in results if r.entity.entity_id == "PRJ-004")
    assert prj004.top_features
    for name, value, contribution in prj004.top_features:
        assert name in ("sim_semantica", "sim_lexica", "compat_metodo", "compat_dominio",
                         "densidad_evidencia", "soporte_capacidad", "enlace_estructural")
        assert isinstance(value, float)
        assert isinstance(contribution, float)


def test_las_42_necesidades_responden_sin_reventar(pipeline):
    repo = pipeline["repo"]
    for need in repo.by_type("NEED"):
        results = descubrir_conexiones(need.entity_id, **pipeline)
        assert isinstance(results, tuple)
        # no todas tendrán resultados no-triviales, pero ninguna debe reventar
        # ni devolver algo que no sea una tupla de RankedConnection coherente.
        for r in results:
            assert r.scored.score == compute_score(r.scored.feature_vector)
