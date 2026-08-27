"""Tests de `/api/*` con `TestClient` + `app.dependency_overrides` — las rutas
piden el pipeline por `Depends(get_query_service)`, así que el test inyecta un
`QueryService` mínimo (HashingProvider, sin red) y NUNCA se ejecuta el
`lifespan` real de `app.py` (que cargaría el modelo real). Mismo patrón de
fixture que `tests/application/test_descubrir_conexiones.py`.
"""
import pytest
from fastapi.testclient import TestClient

from src.adapters.embeddings.hashing_provider import HashingProvider
from src.adapters.graph.networkx_store import NetworkXGraphStore
from src.adapters.repository.dataset_repository import DatasetEntityRepository
from src.adapters.retrieval.bm25_index import BM25Index
from src.adapters.retrieval.corpus import build_corpus
from src.adapters.retrieval.dense_index import DenseIndex
from src.interface.api.routes import get_query_service
from src.interface.app import app
from src.interface.composition import QueryService


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
    # Deliberadamente SIN `with TestClient(app) as client:` — eso dispararía
    # el `lifespan` real de `app.py` (build_pipeline con el modelo real).
    # Sin `with`, el lifespan no corre y el override de dependencia basta:
    # la ruta nunca llega a tocar `request.app.state.query_service`.
    app.dependency_overrides[get_query_service] = lambda: service
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()


def test_discover_devuelve_json_rankeado(client):
    resp = client.get("/api/discover", params={"q": "NEED-001"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["query"] == "NEED-001"
    assert body["results"]
    ranks = [r["rank"] for r in body["results"]]
    assert ranks == sorted(ranks)
    first = body["results"][0]
    assert set(first) >= {"entity_id", "title", "score", "relevance_band", "breakdown", "evidence"}
    assert len(first["breakdown"]) == 7


def test_discover_query_vacia_es_estado_valido_no_error(client):
    """M9 — la query vacía es un estado válido (M1 "empty"), no un error."""
    resp = client.get("/api/discover", params={"q": ""})
    assert resp.status_code == 200
    assert resp.json()["results"] == []


def test_connection_404_si_no_esta_en_los_resultados(client):
    resp = client.get("/api/connection/NO-EXISTE-999", params={"q": "NEED-001"})
    assert resp.status_code == 404


def test_connection_detail_trae_breakdown_y_evidencia(client):
    top = client.get("/api/discover", params={"q": "NEED-001"}).json()["results"][0]
    resp = client.get(f"/api/connection/{top['entity_id']}", params={"q": "NEED-001"})
    assert resp.status_code == 200
    connection = resp.json()["connection"]
    assert connection["entity_id"] == top["entity_id"]
    assert connection["evidence"]["source_file"]
    assert connection["evidence"]["field_name"]


def test_opportunity_puede_venir_vacia_sin_reventar(client):
    resp = client.get("/api/opportunity", params={"q": "texto que no ancla ninguna oportunidad real xyz"})
    assert resp.status_code == 200
    assert isinstance(resp.json()["opportunities"], list)


def test_audit_reproduce_delta_exacto(client):
    results = client.get("/api/discover", params={"q": "NEED-001"}).json()["results"]
    a, b = results[0]["entity_id"], results[1]["entity_id"]
    resp = client.get("/api/audit", params={"q": "NEED-001", "a": a, "b": b})
    assert resp.status_code == 200
    body = resp.json()
    expected_delta = body["a"]["score"] - body["b"]["score"]
    assert body["comparison"]["score_delta"] == pytest.approx(expected_delta, abs=1e-9)


def test_audit_404_si_b_no_esta_en_resultados(client):
    results = client.get("/api/discover", params={"q": "NEED-001"}).json()["results"]
    a = results[0]["entity_id"]
    resp = client.get("/api/audit", params={"q": "NEED-001", "a": a, "b": "NO-EXISTE-999"})
    assert resp.status_code == 404


def test_stats_reporta_entidades_cargadas(client):
    resp = client.get("/api/stats")
    assert resp.status_code == 200
    assert resp.json()["entities"] > 0
