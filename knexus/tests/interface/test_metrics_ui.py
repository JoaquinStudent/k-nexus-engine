"""Tests de `/metrics` (M8, Sprint-07) HTML -- lección L9 de MEMORY.md: un
test verde en JSON (`test_metrics_api.py`) no prueba que la página se
renderice. Se ejercita el HTML real, tanto con datos como en el estado vacío.
"""
import json

import pytest
from fastapi.testclient import TestClient

from src.adapters.embeddings.hashing_provider import HashingProvider
from src.adapters.graph.networkx_store import NetworkXGraphStore
from src.adapters.repository.dataset_repository import DatasetEntityRepository
from src.adapters.retrieval.bm25_index import BM25Index
from src.adapters.retrieval.corpus import build_corpus
from src.adapters.retrieval.dense_index import DenseIndex
from src.interface import metrics_report
from src.interface.api.routes import get_query_service
from src.interface.app import app
from src.interface.composition import QueryService

from tests.interface.test_metrics_api import _SAMPLE


@pytest.fixture(scope="module")
def service():
    repo = DatasetEntityRepository()
    refs, texts = build_corpus(repo)
    dense = DenseIndex(HashingProvider(dim=256))
    dense.build(refs, texts, use_cache=False)
    lexical = BM25Index()
    lexical.build(refs, texts)
    graph = NetworkXGraphStore(repo)
    return QueryService(repo, dense, lexical, graph)


@pytest.fixture()
def client(service):
    app.dependency_overrides[get_query_service] = lambda: service
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()


def test_metrics_page_sin_archivo_muestra_estado_vacio(client, tmp_path, monkeypatch):
    monkeypatch.setattr(metrics_report, "RESULTS_PATH", tmp_path / "no-existe.json")
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "Aún no hay ninguna medición registrada" in resp.text
    assert "scripts/evaluate.py" in resp.text


def test_metrics_page_con_datos_renderiza_numeros_y_procedencia(client, tmp_path, monkeypatch):
    results_path = tmp_path / "results.json"
    results_path.write_text(json.dumps(_SAMPLE), encoding="utf-8")
    monkeypatch.setattr(metrics_report, "RESULTS_PATH", results_path)

    resp = client.get("/metrics")
    assert resp.status_code == 200
    body = resp.text
    # Los números medidos (no sólo el shape JSON) deben llegar al HTML.
    assert "60%" in body  # P@5 del brazo full, ahora en escala 0-100%
    assert "Similitud no es lo mismo que relevancia" in body  # UX: traducido, mismo hallazgo (SPEC.md §13.3)
    # La línea de procedencia -- sin ella el número no es auditable (MEMORY.md).
    assert "paraphrase-multilingual-MiniLM-L12-v2" in body
    assert "2512" in body
    assert "97" in body


def test_metrics_page_esta_en_el_sidebar_activo(client, tmp_path, monkeypatch):
    monkeypatch.setattr(metrics_report, "RESULTS_PATH", tmp_path / "no-existe.json")
    resp = client.get("/metrics")
    assert 'href="/metrics" class="active"' in resp.text
