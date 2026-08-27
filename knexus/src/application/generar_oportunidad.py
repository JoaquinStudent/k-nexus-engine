"""Use-case de ensamblado de oportunidad (F5 de ARCHITECTURE.md): construye la
cadena necesidad→antecedente→investigador→capacidad→currículo para los
mejores antecedentes de una consulta.

Reutiliza `descubrir_conexiones` (Sprint-04) para los antecedentes — NO rehace
recuperación. Cada eslabón declara su `link_type` (`domain/opportunity.py`):
el antecedente es "retrieved"; investigador y currículo son "edge" (arista
real / FK real: researcher_project.csv, primary_program_id); capacidad es
"inferred" (no hay tabla de enlace — ADR-008).

Degradación honesta: si un antecedente no tiene investigador conectado, o
ninguna capacidad/componente curricular coincide, esos eslabones simplemente
NO aparecen en la cadena — nunca se fabrica uno para completar el dibujo.
"""
from src.adapters.repository.capability_match import find_matching_capability
from src.adapters.repository.projection import to_candidate_entity
from src.adapters.retrieval.fusion import aggregate_by_entity
from src.application.descubrir_conexiones import descubrir_conexiones
from src.application.query_builder import build_query
from src.domain.features import compute_features
from src.domain.models import CandidatePair
from src.domain.opportunity import ChainLink, Opportunity, classify_opportunity, opportunity_priority
from src.domain.scoring import compute_score
from src.ports.entity_repository import StoredEntity

DEFAULT_TOP_ANTECEDENTES = 3
CURRICULAR_SCORE_THRESHOLD = 0.30
CURRICULAR_SEARCH_K = 1000  # generoso: sólo unos pocos subjects/competencies por programa


def _cross_faculty(need_entity, researcher_entity) -> bool:
    faculty_id = researcher_entity.raw.get("faculty_id", "")
    originating_unit = need_entity.raw.get("originating_unit", "")
    if not faculty_id or not originating_unit:
        return False
    return faculty_id not in originating_unit


def _pick_researcher(antecedente_id: str, graph, repo):
    """Primer vecino de tipo RESEARCHER — arista real de researcher_project.csv."""
    for neighbor_id in graph.neighbors(antecedente_id):
        try:
            neighbor = repo.get(neighbor_id)
        except KeyError:
            continue
        if neighbor.entity_type == "RESEARCHER":
            return neighbor
    return None


def _curricular_candidates(researcher_entity, repo) -> tuple:
    program_id = researcher_entity.raw.get("primary_program_id", "")
    if not program_id:
        return ()
    subjects = tuple(e for e in repo.by_type("SUBJECT") if e.raw.get("program_id") == program_id)
    competencies = tuple(e for e in repo.by_type("COMPETENCY") if e.raw.get("program_id") == program_id)
    return subjects + competencies


def _pick_curricular(query, researcher_entity, repo, dense_index, capabilities):
    """El componente curricular del programa del investigador que MEJOR
    puntúa contra la consulta (mismas 7 features que todo lo demás) — no el
    primero del programa. `sim_semantica` sale de re-usar el índice denso ya
    construido (agregación campo→entidad, igual que en la fusión de Sprint-04)."""
    candidates = _curricular_candidates(researcher_entity, repo)
    if not candidates:
        return None

    dense_hits = dense_index.search(query.text, k=CURRICULAR_SEARCH_K)
    sims_by_entity = aggregate_by_entity(dense_hits)

    best_entity, best_score = None, -1.0
    for candidate_entity in candidates:
        _, sim_semantic = sims_by_entity.get(candidate_entity.entity_id, (None, 0.0))
        candidate = to_candidate_entity(candidate_entity, capabilities=capabilities)
        feature_vector = compute_features(CandidatePair(
            query=query, candidate=candidate, sim_semantic=sim_semantic,
        ))
        score = compute_score(feature_vector)
        if score > best_score:
            best_entity, best_score = candidate_entity, score

    if best_entity is None or best_score < CURRICULAR_SCORE_THRESHOLD:
        return None
    return best_entity, best_score


def _build_opportunity(need_entity, query, connection, *, repo, graph, dense_index, capabilities) -> Opportunity:
    links = [
        ChainLink(
            role="necesidad", entity_id=need_entity.entity_id,
            entity_type=need_entity.entity_type.lower(), link_type="retrieved",
        ),
        ChainLink(
            role="antecedente", entity_id=connection.entity.entity_id,
            entity_type=connection.entity.entity_type.lower(), link_type="retrieved",
            score=connection.scored.score, relation_type=connection.scored.relation_type,
            rationale_features=tuple((name, value) for name, value, _ in connection.top_features),
        ),
    ]

    researcher = _pick_researcher(connection.entity.entity_id, graph, repo)
    cross_faculty = False
    if researcher is not None:
        cross_faculty = _cross_faculty(need_entity, researcher)
        links.append(ChainLink(
            role="investigador", entity_id=researcher.entity_id,
            entity_type="researcher", link_type="edge",
        ))

    matching_capability = find_matching_capability(
        connection.entity.domains, connection.entity.methods, capabilities,
    )
    if matching_capability is not None:
        links.append(ChainLink(
            role="capacidad", entity_id=matching_capability.entity_id,
            entity_type="capability", link_type="inferred",
            rationale_features=(("capacidad", matching_capability.raw.get("capability_name", "")),),
        ))

    if researcher is not None:
        picked = _pick_curricular(query, researcher, repo, dense_index, capabilities)
        if picked is not None:
            curricular_entity, curricular_score = picked
            links.append(ChainLink(
                role="curriculo", entity_id=curricular_entity.entity_id,
                entity_type=curricular_entity.entity_type.lower(), link_type="edge",
                score=curricular_score,
            ))

    links = tuple(links)
    return Opportunity(
        need_id=need_entity.entity_id,
        links=links,
        opportunity_type=classify_opportunity(links, cross_faculty=cross_faculty),
        priority=opportunity_priority(links),
        score=connection.scored.score,
    )


def generar_oportunidad(
    query_input: str,
    *,
    repo,
    dense_index,
    lexical_index,
    graph,
    top_antecedentes: int = DEFAULT_TOP_ANTECEDENTES,
) -> tuple:
    """Una `Opportunity` por cada uno de los `top_antecedentes` mejores
    resultados de `descubrir_conexiones`. Ninguna dependencia se instancia
    aquí (Regla A2) — se reciben ya construidas."""
    connections = descubrir_conexiones(
        query_input, repo=repo, dense_index=dense_index, lexical_index=lexical_index, graph=graph,
    )
    if not connections:
        return ()

    query = build_query(query_input, repo)
    try:
        need_entity = repo.get(query_input.strip())
    except KeyError:
        need_entity = None
    if need_entity is None:
        # Consulta en texto libre: no hay entidad NEED que anclar la cadena;
        # se usa el propio texto como identificador de la "necesidad".
        need_entity = StoredEntity(entity_id=query_input, entity_type="QUERY")

    capabilities = repo.by_type("CAPABILITY")

    opportunities = []
    for connection in connections[:top_antecedentes]:
        opportunities.append(_build_opportunity(
            need_entity, query, connection,
            repo=repo, graph=graph, dense_index=dense_index, capabilities=capabilities,
        ))
    return tuple(opportunities)
