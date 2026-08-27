"""Test estructural de `evaluation/harness.py` — pipeline rápido
(HashingProvider, sin red) para verificar el SHAPE de `run_all()`. Los
NÚMEROS no significan nada con HashingProvider (no hay similitud semántica
real) — eso lo cubre `test_harness_slow.py` con el modelo real."""
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
        for arm in ("full", "cosine"):
            block = results["precision_recall"][label][arm]
            assert set(block) == {"p5", "p10", "r10", "r30", "mrr"}
    for arm in ("full", "cosine"):
        block = results["construct_validity"][arm]
        assert set(block) == {"trap_rate", "capability_rate", "method_rate", "actionable_rate"}
    assert len(results["per_need"]) == results["needs_evaluated"]
    assert results["avg_latency_ms"] >= 0


def test_run_all_revienta_si_qrels_no_valida(pipeline):
    bad_rows = (qrels.QrelRow(need_id="NEED-001", context="esto no existe en ningun lado", note="typo"),)
    with pytest.raises(ValueError):
        harness.run_all(rows=bad_rows, **pipeline)


def test_recall_ceiling_nunca_supera_uno(pipeline):
    results = harness.run_all(**pipeline)
    for label in ("cluster", "strict"):
        assert 0.0 <= results["recall_ceilings"][label]["r10_ceiling"] <= 1.0
        assert 0.0 <= results["recall_ceilings"][label]["r30_ceiling"] <= 1.0
