"""Use-case principal (F3+F4 de ARCHITECTURE.md): recuperación híbrida +
reranking explicable. Una consulta entra, sale una lista rankeada de
conexiones con score desglosado, tipo de relación y evidencia trazable.

Regla que no se rompe: el `rrf_score` de la fusión SÓLO sirve para generar
candidatos (recall). El orden final sale exclusivamente de
`domain.scoring.compute_score` sobre las 7 features — nunca del RRF.

Pipeline en dos pasadas (`graph_linked` es relacional, ADR-008): hace falta
saber quiénes son los candidatos fuertes de ESTA consulta antes de poder decir
si otro candidato está "enlazado" a ellos.

Expansión por grafo (hallazgo al probar contra datos reales): un investigador
casi nunca comparte vocabulario textual con una necesidad — su perfil académico
no repite las palabras del problema. Si sólo se puntúan los candidatos que la
búsqueda textual trajo, `graph_linked` queda correcto pero VACÍO en la
práctica: nunca hay investigadores en el pool a puntuar. Por eso, tras la
pasada 1, se AMPLÍA el pool con los vecinos directos de los candidatos fuertes
— literalmente "el investigador no lo trae el texto, lo trae la arista", que es
el propio argumento de ADR-008 llevado a su conclusión.
"""
from dataclasses import dataclass

from src.adapters.repository.projection import to_candidate_entity
from src.adapters.retrieval.fusion import FusedCandidate, fuse
from src.application.query_builder import build_query
from src.domain.features import compute_features
from src.domain.models import CandidatePair, ScoredResult
from src.domain.relation_type import classify_relation
from src.domain.scoring import WEIGHTS, compute_score

DEFAULT_TOP_N = 50
DEFAULT_TOP_K_SEEDS = 10
RETRIEVAL_K = 200  # candidatos por índice antes de fusionar (recall amplio)


def feature_contributions(feature_vector) -> tuple:
    """(nombre, valor, contribución normalizada al score) para las features
    activas (no-N/A) — la MISMA lógica de re-normalización que `compute_score`,
    expuesta para poder explicar qué pesó más."""
    active = {name: getattr(feature_vector, name) for name in WEIGHTS if getattr(feature_vector, name) is not None}
    total_weight = sum(WEIGHTS[name] for name in active)
    if not total_weight:
        return ()
    return tuple(
        (name, active[name], WEIGHTS[name] * active[name] / total_weight)
        for name in active
    )


def top_features(feature_vector, n: int = 3) -> tuple:
    """Las `n` features que más explican el score — DATOS estructurados, no
    prosa. La redacción en lenguaje natural es del `Explainer` (Sprint-05)."""
    contributions = feature_contributions(feature_vector)
    return tuple(sorted(contributions, key=lambda c: -c[2])[:n])


@dataclass(frozen=True)
class RankedConnection:
    rank: int
    scored: object          # ScoredResult (domain)
    entity: object          # StoredEntity (ports) — la entidad completa
    evidence: object        # Provenance del campo que justificó la recuperación
    evidence_text: str      # texto de ese campo, listo para mostrar
    top_features: tuple     # (nombre, valor, contribución) descendente


def _best_own_text(entity):
    """Provenance del campo más largo (más informativo) de la propia entidad
    — evidencia razonable para un candidato que entró por el grafo, no por
    texto (no tiene un "mejor campo frente a la query" que ofrecer)."""
    if not entity.texts:
        return None
    return max(entity.texts, key=lambda t: len(t.text)).provenance


def _expand_by_graph(seed_ids: tuple, graph, repo, exclude_ids: set) -> tuple:
    """Vecinos directos de los `seed_ids` que aún no están en el pool —
    candidatos que sólo la estructura del grafo puede justificar."""
    expanded = []
    seen = set(exclude_ids)
    for seed_id in seed_ids:
        for neighbor_id in graph.neighbors(seed_id):
            if neighbor_id in seen:
                continue
            seen.add(neighbor_id)
            try:
                neighbor_entity = repo.get(neighbor_id)
            except KeyError:
                continue
            evidence = _best_own_text(neighbor_entity)
            if evidence is None:
                continue
            expanded.append(FusedCandidate(
                entity_id=neighbor_id, rrf_score=0.0, evidence=evidence, sim_semantic=0.0,
            ))
    return tuple(expanded)


def _evidence_text(entity, evidence) -> str:
    for provenanced_text in entity.texts:
        if provenanced_text.provenance == evidence:
            return provenanced_text.text
    return ""


def _score_candidate(query, entity, *, graph=None, seed_ids=(), capabilities=(), sim_semantic):
    candidate_entity = to_candidate_entity(
        entity, graph=graph, seed_ids=seed_ids, capabilities=capabilities,
    )
    feature_vector = compute_features(CandidatePair(
        query=query, candidate=candidate_entity, sim_semantic=sim_semantic,
    ))
    score = compute_score(feature_vector)
    relation_type = classify_relation(feature_vector, candidate_entity.entity_type)
    return feature_vector, score, relation_type


def descubrir_conexiones(
    query_input: str,
    *,
    repo,
    dense_index,
    lexical_index,
    graph,
    top_n: int = DEFAULT_TOP_N,
    top_k_seeds: int = DEFAULT_TOP_K_SEEDS,
    retrieval_k: int = RETRIEVAL_K,
) -> tuple:
    """`repo`: EntityRepository · `dense_index`: VectorIndex ya construido ·
    `lexical_index`: LexicalIndex ya construido · `graph`: GraphStore. Ninguno
    se instancia aquí (Regla A2) — los construye el composition root."""
    query = build_query(query_input, repo)

    # Si la consulta ES una entidad del dataset (NEED/PROJECT/...), se excluye
    # de sus propios resultados — si no, aparecería como su mejor match trivial.
    try:
        self_entity_id = repo.get(query_input.strip()).entity_id
    except KeyError:
        self_entity_id = None

    dense_hits = dense_index.search(query.text, k=retrieval_k)
    lexical_hits = lexical_index.search(query.text, k=retrieval_k)
    if self_entity_id is not None:
        dense_hits = tuple(h for h in dense_hits if h[0].entity_id != self_entity_id)
        lexical_hits = tuple(h for h in lexical_hits if h[0].entity_id != self_entity_id)
    fused = fuse(dense_hits, lexical_hits, top_n=top_n)  # fin del rol de RRF

    capabilities = repo.by_type("CAPABILITY")
    entities = {c.entity_id: repo.get(c.entity_id) for c in fused}

    # Pasada 1 — sin contexto de grafo: encontrar los candidatos fuertes.
    pass1_scores = {}
    for candidate in fused:
        _, score, _ = _score_candidate(
            query, entities[candidate.entity_id],
            capabilities=capabilities, sim_semantic=candidate.sim_semantic,
        )
        pass1_scores[candidate.entity_id] = score
    seed_ids = tuple(
        sorted(pass1_scores, key=lambda entity_id: -pass1_scores[entity_id])[:top_k_seeds]
    )
    exclude = set(entities) | ({self_entity_id} if self_entity_id else set())
    expanded_candidates = _expand_by_graph(seed_ids, graph, repo, exclude)
    for candidate in expanded_candidates:
        entities[candidate.entity_id] = repo.get(candidate.entity_id)

    # Pasada 2 — con el grafo ya informado por los fuertes de esta consulta;
    # el pool crece con los vecinos de esos fuertes (ver docstring del módulo).
    scored_rows = []
    for candidate in fused + expanded_candidates:
        entity = entities[candidate.entity_id]
        feature_vector, score, relation_type = _score_candidate(
            query, entity, graph=graph, seed_ids=seed_ids,
            capabilities=capabilities, sim_semantic=candidate.sim_semantic,
        )
        scored_rows.append((entity, candidate, feature_vector, score, relation_type))

    scored_rows.sort(key=lambda row: -row[3])

    connections = []
    for rank, (entity, candidate, feature_vector, score, relation_type) in enumerate(scored_rows, start=1):
        scored = ScoredResult(
            entity_id=entity.entity_id, feature_vector=feature_vector,
            score=score, relation_type=relation_type,
        )
        connections.append(RankedConnection(
            rank=rank,
            scored=scored,
            entity=entity,
            evidence=candidate.evidence,
            evidence_text=_evidence_text(entity, candidate.evidence),
            top_features=top_features(feature_vector),
        ))
    return tuple(connections)
