"""CLI de evaluacion (Sprint-07): corre `evaluation/harness.run_all` sobre el
pipeline real y serializa `evaluation/results.json`, que consume
`interface/metrics_report.py` (ruta `/api/metrics` y pantalla `/metrics`).

Uso (desde knexus/):
    python scripts/evaluate.py                     # modelo real, resultado commiteable
    python scripts/evaluate.py --fast               # HashingProvider, smoke test offline
    python scripts/evaluate.py --out otro.json       # ruta de salida alternativa

Reusa `interface/composition.build_pipeline` (Regla A2: este script es el
UNICO lugar que arma el pipeline para evaluacion -- `harness.py` nunca
instancia adapters).

Salida ASCII plano (sin unicode decorativo): la salida de este CLI se
redirige a archivo en demos sobre Windows, donde el stream por defecto es
cp1252 y caracteres como flechas revientan con UnicodeEncodeError
(MEMORY.md leccion L8).
"""
import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evaluation import harness, qrels  # noqa: E402
from src.interface.composition import build_pipeline  # noqa: E402

DEFAULT_OUT = Path(__file__).resolve().parents[1] / "evaluation" / "results.json"


def main():
    parser = argparse.ArgumentParser(description="Evaluacion de desempeno de KNexus Engine (Sprint-07)")
    parser.add_argument("--fast", action="store_true", help="usar HashingProvider (offline, sin modelo real)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help=f"ruta de salida (default {DEFAULT_OUT})")
    args = parser.parse_args()

    repo, dense, lexical, graph = build_pipeline(args.fast, log=lambda msg: print(msg, file=sys.stderr))

    rows = qrels.load_rows()
    print(f"\n=== Evaluando {len(qrels.needs_covered(rows))} NEEDs sobre {len(rows)} filas de qrels.csv ===")
    t0 = time.time()
    report = harness.run_all(repo=repo, dense_index=dense, lexical_index=lexical, graph=graph, rows=rows)
    elapsed = time.time() - t0

    report["meta"] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "provider": dense._provider.name,
        "fast": args.fast,
        "entities_indexed": len(repo.all()),
        "qrels_rows": len(rows),
        "needs_evaluated": report["needs_evaluated"],
        "top_k_primary": harness.TOP_K_PRIMARY,
        "top_k_secondary": harness.TOP_K_SECONDARY,
        "top_k_recall_wide": harness.TOP_K_RECALL_WIDE,
        "elapsed_s": elapsed,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=True)

    _print_summary(report, elapsed, args.out)


def _print_summary(report: dict, elapsed: float, out_path: Path) -> None:
    print(f"\n[{elapsed:.1f}s] Escrito en {out_path}\n")
    print(f"Entities/latency: avg_latency_ms={report['avg_latency_ms']:.1f}  "
          f"avg_dense_latency_ms={report['avg_dense_latency_ms']:.1f}  "
          f"evidence_coverage={report['evidence_coverage']:.2%}\n")

    print("Precision/Recall (cluster relevance set):")
    print(f"{'arm':<8} {'P@5':>6} {'P@10':>6} {'R@10':>6} {'R@30':>6} {'MRR':>6}")
    for arm in harness.ARMS:
        block = report["precision_recall"]["cluster"][arm]
        print(f"{arm:<8} {block['p5']:>6.3f} {block['p10']:>6.3f} {block['r10']:>6.3f} "
              f"{block['r30']:>6.3f} {block['mrr']:>6.3f}")
    ceilings = report["recall_ceilings"]["cluster"]
    print(f"(techos: R@10<={ceilings['r10_ceiling']:.3f}  R@30<={ceilings['r30_ceiling']:.3f})\n")

    delta_full_cosine = (report["precision_recall"]["cluster"]["full"]["p5"]
                          - report["precision_recall"]["cluster"]["cosine"]["p5"])
    delta_full_dense = (report["precision_recall"]["cluster"]["full"]["p5"]
                         - report["precision_recall"]["cluster"]["dense"]["p5"])
    print(f"Ablation P@5 delta: full-cosine={delta_full_cosine:+.3f}  full-dense={delta_full_dense:+.3f}\n")

    print("Construct validity (top-5, tasas sobre candidatos puntuados por el pipeline real):")
    print(f"{'arm':<8} {'trap':>6} {'capab':>6} {'method':>7} {'action':>7} {'unscored':>9}")
    for arm in harness.ARMS:
        block = report["construct_validity"][arm]
        print(f"{arm:<8} {block['trap_rate']:>6.2f} {block['capability_rate']:>6.2f} "
              f"{block['method_rate']:>7.2f} {block['actionable_rate']:>7.2f} {block['unscored_rate']:>9.2f}")
    print()


if __name__ == "__main__":
    main()
