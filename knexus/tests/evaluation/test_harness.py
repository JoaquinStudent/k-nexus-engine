"""Test estructural de `evaluation/harness.py` — pipeline rápido
(HashingProvider, sin red) para verificar el SHAPE de `run_all()` con los 3
brazos del ablation. Los NÚMEROS no significan nada con HashingProvider (no
hay similitud semántica real) — eso lo cubre `test_harness_slow.py` con el
modelo real."""
import pytest

from evaluation import harness, qrels
from src.adapters.embeddings.hashing_provider import HashingProvider
from src.adapters.graph.networkx_store import NetworkXGraphStore
from src.adapters.repository.dataset_repository import DatasetEntityRepository
from src.adapters.retrieval.bm25_index import BM25Index
from src.adapters.retrieval.corpus import build_corpus
from src.adapters.retrieval.dense_index import DenseIndex


@pytest.fixture(scope="module")
def pipeline():
    repo = DatasetEntityRepository()
    refs, texts = build_corpus(repo)
    dense = DenseIndex(HashingProvider(dim=256))
    dense.build(refs, texts, use_cache=False)
    lexical = BM25Index()
    lexical.build(refs, texts)
    graph = NetworkXGraphStore(repo)
    return {"repo": repo, "dense_index": dense, "lexical_index": lexical, "graph": graph}


def test_run_all_produce_el_shape_esperado(pipeline):
    results = harness.run_all(**pipeline)
    assert results["needs_evaluated"] == len(qrels.needs_covered())
    for label in ("cluster", "strict"):
        for arm in harness.ARMS:
            block = results["precision_recall"][label][arm]
            assert set(block) == {"p5", "p10", "r10", "r30", "mrr"}
    for arm in harness.ARMS:
        block = results["construct_validity"][arm]
        assert set(block) == {"trap_rate", "capability_rate", "method_rate", "actionable_rate", "unscored_rate"}
    assert len(results["per_need"]) == results["needs_evaluated"]
    assert results["avg_latency_ms"] >= 0
    assert results["avg_dense_latency_ms"] >= 0


def test_run_all_revienta_si_qrels_no_valida(pipeline):
    bad_rows = (qrels.QrelRow(need_id="NEED-001", context="esto no existe en ningun lado", note="typo"),)
    with pytest.raises(ValueError):
        harness.run_all(rows=bad_rows, **pipeline)


def test_recall_ceiling_nunca_supera_uno(pipeline):
    results = harness.run_all(**pipeline)
    for label in ("cluster", "strict"):
        assert 0.0 <= results["recall_ceilings"][label]["r10_ceiling"] <= 1.0
        assert 0.0 <= results["recall_ceilings"][label]["r30_ceiling"] <= 1.0


def test_dense_ranked_esta_ordenado_por_coseno_descendente(pipeline):
    """El brazo `dense` no pasa por RRF ni por reranking -- su orden debe
    coincidir exactamente con el score de similitud agregado por entidad."""
    run = harness.run_need("NEED-001", **pipeline)
    from src.adapters.retrieval.fusion import aggregate_by_entity
    from src.application.query_builder import build_query

    query = build_query("NEED-001", pipeline["repo"])
    hits = pipeline["dense_index"].search(query.text, k=harness.DENSE_RETRIEVAL_K)
    hits = tuple(h for h in hits if h[0].entity_id != "NEED-001")
    aggregated = aggregate_by_entity(hits)
    scores = [aggregated[entity_id][1] for entity_id in run.dense_ranked]
    assert scores == sorted(scores, reverse=True)


def test_construct_validity_full_y_cosine_nunca_reportan_unscored(pipeline):
    """`full`/`cosine` comparten pool por construcción -- toda posición del
    top-k viene de `full_connections`, nunca queda sin puntuar."""
    results = harness.run_all(**pipeline)
    assert results["construct_validity"]["full"]["unscored_rate"] == 0.0
    assert results["construct_validity"]["cosine"]["unscored_rate"] == 0.0


def test_construct_validity_dense_unscored_rate_en_rango(pipeline):
    results = harness.run_all(**pipeline)
    assert 0.0 <= results["construct_validity"]["dense"]["unscored_rate"] <= 1.0
