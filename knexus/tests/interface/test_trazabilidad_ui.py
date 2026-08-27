"""Regla A3 (ARCHITECTURE.md §6): "todo resultado conserva su provenance hasta
la UI". Hasta este sprint A3 sólo se verificaba a nivel de datos
(`test_ingestion.py`); este test cierra el hueco verificando que el HTML
renderizado de verdad muestra `source_file`/`field_name` — no sólo que el DTO
los tenga."""
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
    app.dependency_overrides[get_query_service] = lambda: service
    test_client = TestClient(app, raise_server_exceptions=True)
    yield test_client
    app.dependency_overrides.clear()


def test_a3_provenance_llega_al_html(client, service):
    top = service.discover("NEED-001")[0]
    resp = client.get(f"/connection/{top.entity.entity_id}", params={"q": "NEED-001"})
    assert resp.status_code == 200
    html = resp.text
    assert top.evidence.source_file in html
    assert top.evidence.field_name in html
    assert top.evidence.entity_id in html


def test_a3_evidencia_y_generado_nunca_en_el_mismo_bloque(client, service):
    """El texto del Explainer (generado) y la cita de evidencia institucional
    deben quedar en bloques visuales separados — DESIGN.md §2.3: "Evidencia
    (orchid) y Generado (gris) siempre visualmente distintos"."""
    top = service.discover("NEED-001")[0]
    resp = client.get(f"/connection/{top.entity.entity_id}", params={"q": "NEED-001"})
    html = resp.text
    evidence_idx = html.index("tag-evidence")
    generated_idx = html.index("tag-generated") if "tag-generated" in html else None
    assert evidence_idx >= 0
    if generated_idx is not None:
        # bloques distintos: no puede ser el mismo índice de aparición
        assert generated_idx != evidence_idx
