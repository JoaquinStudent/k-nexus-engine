"""auditar_resultado.py — "¿por qué A antes que B?" (módulo M7 de DESIGN.md)."""
import pytest

from src.adapters.embeddings.hashing_provider import HashingProvider
from src.adapters.graph.networkx_store import NetworkXGraphStore
from src.adapters.repository.dataset_repository import DatasetEntityRepository
from src.adapters.retrieval.bm25_index import BM25Index
from src.adapters.retrieval.corpus import build_corpus
from src.adapters.retrieval.dense_index import DenseIndex
from src.application.auditar_resultado import comparar
from src.application.descubrir_conexiones import descubrir_conexiones


@pytest.fixture(scope="module")
def repo():
    return DatasetEntityRepository()


@pytest.fixture(scope="module")
def results(repo):
    refs, texts = build_corpus(repo)
    dense = DenseIndex(HashingProvider(dim=256))
    dense.build(refs, texts, use_cache=False)
    lexical = BM25Index()
    lexical.build(refs, texts)
    graph = NetworkXGraphStore(repo)
    return descubrir_conexiones("NEED-001", repo=repo, dense_index=dense, lexical_index=lexical, graph=graph)


def _find(results, entity_id):
    return next(r for r in results if r.entity.entity_id == entity_id)


def test_comparador_prj004_vs_prj002_identifica_compat_metodo(results):
    """★ PRJ-004 (clasificación supervisada, 0.90) vs PRJ-002 (analítica
    educativa, 0.70) — coincide con la frase de defensa de DESIGN.md:264
    ("same topic, but transferable method + available capability")."""
    prj004 = _find(results, "PRJ-004")
    prj002 = _find(results, "PRJ-002")

    comparison = comparar(prj004, prj002)

    assert comparison.score_delta == pytest.approx(prj004.scored.score - prj002.scored.score)
    feature_names = {f.name for f in comparison.features}
    assert feature_names == {
        "sim_semantica", "sim_lexica", "compat_metodo", "compat_dominio",
        "densidad_evidencia", "soporte_capacidad", "enlace_estructural",
    }
    metodo = next(f for f in comparison.features if f.name == "compat_metodo")
    assert metodo.value_a == pytest.approx(0.90)
    assert metodo.value_b == pytest.approx(0.70)
    assert metodo.favors == "A"


def test_suma_de_deltas_reproduce_exacto_el_delta_de_score(results):
    """El comparador no inventa nada: es aditivo y exacto, igual que
    compute_score. Ningún feature "se pierde" ni se cuenta doble."""
    prj004 = _find(results, "PRJ-004")
    prj002 = _find(results, "PRJ-002")
    comparison = comparar(prj004, prj002)
    assert sum(f.delta for f in comparison.features) == pytest.approx(comparison.score_delta)


def test_dominant_feature_es_la_de_mayor_delta_absoluto(results):
    prj004 = _find(results, "PRJ-004")
    prj002 = _find(results, "PRJ-002")
    comparison = comparar(prj004, prj002)
    max_delta = max(abs(f.delta) for f in comparison.features)
    dominant = next(f for f in comparison.features if f.name == comparison.dominant_feature)
    assert abs(dominant.delta) == pytest.approx(max_delta)


def test_features_ordenadas_por_delta_absoluto_descendente(results):
    prj004 = _find(results, "PRJ-004")
    prj002 = _find(results, "PRJ-002")
    comparison = comparar(prj004, prj002)
    deltas = [abs(f.delta) for f in comparison.features]
    assert deltas == sorted(deltas, reverse=True)


def test_comparar_invertido_invierte_favors_y_signo(results):
    """comparar(A, B) y comparar(B, A) deben ser espejo exacto."""
    prj004 = _find(results, "PRJ-004")
    prj002 = _find(results, "PRJ-002")
    ab = comparar(prj004, prj002)
    ba = comparar(prj002, prj004)
    assert ba.score_delta == pytest.approx(-ab.score_delta)
    by_name_ab = {f.name: f for f in ab.features}
    by_name_ba = {f.name: f for f in ba.features}
    for name in by_name_ab:
        assert by_name_ba[name].delta == pytest.approx(-by_name_ab[name].delta)
