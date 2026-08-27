"""E2E con dataset + modelo REALES (marcado `@slow`, se excluye con
-m "not slow"). Verifica L4/R7: el sistema responde a consultas NUEVAS en
vivo, no sólo a las precargadas en desarrollo — usando el pipeline completo
(`interface/composition.py`) tal como lo arranca `app.py`."""
import pytest
from fastapi.testclient import TestClient

from src.interface.api.routes import get_query_service
from src.interface.app import app
from src.interface.composition import QueryService

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def service():
    return QueryService.build(fast=False)


@pytest.fixture()
def client(service):
    app.dependency_overrides[get_query_service] = lambda: service
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()


def test_need001_responde_con_modelo_real(client):
    resp = client.get("/results", params={"q": "NEED-001"})
    assert resp.status_code == 200
    assert "PRJ-" in resp.text or "THS-" in resp.text


def test_consulta_en_texto_libre_nunca_vista_responde_en_vivo(client):
    """L4: "el sistema debe responder a consultas nuevas sin precargados"."""
    query = "impacto de la inteligencia artificial en la evaluacion docente universitaria"
    resp = client.get("/api/discover", params={"q": query})
    assert resp.status_code == 200
    body = resp.json()
    assert body["results"], "una consulta nueva en texto libre debe producir resultados reales"
    assert 0.0 <= body["results"][0]["score"] <= 1.0


def test_conexion_detalle_con_modelo_real_trae_grafo_y_evidencia(client, service):
    results = service.discover("NEED-001")
    top = results[0]
    resp = client.get(f"/connection/{top.entity.entity_id}", params={"q": "NEED-001"})
    assert resp.status_code == 200
    assert "<svg" in resp.text
    assert top.evidence.source_file in resp.text
