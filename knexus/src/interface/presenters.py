"""DTO del backend -> dict de presentación. PURO: sin FastAPI, sin Jinja, sin
pipeline — testeable en aislamiento (`tests/interface/test_presenters.py`).

Reusa el vocabulario ya existente en vez de duplicarlo: las etiquetas ES vienen
de `adapters/explain/template_explainer.py` (la misma redacción que ve el
Explainer), los umbrales de relevancia son los de `domain/opportunity.py`
(una sola vara de medir en todo el sistema), y la contribución por feature
sale de `application/descubrir_conexiones.feature_contributions` — no se
reimplementa la re-normalización de ADR-007/ADR-009 aquí.
"""
from html import escape as _xml_escape

import networkx as nx

from src.adapters.explain.template_explainer import (
    FEATURE_LABELS, LINK_TYPE_LABELS, OPPORTUNITY_TYPE_LABELS, RELATION_LABELS, ROLE_LABELS,
)
from src.adapters.repository.dataset_paths import ENTITY_TABLES
from src.application.descubrir_conexiones import feature_contributions
from src.domain.opportunity import ALTO, MEDIO
from src.domain.scoring import WEIGHTS

TITLE_MAX_WORDS = 12

# entity_type -> columna cruda que mejor sirve de "título" (primera columna
# indexable declarada en ENTITY_TABLES — para NEED/PROJECT/THESIS/... es el
# nombre propio; para COMPETENCY/LEARNING_OUTCOME, que no tienen columna de
# nombre, es su descripción larga y se trunca abajo).
_TITLE_FIELD_BY_TYPE = {
    entity_type: text_cols[0]
    for _relative_path, (entity_type, _id_col, text_cols) in ENTITY_TABLES.items()
}


def title_of(entity) -> str:
    """`entity`: StoredEntity (ports/). Título legible para tarjetas/encabezados."""
    field = _TITLE_FIELD_BY_TYPE.get(entity.entity_type, "")
    text = (entity.raw.get(field, "") if field else "").strip() or entity.entity_id
    words = text.split()
    if len(words) <= TITLE_MAX_WORDS:
        return text
    return " ".join(words[:TITLE_MAX_WORDS]) + "…"


def relevance_band(score: float) -> str:
    """alta/media/baja — mismos umbrales que `relation_type.py`/`opportunity.py`
    (`ALTO=0.6`, `MEDIO=0.4`); nunca un umbral nuevo inventado para la UI."""
    if score >= ALTO:
        return "alta"
    if score >= MEDIO:
        return "media"
    return "baja"


def breakdown_segments(feature_vector) -> tuple:
    """Un dict por cada una de las 7 features de `WEIGHTS`, EN SU ORDEN — la
    Relevance Breakdown Bar (DESIGN.md M3, signature del producto).

    `na=True` para una feature en None (ADR-007/ADR-009): se pinta como "no
    medible", nunca como 0 — confundir N/A con 0 falsearía visualmente el
    mismo error que el dominio ya evita en `compute_score`.

    Invariante (verificado por test): sum(pct)/100 == compute_score(fv) exacto
    — la misma aditividad que `auditar_resultado.comparar`.
    """
    contributions = dict((name, (value, pct)) for name, value, pct in feature_contributions(feature_vector))
    segments = []
    for name in WEIGHTS:
        value = getattr(feature_vector, name)
        if value is None:
            segments.append({
                "name": name, "label": FEATURE_LABELS.get(name, name),
                "value": None, "na": True, "pct": 0.0,
            })
            continue
        _, contribution = contributions[name]
        segments.append({
            "name": name, "label": FEATURE_LABELS.get(name, name),
            # sin redondear: la aditividad exacta (sum(pct)/100 == score) es
            # un invariante de código, no una coincidencia de precisión de
            # display — redondear aquí la rompería. El template redondea al
            # renderizar.
            "value": value, "na": False, "pct": contribution * 100,
        })
    return tuple(segments)


def relation_label(relation_type: str) -> str:
    return RELATION_LABELS.get(relation_type, relation_type)


def role_label(role: str) -> str:
    return ROLE_LABELS.get(role, role)


def link_type_label(link_type: str) -> str:
    return LINK_TYPE_LABELS.get(link_type, link_type)


def opportunity_type_label(opportunity_type: str) -> str:
    return OPPORTUNITY_TYPE_LABELS.get(opportunity_type, opportunity_type)


def serialize_connection(connection, *, explainer=None) -> dict:
    """`connection`: RankedConnection (application/descubrir_conexiones.py).
    Shape compartida por `/api/*` (JSON) y las plantillas Jinja (mismo dict).
    `explainer` es opcional (puerto Explainer) — sin él, `explanation` queda
    vacío en vez de fallar (el resumen de datos estructurados sigue completo)."""
    scored = connection.scored
    return {
        "rank": connection.rank,
        "entity_id": connection.entity.entity_id,
        "entity_type": connection.entity.entity_type,
        "title": title_of(connection.entity),
        "score": scored.score,
        "relevance_band": relevance_band(scored.score),
        "relation_type": scored.relation_type,
        "relation_label": relation_label(scored.relation_type),
        "breakdown": breakdown_segments(scored.feature_vector),
        "evidence": {
            "source_file": connection.evidence.source_file,
            "field_name": connection.evidence.field_name,
            "entity_id": connection.evidence.entity_id,
        },
        "evidence_text": connection.evidence_text,
        "top_features": tuple(
            {"name": name, "label": FEATURE_LABELS.get(name, name), "value": value}
            for name, value, _pct in connection.top_features
        ),
        "explanation": explainer.explain_connection(connection) if explainer is not None else "",
    }


def _title_lookup(entity_id: str, repo) -> str:
    if repo is None:
        return entity_id
    try:
        return title_of(repo.get(entity_id))
    except KeyError:
        return entity_id


def serialize_opportunity(opportunity, *, repo=None, explainer=None) -> dict:
    """`opportunity`: Opportunity (domain/opportunity.py). `repo` es opcional
    (puerto EntityRepository) — sin él, `title` cae al `entity_id`. `explainer`
    es opcional (puerto Explainer) — sin él, `explanation` queda vacío."""
    return {
        "need_id": opportunity.need_id,
        "opportunity_type": opportunity.opportunity_type,
        "opportunity_type_label": opportunity_type_label(opportunity.opportunity_type),
        "priority": opportunity.priority,
        "score": opportunity.score,
        "explanation": explainer.explain_opportunity(opportunity) if explainer is not None else "",
        "links": tuple(
            {
                "role": link.role,
                "role_label": role_label(link.role),
                "entity_id": link.entity_id,
                "title": _title_lookup(link.entity_id, repo),
                "entity_type": link.entity_type,
                "link_type": link.link_type,
                "link_type_label": link_type_label(link.link_type),
                "score": link.score,
                "relation_type": link.relation_type,
                "relation_label": relation_label(link.relation_type) if link.relation_type else "",
                "rationale_features": link.rationale_features,
            }
            for link in opportunity.links
        ),
    }


# --- Mini-grafo (M6, embebido en M3): SVG inline, determinista, sin JS/CDN ---

NODE_COLORS = {
    "NEED": "#251D4B", "PROJECT": "#5B4F9E", "THESIS": "#C3BEEF",
    "RESEARCHER": "#CADFFD", "CAPABILITY": "#2FADB0",
    "SUBJECT": "#CCA9E8", "COMPETENCY": "#CCA9E8",
}
DEFAULT_NODE_COLOR = "#8A86A6"
EDGE_EXPLICIT = "#3D3A57"
EDGE_INFERRED = "#C3BEEF"
SUBGRAPH_MAX_NODES = 15  # tope de DESIGN.md M6: "no un hairball"


def _entity_type_of(entity_id: str, connections, repo=None) -> str:
    for connection in connections:
        if connection.entity.entity_id == entity_id:
            return connection.entity.entity_type
    if repo is not None:
        try:
            return repo.get(entity_id).entity_type
        except KeyError:
            return ""
    return ""


def subgraph_svg(viewed_entity, query_entity, connections, *, graph, repo=None, width: int = 640, height: int = 420) -> str:
    """`viewed_entity`: StoredEntity de la conexión EN VISTA (M3) — el centro
    del grafo. `query_entity`: StoredEntity/placeholder de la consulta (puede
    coincidir con `viewed_entity` si se está viendo la propia query). `graph`:
    GraphStore (puerto). `connections`/`repo` sólo se usan para resolver el
    tipo de cada nodo (color) — no cambian qué nodos se incluyen.

    Nodos: `viewed_entity` + sus vecinos REALES del grafo (hasta el tope) +
    `query_entity` si es distinto. Dos tipos de arista, mismo principio que
    `link_type` en `domain/opportunity.py` — lo recuperado y lo verificado no
    se dibujan igual: sólida oscura = arista REAL (tabla de relación) de
    `viewed_entity`; punteada lavanda = cómo se LLEGÓ a `viewed_entity` desde
    la consulta (reranking, no una arista)."""
    node_ids = [viewed_entity.entity_id]
    has_distinct_query_node = query_entity.entity_id != viewed_entity.entity_id
    if has_distinct_query_node:
        node_ids.append(query_entity.entity_id)
    for neighbor_id in graph.neighbors(viewed_entity.entity_id):
        if len(node_ids) >= SUBGRAPH_MAX_NODES:
            break
        if neighbor_id not in node_ids:
            node_ids.append(neighbor_id)
    node_set = set(node_ids)

    g = nx.Graph()
    g.add_nodes_from(node_ids)

    discovered_edges = set()
    if has_distinct_query_node:
        edge = frozenset((viewed_entity.entity_id, query_entity.entity_id))
        discovered_edges.add(edge)
        g.add_edge(*edge)

    explicit_edges = set()
    for entity_id in node_ids:
        for neighbor in graph.neighbors(entity_id):
            if neighbor in node_set and neighbor != entity_id:
                edge = frozenset((entity_id, neighbor))
                if edge not in discovered_edges:
                    explicit_edges.add(edge)
                    g.add_edge(entity_id, neighbor)

    if len(node_ids) == 1:
        x, y = width / 2, height / 2
        color = NODE_COLORS.get(viewed_entity.entity_type, DEFAULT_NODE_COLOR)
        return (
            f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
            f'role="img" aria-label="Mini-grafo de conexiones">'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10" fill="{color}" stroke="#FFFFFF" stroke-width="1.5"/>'
            f'<text x="{x:.1f}" y="{y + 24:.1f}" text-anchor="middle" font-size="10" '
            f'font-family="Montserrat, sans-serif" fill="#3D3A57">{_xml_escape(viewed_entity.entity_id)}</text></svg>'
        )

    pos = nx.spring_layout(g, seed=42, k=0.9)
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    pad = 40

    def scale(point):
        x, y = point
        sx = pad + (x - min_x) / (max_x - min_x or 1) * (width - 2 * pad)
        sy = pad + (y - min_y) / (max_y - min_y or 1) * (height - 2 * pad)
        return sx, sy

    coords = {node: scale(point) for node, point in pos.items()}

    parts = []
    for edge in explicit_edges:
        a, b = tuple(edge)
        (x1, y1), (x2, y2) = coords[a], coords[b]
        parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                      f'stroke="{EDGE_EXPLICIT}" stroke-width="1.5"/>')
    for edge in discovered_edges:
        a, b = tuple(edge)
        (x1, y1), (x2, y2) = coords[a], coords[b]
        parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                      f'stroke="{EDGE_INFERRED}" stroke-width="1.5" stroke-dasharray="4,3"/>')

    for entity_id in node_ids:
        x, y = coords[entity_id]
        is_center = entity_id == viewed_entity.entity_id
        if is_center:
            entity_type = viewed_entity.entity_type
        elif has_distinct_query_node and entity_id == query_entity.entity_id:
            entity_type = query_entity.entity_type
        else:
            entity_type = _entity_type_of(entity_id, connections, repo)
        color = NODE_COLORS.get(entity_type, DEFAULT_NODE_COLOR)
        r = 10 if is_center else 7
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" stroke="#FFFFFF" stroke-width="1.5"/>')
        parts.append(f'<text x="{x:.1f}" y="{y + r + 12:.1f}" text-anchor="middle" font-size="10" '
                      f'font-family="Montserrat, sans-serif" fill="#3D3A57">{_xml_escape(entity_id)}</text>')

    return (
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="Mini-grafo de conexiones">' + "".join(parts) + "</svg>"
    )


def serialize_comparison(comparison) -> dict:
    """`comparison`: ComparisonResult (application/auditar_resultado.py)."""
    return {
        "score_delta": comparison.score_delta,
        "dominant_feature": comparison.dominant_feature,
        "dominant_feature_label": FEATURE_LABELS.get(comparison.dominant_feature, comparison.dominant_feature),
        "features": tuple(
            {
                "name": f.name, "label": FEATURE_LABELS.get(f.name, f.name),
                "value_a": f.value_a, "value_b": f.value_b,
                "weight": f.weight, "delta": f.delta, "favors": f.favors,
            }
            for f in comparison.features
        ),
    }
