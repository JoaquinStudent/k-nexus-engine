"""Agregación campo→entidad + fusión RRF de los rankings denso y léxico.

Los índices (Sprint-03) devuelven hits a nivel de CAMPO — `(Provenance, score)`.
Antes de fusionar hay que decidir, por entidad, cuál es su mejor campo (esa es
la evidencia que se muestra en la UI, per `DESIGN.md:195`) y qué score de esa
entidad entra al ranking.

RRF sirve ÚNICAMENTE para generar candidatos (recall) — el `rrf_score` de
`FusedCandidate` NUNCA debe usarse como score final. El score final sale
exclusivamente de `domain.scoring.compute_score` sobre las 7 features.
"""
from dataclasses import dataclass

RRF_K = 60


def aggregate_by_entity(hits: tuple) -> dict:
    """hits: tuple[(Provenance, score)]. Retorna {entity_id: (Provenance, score)}
    quedándose, por entidad, con el campo de mayor score (max-pool)."""
    best = {}
    for ref, score in hits:
        current = best.get(ref.entity_id)
        if current is None or score > current[1]:
            best[ref.entity_id] = (ref, score)
    return best


def _rank_order(aggregated: dict) -> tuple:
    return tuple(sorted(aggregated, key=lambda entity_id: -aggregated[entity_id][1]))


def reciprocal_rank_fusion(*rankings: tuple, k: int = RRF_K) -> dict:
    """rankings: cada uno es una tupla de entity_id ordenada por relevancia
    (rank 0 = mejor). RRF(e) = Σ 1/(k + rank_i(e) + 1) sobre los rankings donde
    aparece `e`; una entidad ausente de un ranking simplemente no suma desde
    ahí (no se rellena con 0)."""
    scores = {}
    for ranking in rankings:
        for rank, entity_id in enumerate(ranking):
            scores[entity_id] = scores.get(entity_id, 0.0) + 1.0 / (k + rank + 1)
    return scores


@dataclass(frozen=True)
class FusedCandidate:
    entity_id: str
    rrf_score: float
    evidence: object  # Provenance del mejor campo (denso si existe, si no léxico)
    sim_semantic: float  # coseno del mejor campo denso; 0.0 si sólo vino por léxico


def fuse(dense_hits: tuple, bm25_hits: tuple, top_n: int = 50) -> tuple:
    """Agrega ambos rankings a nivel entidad, los fusiona con RRF y retorna los
    `top_n` `FusedCandidate` — el fin del rol de RRF en el pipeline."""
    dense_agg = aggregate_by_entity(dense_hits)
    bm25_agg = aggregate_by_entity(bm25_hits)
    rrf_scores = reciprocal_rank_fusion(_rank_order(dense_agg), _rank_order(bm25_agg))

    ranked_ids = sorted(rrf_scores, key=lambda entity_id: -rrf_scores[entity_id])[:top_n]

    candidates = []
    for entity_id in ranked_ids:
        if entity_id in dense_agg:
            evidence, sim_semantic = dense_agg[entity_id]
        else:
            evidence, _ = bm25_agg[entity_id]
            sim_semantic = 0.0
        candidates.append(FusedCandidate(
            entity_id=entity_id,
            rrf_score=rrf_scores[entity_id],
            evidence=evidence,
            sim_semantic=sim_semantic,
        ))
    return tuple(candidates)
