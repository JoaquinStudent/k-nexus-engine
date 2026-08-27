"""Demo manual de Sprint-04 — el ensayo del pitch.

Ejecutar desde `knexus/`:
    python scripts/demo_sprint04.py

Construye el pipeline completo con el modelo real (sentence-transformers),
mide arranque en frío vs caché caliente, consulta NEED-001, imprime el
comparador "¿por qué A antes que B?" y demuestra el cruce ES↔EN.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.adapters.embeddings.sentence_transformer_provider import SentenceTransformerProvider
from src.adapters.graph.networkx_store import NetworkXGraphStore
from src.adapters.repository.dataset_repository import DatasetEntityRepository
from src.adapters.retrieval.bm25_index import BM25Index
from src.adapters.retrieval.corpus import build_corpus
from src.adapters.retrieval.dense_index import DenseIndex
from src.application.auditar_resultado import comparar
from src.application.descubrir_conexiones import descubrir_conexiones


def _print_result(r):
    fv = r.scored.feature_vector
    print(f"  #{r.rank:>2} {r.entity.entity_id:<10} score={r.scored.score:.3f}  "
          f"{r.scored.relation_type}")
    print(f"       evidencia: {r.evidence.source_file} · {r.evidence.field_name}")
    print(f"       top features: " + ", ".join(
        f"{name}={value:.2f}(+{contrib:.2f})" for name, value, contrib in r.top_features
    ))


def main():
    print("=== Sprint-04 demo: recuperación híbrida + reranking explicable ===\n")

    t0 = time.time()
    repo = DatasetEntityRepository()
    print(f"[1] Repositorio cargado en {time.time() - t0:.2f}s "
          f"({len(repo.all())} entidades)")

    t0 = time.time()
    refs, texts = build_corpus(repo)
    print(f"[2] Corpus aplanado en {time.time() - t0:.2f}s ({len(texts)} textos)")

    t0 = time.time()
    dense = DenseIndex(SentenceTransformerProvider())
    dense.build(refs, texts)
    t_cold = time.time() - t0
    print(f"[3] Índice denso (arranque en frío / caché miss): {t_cold:.2f}s")

    t0 = time.time()
    dense2 = DenseIndex(SentenceTransformerProvider())
    dense2.build(refs, texts)
    t_warm = time.time() - t0
    print(f"[4] Índice denso (segunda vez / caché hit): {t_warm:.2f}s "
          f"({t_cold / max(t_warm, 0.001):.0f}x más rápido)")

    lexical = BM25Index()
    lexical.build(refs, texts)
    graph = NetworkXGraphStore(repo)

    print("\n=== Consulta: NEED-001 (Predicción y prevención de deserción estudiantil) ===")
    t0 = time.time()
    results = descubrir_conexiones("NEED-001", repo=repo, dense_index=dense, lexical_index=lexical, graph=graph)
    latency = time.time() - t0
    print(f"[latencia de la consulta: {latency:.3f}s — {len(results)} resultados]\n")
    for r in results[:5]:
        _print_result(r)
        print()

    print("=== ¿Por qué A antes que B? — PRJ-004 vs PRJ-002 ===")
    by_id = {r.entity.entity_id: r for r in results}
    if "PRJ-004" in by_id and "PRJ-002" in by_id:
        comparison = comparar(by_id["PRJ-004"], by_id["PRJ-002"])
        print(f"  score PRJ-004={by_id['PRJ-004'].scored.score:.3f} vs "
              f"PRJ-002={by_id['PRJ-002'].scored.score:.3f} "
              f"(delta={comparison.score_delta:+.3f})")
        print(f"  feature dominante: {comparison.dominant_feature}")
        for f in comparison.features[:3]:
            print(f"    {f.name}: A={f.value_a} B={f.value_b} "
                  f"delta={f.delta:+.3f} favorece={f.favors}")
    else:
        print("  (PRJ-004 o PRJ-002 no llegaron al top-N de esta corrida)")

    print("\n=== Cruce ES <-> EN ===")
    for query_text in ("predicción y prevención de deserción estudiantil", "student attrition prediction"):
        t0 = time.time()
        r = descubrir_conexiones(query_text, repo=repo, dense_index=dense, lexical_index=lexical, graph=graph)
        latency = time.time() - t0
        top3 = [x.entity.entity_id for x in r[:3]]
        print(f"  '{query_text}' ({latency:.3f}s) -> top-3: {top3}")

    print("\n=== Robustez: las 42 necesidades responden sin reventar ===")
    t0 = time.time()
    empty = 0
    for need in repo.by_type("NEED"):
        r = descubrir_conexiones(need.entity_id, repo=repo, dense_index=dense, lexical_index=lexical, graph=graph)
        if not r:
            empty += 1
    total_latency = time.time() - t0
    print(f"  42 consultas en {total_latency:.2f}s "
          f"(avg {total_latency / 42 * 1000:.0f}ms/consulta) · {empty} sin resultados")


if __name__ == "__main__":
    main()
