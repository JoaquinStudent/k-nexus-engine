"""CLI para probar el pipeline manualmente con cualquier consulta.

Uso (desde knexus/):
    python scripts/query_cli.py "NEED-001"
    python scripts/query_cli.py "predicción y prevención de deserción estudiantil"
    python scripts/query_cli.py "student attrition prediction" --top 10
    python scripts/query_cli.py "PRJ-004" --compare PRJ-002
    python scripts/query_cli.py "NEED-001" --fast   # HashingProvider, sin descargar el modelo
    python scripts/query_cli.py "NEED-001" --opportunity   # cadena de oportunidad ensamblada

Construye el pipeline una vez (con caché de vectores) y responde la consulta.
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.application.auditar_resultado import comparar
from src.application.descubrir_conexiones import descubrir_conexiones
from src.application.generar_oportunidad import generar_oportunidad
from src.adapters.explain.factory import build_explainer
from src.interface.composition import build_pipeline


def main():
    parser = argparse.ArgumentParser(description="Prueba manual del pipeline de KNexus Engine")
    parser.add_argument("query", help="NEED-XXX, PRJ-XXX, THS-XXX... o texto libre (ES o EN)")
    parser.add_argument("--top", type=int, default=5, help="cuántos resultados mostrar (default 5)")
    parser.add_argument("--compare", metavar="ENTITY_ID", help="comparar el #1 contra este entity_id")
    parser.add_argument("--fast", action="store_true", help="usar HashingProvider (offline, sin modelo real)")
    parser.add_argument("--opportunity", action="store_true", help="ensamblar y mostrar la cadena de oportunidad")
    args = parser.parse_args()

    repo, dense, lexical, graph = build_pipeline(args.fast, log=lambda msg: print(msg, file=sys.stderr))

    print(f"\n=== Consulta: {args.query!r} ===")
    t0 = time.time()
    results = descubrir_conexiones(args.query, repo=repo, dense_index=dense, lexical_index=lexical, graph=graph)
    latency = time.time() - t0
    print(f"[{len(results)} resultados en {latency:.3f}s]\n")

    for r in results[: args.top]:
        fv = r.scored.feature_vector
        print(f"#{r.rank:<3} {r.entity.entity_id:<10} score={r.scored.score:.3f}  {r.scored.relation_type}")
        print(f"      evidencia: {r.evidence.source_file} · {r.evidence.field_name}")
        print(f"      \"{r.evidence_text[:100]}{'...' if len(r.evidence_text) > 100 else ''}\"")
        print("      features: " + ", ".join(
            f"{name}={value:.2f}" for name, value, _ in r.top_features
        ))
        print()

    if args.compare:
        by_id = {r.entity.entity_id: r for r in results}
        if args.compare not in by_id or not results:
            print(f"'{args.compare}' no está en los resultados de esta consulta.")
            return
        top = results[0]
        other = by_id[args.compare]
        comparison = comparar(top, other)
        print(f"=== ¿Por qué {top.entity.entity_id} antes que {other.entity.entity_id}? ===")
        print(f"delta de score: {comparison.score_delta:+.3f} · feature dominante: {comparison.dominant_feature}")
        for f in comparison.features:
            print(f"  {f.name:<20} A={f.value_a}  B={f.value_b}  delta={f.delta:+.3f}  favorece={f.favors}")

    if args.opportunity:
        print("\n=== Cadena(s) de oportunidad ===")
        explainer = build_explainer()
        opportunities = generar_oportunidad(args.query, repo=repo, dense_index=dense, lexical_index=lexical, graph=graph)
        if not opportunities:
            print("  (no se pudo ensamblar ninguna oportunidad para esta consulta)")
        for o in opportunities:
            chain = " -> ".join(f"{l.role}:{l.entity_id}[{l.link_type}]" for l in o.links)
            print(f"\n  tipo={o.opportunity_type}  prioridad={o.priority}  score={o.score:.3f}")
            print(f"  cadena: {chain}")
            print(f"  explicación: {explainer.explain_opportunity(o)}")


if __name__ == "__main__":
    main()
