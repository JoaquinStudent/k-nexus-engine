"""DTO del backend -> dict de presentación. PURO: sin FastAPI, sin Jinja, sin
pipeline — testeable en aislamiento (`tests/interface/test_presenters.py`).

Reusa el vocabulario ya existente en vez de duplicarlo: las etiquetas ES vienen
de `adapters/explain/template_explainer.py` (la misma redacción que ve el
Explainer), los umbrales de relevancia son los de `domain/opportunity.py`
(una sola vara de medir en todo el sistema), y la contribución por feature
sale de `application/descubrir_conexiones.feature_contributions` — no se
reimplementa la re-normalización de ADR-007/ADR-009 aquí.
"""
import textwrap
from html import escape as _xml_escape
from urllib.parse import quote as _urlquote

import networkx as nx

from src.adapters.explain.template_explainer import (
    ARM_HELP, FEATURE_HELP, FEATURE_LABELS, LINK_TYPE_LABELS, OPPORTUNITY_TYPE_LABELS,
    RELATION_HELP, RELATION_LABELS, ROLE_LABELS,
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


def reason_text(top_features_tuple) -> str:
    """Frase en lenguaje natural para la tarjeta de resultado (M2/UX), a partir
    de `top_features` (ya calculado por `descubrir_conexiones.top_features` —
    no se reimplementa la selección aquí). Sin top_features, cadena vacía: la
    plantilla cae al rótulo de tipo de relación como respaldo."""
    if not top_features_tuple:
        return ""
    parts = [
        f"{FEATURE_LABELS.get(name, name)} ({value:.2f})"
        for name, value, _pct in top_features_tuple
    ]
    return "Destaca por " + ", ".join(parts)


def feature_glossary() -> tuple:
    """Una entrada por feature en el orden de `WEIGHTS`, para el bloque
    "Cómo leer esto" (M9/UX) — misma fuente que la Relevance Breakdown Bar,
    nunca un texto duplicado en la plantilla."""
    return tuple(
        {"name": name, "label": FEATURE_LABELS.get(name, name), "help": FEATURE_HELP.get(name, "")}
        for name in WEIGHTS
    )


def relation_glossary() -> tuple:
    return tuple(
        {"relation_type": key, "label": RELATION_LABELS[key], "help": RELATION_HELP.get(key, "")}
        for key in RELATION_LABELS
    )


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
        "relation_help": RELATION_HELP.get(scored.relation_type, ""),
        "reason": reason_text(connection.top_features),
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
    # Añadidos: `researcher_group`/`publication_*` (networkx_store.py) SÍ
    # aparecen como vecinos reales en el grafo — antes cara sin color propio
    # caían en DEFAULT_NODE_COLOR, indistinguibles entre sí y sin leyenda.
    "RESEARCH_GROUP": "#3A2E6E", "PUBLICATION": "#9C7A3C",
}
DEFAULT_NODE_COLOR = "#8A86A6"
EDGE_EXPLICIT = "#3D3A57"
EDGE_INFERRED = "#C3BEEF"
SUBGRAPH_MAX_NODES = 15  # tope de DESIGN.md M6: "no un hairball"
NODE_LABEL_MAX_CHARS = 18  # ancho de línea de la etiqueta bajo cada nodo
NODE_LABEL_LINE_HEIGHT = 11


def _resolves_to_entity(entity_id: str, connections, repo=None) -> bool:
    """Algunas aristas del grafo (`researcher_expertise`, networkx_store.py)
    apuntan a un id (`EXP-...`) que nunca se cargó como entidad — no hay
    `ENTITY_TABLES` para eso. Ese vecino no tiene tipo, ni color, ni nombre
    legible, y su link de `/connection/{id}` siempre da 404: se filtra antes
    de entrar al grafo en vez de dibujarse como un gris sin explicación."""
    for connection in connections:
        if connection.entity.entity_id == entity_id:
            return True
    if repo is not None:
        try:
            repo.get(entity_id)
            return True
        except KeyError:
            return False
    return False


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


def _node_label(entity_id: str, connections, repo=None) -> str:
    """Título completo legible para un nodo del mini-grafo (UX) — antes sólo se
    mostraba el `entity_id` crudo, ilegible para quien no conoce el dataset.
    Sin truncar: el grafo es arrastrable/con zoom (JS embebido en el SVG), así
    que un nombre largo se resuelve separando nodos, no cortando texto."""
    for connection in connections:
        if connection.entity.entity_id == entity_id:
            return title_of(connection.entity)
    if repo is not None:
        try:
            return title_of(repo.get(entity_id))
        except KeyError:
            return entity_id
    return entity_id


def _wrap_label(text: str) -> list:
    """Nombre completo, siempre — nunca truncado con `…`. Se parte en tantas
    líneas cortas como haga falta para que quepa bajo el nodo (el grafo es
    arrastrable/con zoom, así que más líneas sólo significa separar nodos)."""
    return textwrap.wrap(text, width=NODE_LABEL_MAX_CHARS) or [text]


def _label_markup(x: float, y: float, text: str) -> str:
    lines = _wrap_label(text)
    tspans = "".join(
        f'<tspan x="{x:.1f}" dy="{0 if i == 0 else NODE_LABEL_LINE_HEIGHT}">{_xml_escape(line)}</tspan>'
        for i, line in enumerate(lines)
    )
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-size="10" '
        f'font-family="Montserrat, sans-serif" fill="#3D3A57" paint-order="stroke" '
        f'stroke="#FFFFFF" stroke-width="3">{tspans}</text>'
    )


def _svg_dom_id(entity_id: str) -> str:
    """id de DOM válido para el <svg> (usado por el script embebido para
    encontrarse a sí mismo sin depender de `document.currentScript`, que en
    algunos navegadores no resuelve un <script> dentro de un elemento SVG)."""
    safe = "".join(c if c.isalnum() else "-" for c in entity_id)
    return f"graph-{safe}"


def subgraph_svg(viewed_entity, query_entity, connections, *, graph, repo=None, query: str = "",
                  width: int = 640, height: int = 420) -> str:
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
        if neighbor_id not in node_ids and _resolves_to_entity(neighbor_id, connections, repo):
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

    svg_id = _svg_dom_id(viewed_entity.entity_id)

    if len(node_ids) == 1:
        x, y = width / 2, height / 2
        color = NODE_COLORS.get(viewed_entity.entity_type, DEFAULT_NODE_COLOR)
        label = title_of(viewed_entity)
        return (
            f'<svg id="{svg_id}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
            f'role="img" aria-label="Mini-grafo de conexiones">'
            f'<title>Grafo con 1 entidad, sin vecinos registrados en los datos.</title>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10" fill="{color}" stroke="#FFFFFF" stroke-width="1.5"/>'
            + _label_markup(x, y + 24, label) + "</svg>"
        )

    # k crece con la cantidad de nodos (hasta 15, DESIGN.md M6) para que un
    # grafo lleno no amontone las etiquetas unas sobre otras.
    k = 0.9 + 0.06 * len(node_ids)
    pos = nx.spring_layout(g, seed=42, k=k)
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

    edge_parts = []
    for edge in explicit_edges:
        a, b = tuple(edge)
        (x1, y1), (x2, y2) = coords[a], coords[b]
        edge_parts.append(
            f'<line data-a="{_xml_escape(a)}" data-b="{_xml_escape(b)}" '
            f'x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{EDGE_EXPLICIT}" stroke-width="1.5"/>'
        )
    for edge in discovered_edges:
        a, b = tuple(edge)
        (x1, y1), (x2, y2) = coords[a], coords[b]
        edge_parts.append(
            f'<line data-a="{_xml_escape(a)}" data-b="{_xml_escape(b)}" '
            f'x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{EDGE_INFERRED}" stroke-width="1.5" stroke-dasharray="4,3"/>'
        )

    node_parts = []
    for entity_id in node_ids:
        x, y = coords[entity_id]
        is_center = entity_id == viewed_entity.entity_id
        is_query = has_distinct_query_node and entity_id == query_entity.entity_id
        if is_center:
            entity_type = viewed_entity.entity_type
            label = title_of(viewed_entity)
        elif is_query:
            entity_type = query_entity.entity_type
            label = title_of(query_entity)
        else:
            entity_type = _entity_type_of(entity_id, connections, repo)
            label = _node_label(entity_id, connections, repo)
        color = NODE_COLORS.get(entity_type, DEFAULT_NODE_COLOR)
        r = 10 if is_center else 7
        # data-id/-x/-y/-r: el script de abajo los lee para poder arrastrar
        # el nodo y recalcular las líneas conectadas sin recalcular el layout.
        node_group = (
            f'<g class="graph-node-group" data-id="{_xml_escape(entity_id)}" '
            f'data-x="{x:.1f}" data-y="{y:.1f}" data-r="{r}">'
            f'<circle class="graph-node" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" '
            f'stroke="#FFFFFF" stroke-width="1.5"><title>{_xml_escape(entity_id)}</title></circle>'
            + _label_markup(x, y + r + 12, label) + "</g>"
        )
        # sólo se enlazan entidades reales del dataset (no el nodo-consulta de
        # texto libre, que no tiene una página /connection propia) y no el
        # centro, que ya es la página en la que estás.
        is_linkable = not is_center and entity_type != "QUERY"
        if is_linkable:
            href = f"/connection/{_urlquote(entity_id, safe='')}?q={_urlquote(query, safe='')}"
            node_parts.append(f'<a href="{_xml_escape(href)}" class="graph-node-link">{node_group}</a>')
        else:
            node_parts.append(node_group)

    summary = (
        f"Grafo con {len(node_ids)} entidades y {len(explicit_edges) + len(discovered_edges)} vínculos: "
        f"{len(explicit_edges)} explícitos (línea sólida), {len(discovered_edges)} por ranking (línea punteada). "
        f"Arrastrable, con zoom (rueda) y paneo (arrastrar el fondo)."
    )
    return (
        f'<svg id="{svg_id}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="Mini-grafo de conexiones interactivo">'
        f'<title>{_xml_escape(summary)}</title>'
        f'<g class="knexus-graph-viewport">' + "".join(edge_parts) + "".join(node_parts) + "</g>"
        + _graph_interaction_script(svg_id) + "</svg>"
    )


def _graph_interaction_script(svg_id: str) -> str:
    """Zoom (rueda), paneo (arrastrar el fondo) y arrastre de nodos individuales
    — sin dependencias nuevas (rung 4 de la escalera): vanilla JS embebido en el
    propio SVG, se ejecuta solo al insertarse la página (progressive
    enhancement: sin JS, el grafo sigue siendo una imagen SVG válida y legible,
    sólo pierde la interacción). Usa un id de DOM en vez de
    `document.currentScript` porque ese accessor es poco fiable para un
    <script> dentro de contenido SVG en algunos navegadores."""
    return f"""<script>(function(){{
  var svg = document.getElementById("{svg_id}");
  if (!svg) return;
  var vp = svg.querySelector('.knexus-graph-viewport');
  var scale = 1, tx = 0, ty = 0;
  function applyTransform() {{ vp.setAttribute('transform', 'translate(' + tx + ',' + ty + ') scale(' + scale + ')'); }}
  function toLocalPoint(evt) {{
    var pt = svg.createSVGPoint();
    pt.x = evt.clientX; pt.y = evt.clientY;
    return pt.matrixTransform(svg.getScreenCTM().inverse());
  }}
  var nodes = {{}};
  svg.querySelectorAll('.graph-node-group').forEach(function(g) {{
    var id = g.getAttribute('data-id');
    nodes[id] = {{
      circle: g.querySelector('circle'), text: g.querySelector('text'),
      tspans: g.querySelectorAll('tspan'),
      x: parseFloat(g.getAttribute('data-x')), y: parseFloat(g.getAttribute('data-y')),
      r: parseFloat(g.getAttribute('data-r')), dragDist: 0, wasDragged: false
    }};
    var anchor = g.closest('a');
    if (anchor) {{
      anchor.addEventListener('click', function(e) {{
        if (nodes[id].wasDragged) {{ e.preventDefault(); nodes[id].wasDragged = false; }}
      }});
    }}
    g.addEventListener('pointerdown', function(e) {{
      // Capturado en el propio <g>, no en <svg>: si se capturara en <svg> el
      // click resultante se retargetea a <svg> y el navegador nunca navega
      // el <a>. Capturado aquí, el click retargeteado sigue burbujeando por
      // <a> (su ancestro) — y el arrastre no se corta si el puntero se
      // escapa del círculo (chico) al moverse rápido.
      dragId = id; dragStart = toLocalPoint(e); nodes[id].dragDist = 0;
      e.stopPropagation();
      g.setPointerCapture(e.pointerId);
    }});
  }});
  var lines = svg.querySelectorAll('line[data-a]');
  function moveNode(id) {{
    var n = nodes[id];
    n.circle.setAttribute('cx', n.x); n.circle.setAttribute('cy', n.y);
    n.text.setAttribute('x', n.x); n.text.setAttribute('y', n.y + n.r + 12);
    n.tspans.forEach(function(t) {{ t.setAttribute('x', n.x); }});
    lines.forEach(function(line) {{
      if (line.getAttribute('data-a') === id) {{ line.setAttribute('x1', n.x); line.setAttribute('y1', n.y); }}
      if (line.getAttribute('data-b') === id) {{ line.setAttribute('x2', n.x); line.setAttribute('y2', n.y); }}
    }});
  }}
  var dragId = null, dragStart = null, panning = false, panStart = null;
  svg.addEventListener('pointerdown', function(e) {{
    panning = true; panStart = toLocalPoint(e);
    svg.setPointerCapture(e.pointerId);
  }});
  svg.addEventListener('pointermove', function(e) {{
    var p = toLocalPoint(e);
    if (dragId) {{
      var n = nodes[dragId];
      var ddx = (p.x - dragStart.x) / scale, ddy = (p.y - dragStart.y) / scale;
      n.x += ddx; n.y += ddy;
      n.dragDist += Math.abs(ddx) + Math.abs(ddy);
      if (n.dragDist > 3) nodes[dragId].wasDragged = true;
      dragStart = p;
      moveNode(dragId);
    }} else if (panning) {{
      tx += (p.x - panStart.x); ty += (p.y - panStart.y);
      panStart = p;
      applyTransform();
    }}
  }});
  function endDrag() {{ dragId = null; panning = false; }}
  svg.addEventListener('pointerup', endDrag);
  svg.addEventListener('pointerleave', endDrag);
  svg.addEventListener('wheel', function(e) {{
    e.preventDefault();
    var p = toLocalPoint(e);
    var localX = (p.x - tx) / scale, localY = (p.y - ty) / scale;
    var factor = e.deltaY < 0 ? 1.15 : (1 / 1.15);
    scale = Math.min(4, Math.max(0.4, scale * factor));
    tx = p.x - localX * scale; ty = p.y - localY * scale;
    applyTransform();
  }}, {{passive: false}});
}})();</script>"""


# --- Métricas (M8, Sprint-07): dict de `evaluation/results.json` -> presentación ---

ARMS_ORDER = ("full", "cosine", "dense")
ARM_LABELS = {"full": "Pipeline completo", "cosine": "Reorden por coseno", "dense": "Sólo denso"}

# Umbral único para pintar accionable_rate/trap_rate en la tabla de validez de
# constructo (verde/rojo) — mismo criterio simple en toda la fila, nunca un
# umbral distinto por brazo. No es un umbral de dominio (no vive en
# domain/opportunity.py como ALTO/MEDIO): es puramente de presentación, para
# que la tabla no dependa de leer los números con cuidado para notar cuál
# brazo va mejor.
_QUALITY_THRESHOLD = 0.4


def _quality_class(value: float, *, good_when_high: bool) -> str:
    is_good = (value >= _QUALITY_THRESHOLD) if good_when_high else (value < _QUALITY_THRESHOLD)
    return "stat-positive" if is_good else "stat-negative"


def serialize_metrics(report: dict | None) -> dict:
    """`report`: dict ya cargado de `evaluation/results.json`
    (`interface/metrics_report.load_report()`), o `None` si el archivo no
    existe todavía. PURA: no importa `evaluation/`, sólo transforma un dict.

    Sin medición registrada, `available=False` es un estado válido (M9),
    nunca un error — mismo criterio que una query vacía en `/api/discover`.

    Todas las barras (`pct`) son directamente `valor * 100`: precision/recall/
    MRR/tasas de `harness.py` ya viven en [0, 1] por construcción, así que no
    hace falta normalizar contra un máximo — el ancho queda acotado a [0, 100]
    sin casos borde de división por cero."""
    if report is None:
        return {"available": False}

    meta = report["meta"]
    pr_cluster = report["precision_recall"]["cluster"]
    construct = report["construct_validity"]

    return {
        "available": True,
        "meta": meta,
        "stat_tiles": (
            {"label": "Entidades indexadas", "value": str(meta.get("entities_indexed", "-"))},
            {"label": "Latencia promedio", "value": f"{report['avg_latency_ms']:.0f} ms"},
            {"label": "Cobertura de evidencia", "value": f"{report['evidence_coverage'] * 100:.0f}%"},
        ),
        "precision_at_k": (
            {"label": "P@5", "value": pr_cluster["full"]["p5"], "pct": pr_cluster["full"]["p5"] * 100},
            {"label": "P@10", "value": pr_cluster["full"]["p10"], "pct": pr_cluster["full"]["p10"] * 100},
        ),
        "ablation": tuple(
            {"arm": arm, "label": ARM_LABELS[arm], "help": ARM_HELP[arm],
             "p5": pr_cluster[arm]["p5"], "pct": pr_cluster[arm]["p5"] * 100}
            for arm in ARMS_ORDER
        ),
        "ablation_delta_cosine": pr_cluster["full"]["p5"] - pr_cluster["cosine"]["p5"],
        "ablation_delta_dense": pr_cluster["full"]["p5"] - pr_cluster["dense"]["p5"],
        "recall_ceilings": report["recall_ceilings"]["cluster"],
        "construct_validity": tuple(
            {
                "arm": arm, "label": ARM_LABELS[arm], **construct[arm],
                "trap_class": _quality_class(construct[arm]["trap_rate"], good_when_high=False),
                "actionable_class": _quality_class(construct[arm]["actionable_rate"], good_when_high=True),
            }
            for arm in ARMS_ORDER
        ),
        "per_need": report["per_need"],
    }


def _display_favors(f) -> str:
    """`f.favors` (auditar_resultado.py) compara la CONTRIBUCIÓN exacta — hasta
    la última cifra de punto flotante — para que la suma de deltas cuadre con
    el delta de score. Pero la UI redondea `value_a`/`value_b` a 2 decimales,
    así que un delta minúsculo (ruido del modelo de embeddings) puede mostrar
    el mismo número en ambos lados con el ✓ en uno solo — parece arbitrario.
    Si lo que se VE es igual, se muestra como empate aunque por debajo haya
    ganado alguien por 0.0003."""
    if f.value_a is None or f.value_b is None:
        return f.favors
    if round(f.value_a, 2) == round(f.value_b, 2):
        return "empate"
    return f.favors


def serialize_comparison(comparison, *, explainer=None) -> dict:
    """`comparison`: ComparisonResult (application/auditar_resultado.py).
    `explainer` es opcional (puerto Explainer) — sin él, `explanation` queda
    vacío en vez de fallar, mismo patrón que `serialize_connection`."""
    return {
        "score_delta": comparison.score_delta,
        "dominant_feature": comparison.dominant_feature,
        "dominant_feature_label": FEATURE_LABELS.get(comparison.dominant_feature, comparison.dominant_feature),
        "features": tuple(
            {
                "name": f.name, "label": FEATURE_LABELS.get(f.name, f.name),
                "value_a": f.value_a, "value_b": f.value_b,
                "weight": f.weight, "delta": f.delta, "favors": _display_favors(f),
            }
            for f in comparison.features
        ),
        "explanation": explainer.explain_comparison(comparison) if explainer is not None else "",
    }
