"""Sprint-03: representación (denso + léxico + grafo) y cierre del 25% inerte
(ADR-008). Los tests marcados `slow` usan el modelo real (descarga/red la
primera vez); `pytest -m "not slow"` corre todo lo demás offline."""
import numpy as np
import pytest

from src.adapters.embeddings.hashing_provider import HashingProvider
from src.adapters.graph.networkx_store import NetworkXGraphStore
from src.adapters.repository.dataset_repository import DatasetEntityRepository
from src.adapters.repository.projection import to_candidate_entity, to_query_entity
from src.adapters.retrieval.bm25_index import BM25Index
from src.adapters.retrieval.corpus import build_corpus
from src.adapters.retrieval.dense_index import DenseIndex
from src.domain.features import compute_features
from src.domain.models import CandidatePair
from src.domain.relation_type import classify_relation
from src.domain.scoring import WEIGHTS, compute_score


@pytest.fixture(scope="module")
def repo():
    return DatasetEntityRepository()


@pytest.fixture(scope="module")
def corpus(repo):
    return build_corpus(repo)


@pytest.fixture(scope="module")
def graph(repo):
    return NetworkXGraphStore(repo)


# ---------------------------------------------------------------------------
# Índice denso (con HashingProvider — sin red, Regla A4)
# ---------------------------------------------------------------------------

def test_dense_index_dimensiones_y_normalizacion(corpus):
    refs, texts = corpus
    provider = HashingProvider(dim=64)
    vectors = provider.encode(texts[:20])
    assert vectors.shape == (20, 64)
    norms = np.linalg.norm(vectors, axis=1)
    assert np.allclose(norms[norms > 0], 1.0)


def test_dense_index_search_ordenado_y_determinista(corpus):
    refs, texts = corpus
    provider = HashingProvider(dim=64)
    index = DenseIndex(provider)
    index.build(refs[:200], texts[:200])

    results_a = index.search("deserción estudiantil", k=5)
    results_b = index.search("deserción estudiantil", k=5)
    assert results_a == results_b  # determinismo

    scores = [score for _, score in results_a]
    assert scores == sorted(scores, reverse=True)
    assert all(-1.0 <= s <= 1.0 for s in scores)
    assert len(results_a) <= 5


def test_degradacion_offline_sin_red(corpus):
    # Regla A4: la suite entera puede correr sin el modelo real.
    refs, texts = corpus
    provider = HashingProvider()
    index = DenseIndex(provider)
    index.build(refs[:500], texts[:500])
    results = index.search("clasificación supervisada", k=3)
    assert results


# ---------------------------------------------------------------------------
# Índice léxico (BM25)
# ---------------------------------------------------------------------------

def test_bm25_recupera_termino_exacto(corpus):
    refs, texts = corpus
    index = BM25Index()
    index.build(refs, texts)
    # k=30, no 10: a nivel de campo, un `researcher.methodological_expertise`
    # corto que dice literalmente "clasificación supervisada" puntúa más alto
    # en BM25 que la oración larga de `project.methodology` — comportamiento
    # correcto de BM25 (favorece campos cortos y densos en el término), no bug.
    results = index.search("clasificación supervisada", k=30)
    assert results
    hit_entities = {ref.entity_id for ref, _ in results}
    assert "PRJ-004" in hit_entities
    assert any(ref.entity_type == "RESEARCHER" for ref, _ in results)


def test_bm25_folding_analitica_sin_acento_equivale_a_analitica_con_acento(corpus):
    refs, texts = corpus
    index = BM25Index()
    index.build(refs, texts)
    con_acento = index.search("analítica educativa", k=10)
    sin_acento = index.search("analitica educativa", k=10)
    assert {r.entity_id for r, _ in con_acento} == {r.entity_id for r, _ in sin_acento}


def test_provenance_sobrevive_la_recuperacion(corpus):
    refs, texts = corpus
    index = BM25Index()
    index.build(refs, texts)
    results = index.search("clasificación supervisada", k=5)
    for ref, _ in results:
        assert ref.entity_id
        assert ref.field_name
        assert ref.source_file


# ---------------------------------------------------------------------------
# Grafo (NetworkX sobre las 7 relaciones ya cargadas por Sprint-02)
# ---------------------------------------------------------------------------

def test_grafo_carga_todas_las_aristas_de_las_7_relaciones(repo, graph):
    # Conteos de Sprint-02 (cuadran con los manifests de Data V1.0):
    # researcher_project=746, project_group=320, thesis_advisor=650,
    # publication_researcher=720, publication_project=200,
    # researcher_group=180, researcher_expertise=720 -> total 3536.
    total = sum(len(repo.edges(r)) for r in (
        "researcher_project", "project_group", "thesis_advisor",
        "publication_researcher", "publication_project", "researcher_group",
        "researcher_expertise",
    ))
    assert total == 3536


def test_grafo_neighbors_investigadores_reales_de_prj004(graph):
    neighbors = graph.neighbors("PRJ-004")
    assert "INV-127" in neighbors  # PI real (researcher_project.csv)
    assert "INV-100" in neighbors  # co-investigador real


def test_grafo_linked_to_any_discrimina(graph):
    assert graph.linked_to_any("INV-127", ("PRJ-004",)) is True
    assert graph.linked_to_any("INV-003", ("PRJ-004",)) is False  # sin arista alguna


# ---------------------------------------------------------------------------
# Cierre del 25% inerte (ADR-008): graph_linked + has_capability_support
# ---------------------------------------------------------------------------

def test_cierre_enlace_estructural_investigador_complementario(repo, graph):
    need = to_query_entity(repo.get("NEED-001"))
    researcher = to_candidate_entity(
        repo.get("INV-127"), graph=graph, seed_ids=("PRJ-004",),
    )
    assert researcher.graph_linked is True

    fv = compute_features(CandidatePair(query=need, candidate=researcher, sim_semantic=0.5))
    assert fv.enlace_estructural == 1.0
    assert classify_relation(fv, "researcher") == "investigador_complementario"


def test_sin_contexto_graph_linked_sigue_false_cero_regresion(repo):
    # Sin graph/seed_ids, comportamiento idéntico a Sprint-02 (no regresión).
    researcher = to_candidate_entity(repo.get("INV-127"))
    assert researcher.graph_linked is False


def test_cierre_soporte_capacidad_activacion_capacidad(repo):
    capabilities = repo.by_type("CAPABILITY")
    need = to_query_entity(repo.get("NEED-001"))

    prj004 = to_candidate_entity(repo.get("PRJ-004"), capabilities=capabilities)
    assert prj004.has_capability_support is True

    fv = compute_features(CandidatePair(query=need, candidate=prj004, sim_semantic=0.3))
    assert fv.soporte_capacidad == 1.0


def test_sin_contexto_capability_support_sigue_false_cero_regresion(repo):
    prj004 = to_candidate_entity(repo.get("PRJ-004"))
    assert prj004.has_capability_support is False


def test_soporte_capacidad_deja_de_estar_muerto_en_el_score(repo):
    # Antes de Sprint-03, has_capability_support era False para todo candidato
    # real -> ese 0.15 de peso contribuía 0 siempre. Con contexto, PRJ-004
    # (soporte_capacidad=True) debe puntuar por encima de sí mismo sin contexto.
    capabilities = repo.by_type("CAPABILITY")
    need = to_query_entity(repo.get("NEED-001"))

    prj004_sin_contexto = to_candidate_entity(repo.get("PRJ-004"))
    prj004_con_capacidad = to_candidate_entity(repo.get("PRJ-004"), capabilities=capabilities)

    fv_sin = compute_features(CandidatePair(query=need, candidate=prj004_sin_contexto, sim_semantic=0.88))
    fv_con = compute_features(CandidatePair(query=need, candidate=prj004_con_capacidad, sim_semantic=0.88))

    assert fv_sin.soporte_capacidad == 0.0
    assert fv_con.soporte_capacidad == 1.0
    assert compute_score(fv_con) > compute_score(fv_sin)
    assert compute_score(fv_con) - compute_score(fv_sin) == pytest.approx(WEIGHTS["soporte_capacidad"])


# ---------------------------------------------------------------------------
# Cruce ES <-> EN con el modelo real (DoD del sprint)
# ---------------------------------------------------------------------------

@pytest.mark.slow
def test_cruce_es_en_con_modelo_real(corpus):
    from src.adapters.embeddings.sentence_transformer_provider import SentenceTransformerProvider

    refs, texts = corpus
    provider = SentenceTransformerProvider()
    index = DenseIndex(provider)
    index.build(refs, texts)

    hits_es = index.search("deserción estudiantil", k=15)
    entities_from_es_query = {ref.entity_id for ref, _ in hits_es}
    assert "PRJ-004" in entities_from_es_query or "NEED-001" in entities_from_es_query

    hits_en = index.search("student attrition", k=15)
    entities_from_en_query = {ref.entity_id for ref, _ in hits_en}
    assert "PRJ-004" in entities_from_en_query or "PRJ-007" in entities_from_en_query

    # el cruce real: la consulta en un idioma recupera texto escrito en el otro
    assert entities_from_es_query & entities_from_en_query
