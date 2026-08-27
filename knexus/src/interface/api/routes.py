"""Rutas JSON (`/api/*`) — capa `interface/` de ARCHITECTURE.md F7.

Reciben el `QueryService` ya construido por `Depends` (Regla A2: la ruta NO
arma el pipeline). Mismos DTO de presentación que las plantillas Jinja
(`interface/presenters.py`) — una sola fuente de verdad para "qué se muestra".
"""
from fastapi import APIRouter, Depends, HTTPException, Request

from src.application.auditar_resultado import comparar
from src.interface import metrics_report, presenters
from src.interface.composition import QueryService

router = APIRouter(prefix="/api")


def get_query_service(request: Request) -> QueryService:
    service = getattr(request.app.state, "query_service", None)
    if service is None:
        raise RuntimeError("QueryService no inicializado — ver interface/app.py")
    return service


def _connection_or_404(service: QueryService, query: str, entity_id: str):
    results = service.discover(query)
    for connection in results:
        if connection.entity.entity_id == entity_id:
            return connection, results
    raise HTTPException(status_code=404, detail=f"'{entity_id}' no está en los resultados de '{query}'")


@router.get("/stats")
def stats(service: QueryService = Depends(get_query_service)) -> dict:
    entities = service.repo.all()
    return {
        "entities": len(entities),
        "sources": len(set(e.entity_type for e in entities)),
    }


@router.get("/discover")
def discover(q: str, service: QueryService = Depends(get_query_service)) -> dict:
    if not q or not q.strip():
        return {"query": q, "results": []}
    results = service.discover(q)
    return {"query": q, "results": [presenters.serialize_connection(c, explainer=service.explainer) for c in results]}


@router.get("/connection/{entity_id}")
def connection_detail(entity_id: str, q: str, service: QueryService = Depends(get_query_service)) -> dict:
    connection, _results = _connection_or_404(service, q, entity_id)
    return {"query": q, "connection": presenters.serialize_connection(connection, explainer=service.explainer)}


@router.get("/opportunity")
def opportunity(q: str, service: QueryService = Depends(get_query_service)) -> dict:
    if not q or not q.strip():
        return {"query": q, "opportunities": []}
    opportunities = service.opportunities(q)
    return {
        "query": q,
        "opportunities": [presenters.serialize_opportunity(o, repo=service.repo, explainer=service.explainer) for o in opportunities],
    }


@router.get("/metrics")
def metrics() -> dict:
    """Sprint-07 (M8): lee `evaluation/results.json`, no lo calcula en vivo
    (20 NEEDs con el modelo real toma minutos, incompatible con un request).
    Sin archivo -> 200 con `available: false` (estado válido, no un error)."""
    return presenters.serialize_metrics(metrics_report.load_report())


@router.get("/audit")
def audit(q: str, a: str, b: str, service: QueryService = Depends(get_query_service)) -> dict:
    connection_a, results = _connection_or_404(service, q, a)
    connection_b = next((c for c in results if c.entity.entity_id == b), None)
    if connection_b is None:
        raise HTTPException(status_code=404, detail=f"'{b}' no está en los resultados de '{q}'")
    comparison = comparar(connection_a, connection_b)
    return {
        "query": q,
        "a": presenters.serialize_connection(connection_a, explainer=service.explainer),
        "b": presenters.serialize_connection(connection_b, explainer=service.explainer),
        "comparison": presenters.serialize_comparison(comparison),
    }
