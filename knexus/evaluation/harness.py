"""Arnés de evaluación (Sprint-07): corre los tres brazos del ablation sobre
el set etiquetado (`qrels.csv`) y arma el dict que se serializa a
`results.json` (lo consume `/api/metrics`, ver `scripts/evaluate.py` e
`interface/metrics_report.py`).

Regla A2 (extendida a `evaluation/`, aunque no es parte del hexágono de
`src/`): este módulo NO instancia adapters — los recibe ya construidos desde
`scripts/evaluate.py` (que reusa `interface/composition.build_pipeline`,
igual que el CLI y la app).

**Tres brazos, tres preguntas distintas (SPEC.md §13):**
- `full` — el pipeline real: RRF + expansión por grafo + reranking de 7
  features (`descubrir_conexiones`).
- `cosine` — LOS MISMOS candidatos de `full`, re-ordenados por
  `feature_vector.sim_semantica`. Aísla la DECISIÓN DE ORDEN: compara "¿el
  reranker ordena mejor que el coseno crudo sobre el mismo pool?" — los
  sesgos del propio pool (SPEC.md §13) se cancelan en este delta.
- `dense` — top-K directo del índice denso, SIN RRF, SIN expansión de grafo,
  SIN reranking (`_dense_only_ranked`). Aísla el SISTEMA completo: es el
  buscador de "similarity" puro con el que compite todo lo demás — el
  argumento literal de R6 ("similarity != relevance"). Sus candidatos pueden
  no haber sido puntuados nunca por el pipeline real (nunca entraron al pool
  fusionado); `_construct_validity` lo reporta como `unscored_rate`, nunca
  como un 0 falso (mismo principio que N/A + re-normalización de ADR-007).
"""
import time
from dataclasses import dataclass

from evaluation import metrics, qrels
from src.adapters.retrieval.fusion import aggregate_by_entity
from src.application.descubrir_conexiones import descubrir_conexiones
from src.application.query_builder import build_query

TOP_K_PRIMARY = 5
TOP_K_SECONDARY = 10
TOP_K_RECALL_WIDE = 30
DENSE_RETRIEVAL_K = 200  # mismo ancho que RETRIEVAL_K del pipeline real -- comparación justa

# "Accionable" = tipos de relación con valor de decisión directo (método
# transferible confirmado o capacidad institucional disponible) — subconjunto
# deliberadamente más estricto que "no es la trampa" (ver relation_type.py).
ACTIONABLE_RELATION_TYPES = ("antecedente_metodologico", "activacion_capacidad")
TRAP_RELATION_TYPE = "coincidencia_superficial"

ARMS = ("full", "cosine", "dense")


@dataclass(frozen=True)
class NeedRun:
    need_id: str
    latency_s: float          # latencia del pipeline real (full)
    dense_latency_s: float    # latencia del brazo denso puro -- el contraste también es evidencia
    full_ranked: tuple        # entity_id ordenados por compute_score (el pipeline real)
    cosine_ranked: tuple      # mismos candidatos, re-ordenados por sim_semantica
    dense_ranked: tuple       # top-K del índice denso puro, sin RRF/grafo/reranking
    full_connections: tuple   # RankedConnection en orden "full" -- insumo de construct-validity


def _cosine_order(connections: tuple) -> tuple:
    return tuple(sorted(connections, key=lambda c: -c.scored.feature_vector.sim_semantica))


def _dense_only_ranked(query_input: str, *, repo, dense_index, k: int = DENSE_RETRIEVAL_K) -> tuple:
    """Brazo "similarity puro": ningún RRF, ninguna expansión de grafo,
    ningún reranking de 7 features -- sólo coseno del índice denso, agregado
    campo->entidad (`aggregate_by_entity`, reusado de `adapters/retrieval/fusion.py`,
    el mismo max-pool que usa el pipeline real) y ordenado por ese score."""
    query = build_query(query_input, repo)
    try:
        self_entity_id = repo.get(query_input.strip()).entity_id
    except KeyError:
        self_entity_id = None

    hits = dense_index.search(query.text, k=k)
    if self_entity_id is not None:
        hits = tuple(h for h in hits if h[0].entity_id != self_entity_id)

    aggregated = aggregate_by_entity(hits)
    return tuple(sorted(aggregated, key=lambda entity_id: -aggregated[entity_id][1]))


def run_need(need_id: str, *, repo, dense_index, lexical_index, graph) -> NeedRun:
    t0 = time.perf_counter()
    connections = descubrir_conexiones(
        need_id, repo=repo, dense_index=dense_index, lexical_index=lexical_index, graph=graph,
    )
    latency = time.perf_counter() - t0

    t1 = time.perf_counter()
    dense_ranked = _dense_only_ranked(need_id, repo=repo, dense_index=dense_index)
    dense_latency = time.perf_counter() - t1

    return NeedRun(
        need_id=need_id,
        latency_s=latency,
        dense_latency_s=dense_latency,
        full_ranked=tuple(c.entity.entity_id for c in connections),
        cosine_ranked=tuple(c.entity.entity_id for c in _cosine_order(connections)),
        dense_ranked=dense_ranked,
        full_connections=connections,
    )


def _ranked_for_arm(run: NeedRun, arm: str) -> tuple:
    if arm == "full":
        return run.full_ranked
    if arm == "cosine":
        return run.cosine_ranked
    return run.dense_ranked


def _pr_block(runs: tuple, relevant_by_need: dict, *, arm: str) -> dict:
    """Precision/recall/MRR agregados de un brazo (`arm` ∈ ARMS) contra un
    conjunto de relevancia (cluster o estricto)."""
    p5, p10, r10, r30, mrrs = [], [], [], [], []
    for run in runs:
        relevant = relevant_by_need.get(run.need_id, set())
        ranked = _ranked_for_arm(run, arm)
        p5.append(metrics.precision_at_k(ranked, relevant, TOP_K_PRIMARY))
        p10.append(metrics.precision_at_k(ranked, relevant, TOP_K_SECONDARY))
        r10.append(metrics.recall_at_k(ranked, relevant, TOP_K_SECONDARY))
        r30.append(metrics.recall_at_k(ranked, relevant, TOP_K_RECALL_WIDE))
        mrrs.append(metrics.mrr(ranked, relevant))
    return {
        "p5": metrics.mean(p5), "p10": metrics.mean(p10),
        "r10": metrics.mean(r10), "r30": metrics.mean(r30),
        "mrr": metrics.mean(mrrs),
    }


def _recall_ceiling(relevant_by_need: dict, k: int) -> float:
    """Techo teórico de R@k dado el tamaño real de cada cluster de relevancia
    — se reporta junto al número, nunca se esconde (SPEC.md §13)."""
    ceilings = [min(1.0, k / len(relevant)) for relevant in relevant_by_need.values() if relevant]
    return metrics.mean(ceilings)


def _ordered_connections_for_arm(run: NeedRun, arm: str, k: int) -> list:
    """Conexiones (con `feature_vector`) en el orden de `arm`, top-k. El brazo
    `dense` puede pedir entity_id que el pipeline real nunca puntuó -- esas
    posiciones quedan `None` (unscored), nunca se fabrica un ScoredResult."""
    if arm == "full":
        return list(run.full_connections[:k])
    if arm == "cosine":
        return list(_cosine_order(run.full_connections)[:k])
    by_id = {c.entity.entity_id: c for c in run.full_connections}
    return [by_id.get(entity_id) for entity_id in run.dense_ranked[:k]]


def _construct_validity(runs: tuple, *, arm: str, k: int = TOP_K_PRIMARY) -> dict:
    """Tasas de composición del top-k: trampa / capacidad / método / accionable
    -- medidas SÓLO sobre candidatos que el pipeline real llegó a puntuar
    (nunca se recalculan features fuera de él). `unscored_rate` reporta, por
    separado, qué fracción del top-k de este brazo el pipeline real ni
    siquiera consideró -- para `full`/`cosine` es siempre 0.0 (comparten pool
    con `full` por construcción); para `dense` es la evidencia de que el
    buscador de "similarity" puro trae candidatos que el reranker real
    descartaría de entrada."""
    trap, capability, method, actionable, scored, total = 0, 0, 0, 0, 0, 0
    for run in runs:
        for connection in _ordered_connections_for_arm(run, arm, k):
            total += 1
            if connection is None:
                continue
            scored += 1
            fv = connection.scored.feature_vector
            if connection.scored.relation_type == TRAP_RELATION_TYPE:
                trap += 1
            if fv.soporte_capacidad >= 1.0:
                capability += 1
            if (fv.compat_metodo or 0.0) >= 0.6:
                method += 1
            if connection.scored.relation_type in ACTIONABLE_RELATION_TYPES:
                actionable += 1
    if total == 0:
        return {"trap_rate": 0.0, "capability_rate": 0.0, "method_rate": 0.0,
                "actionable_rate": 0.0, "unscored_rate": 0.0}
    denom = scored or 1
    return {
        "trap_rate": trap / denom, "capability_rate": capability / denom,
        "method_rate": method / denom, "actionable_rate": actionable / denom,
        "unscored_rate": (total - scored) / total,
    }


def _evidence_coverage(runs: tuple, k: int = TOP_K_SECONDARY) -> float:
    covered, total = 0, 0
    for run in runs:
        for connection in run.full_connections[:k]:
            total += 1
            if connection.evidence_text.strip():
                covered += 1
    return covered / total if total else 0.0


def run_all(*, repo, dense_index, lexical_index, graph, rows: tuple = None) -> dict:
    rows = rows if rows is not None else qrels.load_rows()
    errors = qrels.validation_errors(repo, rows)
    if errors:
        raise ValueError("qrels.csv no pasa su propia validación:\n" + "\n".join(errors))

    need_ids = qrels.needs_covered(rows)
    relevant_cluster = qrels.build_relevant_sets(repo, rows, strict=False)
    relevant_strict = qrels.build_relevant_sets(repo, rows, strict=True)

    runs = tuple(
        run_need(need_id, repo=repo, dense_index=dense_index, lexical_index=lexical_index, graph=graph)
        for need_id in need_ids
    )

    precision_recall = {
        "cluster": {arm: _pr_block(runs, relevant_cluster, arm=arm) for arm in ARMS},
        "strict": {arm: _pr_block(runs, relevant_strict, arm=arm) for arm in ARMS},
    }
    recall_ceilings = {
        "cluster": {"r10_ceiling": _recall_ceiling(relevant_cluster, TOP_K_SECONDARY),
                    "r30_ceiling": _recall_ceiling(relevant_cluster, TOP_K_RECALL_WIDE)},
        "strict": {"r10_ceiling": _recall_ceiling(relevant_strict, TOP_K_SECONDARY),
                   "r30_ceiling": _recall_ceiling(relevant_strict, TOP_K_RECALL_WIDE)},
    }
    construct_validity = {arm: _construct_validity(runs, arm=arm) for arm in ARMS}

    return {
        "needs_evaluated": len(need_ids),
        "avg_latency_ms": metrics.mean([r.latency_s for r in runs]) * 1000,
        "avg_dense_latency_ms": metrics.mean([r.dense_latency_s for r in runs]) * 1000,
        "evidence_coverage": _evidence_coverage(runs),
        "precision_recall": precision_recall,
        "recall_ceilings": recall_ceilings,
        "construct_validity": construct_validity,
        "per_need": [
            {
                "need_id": r.need_id,
                "relevant_cluster": len(relevant_cluster.get(r.need_id, ())),
                "relevant_strict": len(relevant_strict.get(r.need_id, ())),
                "p5_full": metrics.precision_at_k(r.full_ranked, relevant_cluster.get(r.need_id, set()), TOP_K_PRIMARY),
                "p5_cosine": metrics.precision_at_k(r.cosine_ranked, relevant_cluster.get(r.need_id, set()), TOP_K_PRIMARY),
                "p5_dense": metrics.precision_at_k(r.dense_ranked, relevant_cluster.get(r.need_id, set()), TOP_K_PRIMARY),
                "latency_ms": r.latency_s * 1000,
            }
            for r in runs
        ],
    }
