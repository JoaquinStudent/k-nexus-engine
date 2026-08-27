"""Tests de `/api/metrics` (Sprint-07, M8) -- lee `evaluation/results.json` vía
`interface/metrics_report.py`. Se monkeypatchea `RESULTS_PATH` con un archivo
de fixture en vez de depender del artefacto real commiteado (que puede no
existir en este checkout, o cambiar de número entre corridas).
"""
import json

import pytest
from fastapi.testclient import TestClient

from src.interface import metrics_report
from src.interface.app import app

_SAMPLE = {
    "needs_evaluated": 1,
    "avg_latency_ms": 200.0,
    "avg_dense_latency_ms": 1.5,
    "evidence_coverage": 1.0,
    "precision_recall": {
        "cluster": {
            "full": {"p5": 0.6, "p10": 0.5, "r10": 0.2, "r30": 0.4, "mrr": 0.7},
            "cosine": {"p5": 0.3, "p10": 0.25, "r10": 0.1, "r30": 0.2, "mrr": 0.4},
            "dense": {"p5": 0.2, "p10": 0.15, "r10": 0.05, "r30": 0.15, "mrr": 0.3},
        },
        "strict": {
            "full": {"p5": 0.5, "p10": 0.4, "r10": 0.15, "r30": 0.3, "mrr": 0.6},
            "cosine": {"p5": 0.2, "p10": 0.2, "r10": 0.08, "r30": 0.18, "mrr": 0.3},
            "dense": {"p5": 0.1, "p10": 0.1, "r10": 0.04, "r30": 0.1, "mrr": 0.2},
        },
    },
    "recall_ceilings": {
        "cluster": {"r10_ceiling": 0.36, "r30_ceiling": 0.97},
        "strict": {"r10_ceiling": 0.30, "r30_ceiling": 0.90},
    },
    "construct_validity": {
        "full": {"trap_rate": 0.18, "capability_rate": 0.43, "method_rate": 0.44, "actionable_rate": 0.63, "unscored_rate": 0.0},
        "cosine": {"trap_rate": 0.5, "capability_rate": 0.1, "method_rate": 0.1, "actionable_rate": 0.2, "unscored_rate": 0.0},
        "dense": {"trap_rate": 0.6, "capability_rate": 0.05, "method_rate": 0.05, "actionable_rate": 0.1, "unscored_rate": 0.3},
    },
    "per_need": [
        {"need_id": "NEED-001", "relevant_cluster": 6, "relevant_strict": 1,
         "p5_full": 0.6, "p5_cosine": 0.3, "p5_dense": 0.2, "latency_ms": 200.0},
    ],
    "meta": {
        "generated_at": "2026-08-27T00:00:00+00:00",
        "provider": "paraphrase-multilingual-MiniLM-L12-v2",
        "fast": False,
        "entities_indexed": 2512,
        "qrels_rows": 97,
        "needs_evaluated": 1,
        "top_k_primary": 5, "top_k_secondary": 10, "top_k_recall_wide": 30,
        "elapsed_s": 60.0,
    },
}


@pytest.fixture()
def client():
    # Sin `with TestClient(app):` -- evita el lifespan real (build_pipeline
    # con el modelo real), mismo patrón que tests/interface/test_api.py.
    return TestClient(app, raise_server_exceptions=True)


def test_metrics_sin_archivo_es_200_con_available_false(client, tmp_path, monkeypatch):
    monkeypatch.setattr(metrics_report, "RESULTS_PATH", tmp_path / "no-existe.json")
    resp = client.get("/api/metrics")
    assert resp.status_code == 200
    assert resp.json() == {"available": False}


def test_metrics_con_archivo_devuelve_shape_completo(client, tmp_path, monkeypatch):
    results_path = tmp_path / "results.json"
    results_path.write_text(json.dumps(_SAMPLE), encoding="utf-8")
    monkeypatch.setattr(metrics_report, "RESULTS_PATH", results_path)

    resp = client.get("/api/metrics")
    assert resp.status_code == 200
    body = resp.json()
    assert body["available"] is True
    assert len(body["stat_tiles"]) == 3
    assert [row["arm"] for row in body["ablation"]] == ["full", "cosine", "dense"]
    assert body["meta"]["provider"] == "paraphrase-multilingual-MiniLM-L12-v2"
