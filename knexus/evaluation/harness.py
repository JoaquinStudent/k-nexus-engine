"""Arnés de evaluación (Sprint-07): corre los dos brazos del ablation sobre
el set etiquetado (`qrels.csv`) y arma el dict que se serializa a
`results.json` (lo consume `/api/metrics`).

Regla A2 (extendida a `evaluation/`, aunque no es parte del hexágono de
`src/`): este módulo NO instancia adapters — los recibe ya construidos desde
`scripts/evaluate.py` (que reusa `interface/composition.build_pipeline`,
igual que el CLI y la app).

**El ablation aísla el RERANKER, no el recuperador.** Los dos brazos comparten
la MISMA llamada a `descubrir_conexiones` (misma recuperación híbrida,
mismos candidatos) — el brazo "coseno" es la lista RE-ORDENADA por
`feature_vector.sim_semantica`. Esto es deliberado: compara la decisión de
orden, no dos sistemas de recuperación distintos, y hace que los sesgos de
la etiqueta (declarados en SPEC.md §13) se cancelen en el delta entre brazos.
"""
import time
from dataclasses import dataclass

from evaluation import metrics, qrels
from src.application.descubrir_conexiones import descubrir_conexiones

TOP_K_PRIMARY = 5
TOP_K_SECONDARY = 10
TOP_K_RECALL_WIDE = 30

# "Accionable" = tipos de relación con valor de decisión directo (método
# transferible confirmado o capacidad institucional disponible) — subconjunto
# deliberadamente más estricto que "no es la trampa" (ver relation_type.py).
ACTIONABLE_RELATION_TYPES = ("antecedente_metodologico", "activacion_capacidad")
TRAP_RELATION_TYPE = "coincidencia_superficial"


@dataclass(frozen=True)
class NeedRun:
    need_id: str
    latency_s: float
    full_ranked: tuple       # entity_id ordenados por compute_score (el pipeline real)
    cosine_ranked: tuple     # mismos candidatos, re-ordenados por sim_semantica
    full_connections: tuple  # RankedConnection en orden "full" -- insumo de construct-validity


def _cosine_order(connections: tuple) -> tuple:
    return tuple(sorted(connections, key=lambda c: -c.scored.feature_vector.sim_semantica))


def run_need(need_id: str, *, repo, dense_index, lexical_index, graph) -> NeedRun:
    t0 = time.perf_counter()
    connections = descubrir_conexiones(
        need_id, repo=repo, dense_index=dense_index, lexical_index=lexical_index, graph=graph,
    )
    latency = time.perf_counter() - t0
    return NeedRun(
        need_id=need_id,
        latency_s=latency,
        full_ranked=tuple(c.entity.entity_id for c in connections),
        cosine_ranked=tuple(c.entity.entity_id for c in _cosine_order(connections)),
        full_connections=connections,
    )


def _pr_block(runs: tuple, relevant_by_need: dict, *, arm: str) -> dict:
    """Precision/recall/MRR agregados de un brazo (`arm` = "full"/"cosine")
    contra un conjunto de relevancia (cluster o estricto)."""
    p5, p10, r10, r30, mrrs = [], [], [], [], []
    for run in runs:
        relevant = relevant_by_need.get(run.need_id, set())
        ranked = run.full_ranked if arm == "full" else run.cosine_ranked
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


def _construct_validity(runs: tuple, *, arm: str, k: int = TOP_K_PRIMARY) -> dict:
    """Tasas de composición del top-k: trampa / capacidad / método / accionable.
    Mide sobre las MISMAS conexiones ya calificadas — nunca recalcula features."""
    trap, capability, method, actionable, total = 0, 0, 0, 0, 0
    for run in runs:
        ordered = run.full_connections if arm == "full" else _cosine_order(run.full_connections)
        for connection in ordered[:k]:
            total += 1
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
        return {"trap_rate": 0.0, "capability_rate": 0.0, "method_rate": 0.0, "actionable_rate": 0.0}
    return {
        "trap_rate": trap / total, "capability_rate": capability / total,
        "method_rate": method / total, "actionable_rate": actionable / total,
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
        "cluster": {
            "full": _pr_block(runs, relevant_cluster, arm="full"),
            "cosine": _pr_block(runs, relevant_cluster, arm="cosine"),
        },
        "strict": {
            "full": _pr_block(runs, relevant_strict, arm="full"),
            "cosine": _pr_block(runs, relevant_strict, arm="cosine"),
        },
    }
    recall_ceilings = {
        "cluster": {"r10_ceiling": _recall_ceiling(relevant_cluster, TOP_K_SECONDARY),
                    "r30_ceiling": _recall_ceiling(relevant_cluster, TOP_K_RECALL_WIDE)},
        "strict": {"r10_ceiling": _recall_ceiling(relevant_strict, TOP_K_SECONDARY),
                   "r30_ceiling": _recall_ceiling(relevant_strict, TOP_K_RECALL_WIDE)},
    }
    construct_validity = {
        "full": _construct_validity(runs, arm="full"),
        "cosine": _construct_validity(runs, arm="cosine"),
    }

    return {
        "needs_evaluated": len(need_ids),
        "avg_latency_ms": metrics.mean([r.latency_s for r in runs]) * 1000,
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
                "latency_ms": r.latency_s * 1000,
            }
            for r in runs
        ],
    }
