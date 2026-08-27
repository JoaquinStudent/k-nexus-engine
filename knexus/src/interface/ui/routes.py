"""Rutas HTML (M1-M5, M7, M9 de DESIGN.md) — capa `interface/` de
ARCHITECTURE.md F7. Consumen los MISMOS DTO de presentación que `/api/*`
(`interface/presenters.py`) — una sola forma de "qué se muestra", dos formatos
de salida."""
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.application.auditar_resultado import comparar
from src.interface import presenters
from src.interface.api.routes import get_query_service
from src.interface.composition import QueryService
from src.ports.entity_repository import StoredEntity

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter()

# IDs de ejemplo para los quick-picks de M1 (DESIGN.md §5, M1) — se resuelven
# contra el repositorio real; uno que no exista simplemente no aparece.
QUICK_PICK_IDS = ("NEED-001", "NEED-005", "NEED-009")


def _quick_picks(repo) -> tuple:
    picks = []
    for entity_id in QUICK_PICK_IDS:
        try:
            picks.append({"id": entity_id, "title": presenters.title_of(repo.get(entity_id))})
        except KeyError:
            continue
    return tuple(picks)


def _base_context(request: Request, service: QueryService, *, active: str) -> dict:
    return {
        "request": request,
        "active": active,
        "explainer_degraded": service.explainer_degraded,
    }


def _query_entity_or_placeholder(service: QueryService, query: str):
    """El mismo patrón que `generar_oportunidad.py` para texto libre: si la
    query no es una entidad del dataset, se usa el propio texto como sujeto."""
    try:
        return service.repo.get(query.strip())
    except KeyError:
        return StoredEntity(entity_id=query, entity_type="QUERY")


@router.get("/", response_class=HTMLResponse)
def query_page(request: Request, service: QueryService = Depends(get_query_service)):
    context = _base_context(request, service, active="discover")
    context.update({
        "entity_count": len(service.repo.all()),
        "quick_picks": _quick_picks(service.repo),
    })
    return templates.TemplateResponse(request, "query.html", context)


@router.get("/results", response_class=HTMLResponse)
def results_page(request: Request, q: str = "", service: QueryService = Depends(get_query_service)):
    q = q.strip()
    if not q:
        return query_page(request, service)
    results = service.discover(q)
    context = _base_context(request, service, active="results")
    context.update({
        "query": q,
        "connections": [presenters.serialize_connection(c) for c in results],
    })
    return templates.TemplateResponse(request, "results.html", context)


@router.get("/connection/{entity_id}", response_class=HTMLResponse)
def connection_page(entity_id: str, request: Request, q: str, service: QueryService = Depends(get_query_service)):
    results = service.discover(q.strip())
    connection = next((c for c in results if c.entity.entity_id == entity_id), None)
    context = _base_context(request, service, active="results")
    if connection is None:
        context.update({
            "query": q, "connections": [presenters.serialize_connection(c) for c in results],
            "not_found_id": entity_id,
        })
        return templates.TemplateResponse(request, "results.html", context, status_code=404)

    query_entity = _query_entity_or_placeholder(service, q)
    context.update({
        "query": q,
        "connection": presenters.serialize_connection(connection, explainer=service.explainer),
        "graph_svg": presenters.subgraph_svg(
            connection.entity, query_entity, results, graph=service.graph, repo=service.repo,
        ),
    })
    return templates.TemplateResponse(request, "connection.html", context)


@router.get("/opportunity", response_class=HTMLResponse)
def opportunity_page(request: Request, q: str = "", service: QueryService = Depends(get_query_service)):
    q = q.strip()
    context = _base_context(request, service, active="opportunity")
    if not q:
        context.update({"query": q, "opportunities": ()})
        return templates.TemplateResponse(request, "opportunity.html", context)
    opportunities = service.opportunities(q)
    context.update({
        "query": q,
        "opportunities": [
            presenters.serialize_opportunity(o, repo=service.repo, explainer=service.explainer)
            for o in opportunities
        ],
    })
    return templates.TemplateResponse(request, "opportunity.html", context)


@router.get("/audit", response_class=HTMLResponse)
def audit_page(
    request: Request, q: str = "", a: str = "", b: str = "",
    service: QueryService = Depends(get_query_service),
):
    q = q.strip()
    context = _base_context(request, service, active="audit")
    results = service.discover(q) if q else ()
    context.update({
        "query": q, "a": a, "b": b,
        "connections": [presenters.serialize_connection(c) for c in results],
    })

    connection_a = next((c for c in results if c.entity.entity_id == a), None) if a else None
    connection_b = next((c for c in results if c.entity.entity_id == b), None) if b else None
    if connection_a is not None and connection_b is not None:
        comparison = comparar(connection_a, connection_b)
        context.update({
            "connection_a": presenters.serialize_connection(connection_a),
            "connection_b": presenters.serialize_connection(connection_b),
            "comparison": presenters.serialize_comparison(comparison),
        })
    return templates.TemplateResponse(request, "audit.html", context)
