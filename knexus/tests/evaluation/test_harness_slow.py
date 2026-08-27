"""Verificación de `evaluation/harness.py` con el MODELO REAL de embeddings
(marcado `@slow`, mismo patrón que `tests/application/test_generar_oportunidad_slow.py`).
`test_harness.py` sólo prueba el SHAPE con HashingProvider -- aquí se prueba
que los 3 brazos producen resultados que tienen sentido con similitud
semántica real, no sólo que no revientan.

Deliberadamente NO se asertar "full > cosine" en ningún número -- eso fijaría
un resultado que los DATOS deben decidir (lección de honestidad, MEMORY.md
L6). Lo que sí se verifica es que el sistema corre end-to-end y que los 3
brazos son medibles y (normalmente) producen órdenes distintos.
"""
import pytest

from evaluation import harness, qrels
from src.adapters.embeddings.sentence_transformer_provider import SentenceTransformerProvider
from src.adapters.graph.networkx_store import NetworkXGraphStore
from src.adapters.repository.dataset_repository import DatasetEntityRepository
from src.adapters.retrieval.bm25_index import BM25Index
from src.adapters.retrieval.corpus import build_corpus
from src.adapters.retrieval.dense_index import DenseIndex

# Subconjunto -- correr los 20 NEEDs con el modelo real es el trabajo de
# `scripts/evaluate.py` (varios minutos); este test sólo verifica que el
# arnés funciona correctamente con similitud semántica real.
SAMPLE_NEED_IDS = ("NEED-001", "NEED-005", "NEED-009")


@pytest.fixture(scope="module")
def pipeline():
    repo = DatasetEntityRepository()
    refs, texts = build_corpus(repo)
    dense = DenseIndex(SentenceTransformerProvider())
    dense.build(refs, texts, use_cache=True)
    lexical = BM25Index()
    lexical.build(refs, texts)
    graph = NetworkXGraphStore(repo)
    return {"repo": repo, "dense_index": dense, "lexical_index": lexical, "graph": graph}


@pytest.mark.slow
def test_run_need_corre_end_to_end_con_modelo_real(pipeline):
    run = harness.run_need("NEED-001", **pipeline)
    assert run.full_ranked
    assert run.cosine_ranked
    assert run.dense_ranked
    assert set(run.full_ranked) == set(run.cosine_ranked)  # mismo pool, distinto orden


@pytest.mark.slow
def test_full_ranked_no_es_identico_a_dense_ranked_con_modelo_real(pipeline):
    """El brazo `full` (RRF + grafo + reranking) y el brazo `dense` (coseno
    puro) parten de mecanismos de recuperación distintos -- con el modelo
    real, casi nunca coinciden posición por posición."""
    run = harness.run_need("NEED-001", **pipeline)
    assert run.full_ranked[:10] != run.dense_ranked[:10]


@pytest.mark.slow
def test_run_all_sobre_muestra_produce_p5_positivo(pipeline):
    rows = tuple(row for row in qrels.load_rows() if row.need_id in SAMPLE_NEED_IDS)
    results = harness.run_all(rows=rows, **pipeline)
    assert results["needs_evaluated"] == len(SAMPLE_NEED_IDS)
    assert results["precision_recall"]["cluster"]["full"]["p5"] > 0.0
