# ARCHITECTURE.md — KNexus Engine

> **Estilo arquitectónico:** Pipeline (Pipes & Filters) gobernado por **Arquitectura Limpia / Hexagonal (Ports & Adapters)** con **núcleo de dominio puro**.
> **Principio rector:** las dependencias apuntan **siempre hacia adentro**. El `domain` no conoce a nadie.

---

## 1. Por qué esta arquitectura

| Necesidad del reto | Respuesta arquitectónica |
|---|---|
| El sistema es un flujo por etapas (fuentes → … → oportunidad). | **Pipeline / Pipes & Filters** como macro-forma. |
| El scoring debe ser auditable y testeable sin red. | **Dominio puro** aislado, testeable con datos falsos. |
| El LLM y la UI deben ser desechables (degradar si fallan). | **Ports & Adapters**: lo volátil se enchufa/desenchufa. |
| Trazabilidad campo-por-campo. | **Provenance** capturada en el adapter de repositorio, en la ingesta. |

---

## 2. Diagrama de capas (concéntrico)

```
        ┌───────────────────────────────────────────────┐
        │                 INTERFACE                     │  FastAPI + Jinja2 (un proceso) · mini-grafo SVG
        │   ┌───────────────────────────────────────┐   │
        │   │              ADAPTERS                  │   │  bge-m3 · FAISS · bm25 · NetworkX
        │   │   ┌───────────────────────────────┐   │   │  LlmExplainer / TemplateExplainer
        │   │   │        APPLICATION            │   │   │  use-cases (orquestan el pipeline)
        │   │   │   ┌───────────────────────┐   │   │   │
        │   │   │   │       PORTS           │   │   │   │  interfaces abstractas
        │   │   │   │   ┌───────────────┐   │   │   │   │
        │   │   │   │   │    DOMAIN     │   │   │   │   │  features · scoring · tipado
        │   │   │   │   │   (PURO)      │   │   │   │   │  reglas de oportunidad
        │   │   │   │   └───────────────┘   │   │   │   │
        │   │   │   └───────────────────────┘   │   │   │
        │   │   └───────────────────────────────┘   │   │
        │   └───────────────────────────────────────┘   │
        └───────────────────────────────────────────────┘

     Dirección de dependencias:  INTERFACE → ADAPTERS → APPLICATION → PORTS → DOMAIN
     El DOMAIN no importa hacia afuera. NUNCA.
```

## 3. El pipeline de datos (Pipes & Filters)

```
[FUENTES Data V1.0]
   CSV + 60 MD (01_institution · 02_people_curriculum · 03_knowledge_needs)
        │
        ▼
[F1] INGESTA + PROVENANCE      ── adapter/repository ──► EntityRepository (port)
        │   cada texto → {texto, entity_id, entity_type, archivo, campo}
        ▼
[F2] REPRESENTACIÓN
        │   denso (bge-m3→FAISS) · léxico (bm25) · grafo (NetworkX desde tablas de relación)
        ▼
[F3] RECUPERACIÓN HÍBRIDA      ◄── query: necesidad / entidad / texto libre
        │   fusión RRF(denso, léxico) → candidatos top-N
        ▼
[F4] RERANKING EXPLICABLE  ★   ── DOMAIN puro ──
        │   7 features auditables → score ponderado → tipo de relación
        ▼
[F5] ENSAMBLADO DE OPORTUNIDAD ── DOMAIN + GraphStore ──
        │   necesidad → antecedente → investigador → capacidad → currículo
        ▼
[F6] EXPLICACIÓN + TRAZABILIDAD── Explainer (port) ──
        │   LlmExplainer  ó  TemplateExplainer (degradación)
        ▼
[F7] INTERFAZ                  ── FastAPI + Jinja2 (Sprint-06, ADR-013) ──
        score desglosado · evidencia · procedencia · mini-grafo · oportunidad
```

## 4. Estructura de carpetas

```
knexus/
├── src/
│   ├── domain/            # PURO — sin libs externas
│   │   ├── features.py        # cálculo de las 7 features
│   │   ├── scoring.py         # combinación ponderada → relevancia
│   │   ├── relation_type.py   # tipado de la conexión
│   │   └── opportunity.py     # reglas de ensamblado de oportunidad
│   ├── application/       # use-cases (orquestan el pipeline)
│   │   ├── descubrir_conexiones.py
│   │   ├── generar_oportunidad.py
│   │   └── auditar_resultado.py
│   ├── ports/            # interfaces abstractas
│   │   ├── embedding_provider.py
│   │   ├── lexical_index.py
│   │   ├── graph_store.py
│   │   ├── explainer.py
│   │   └── entity_repository.py
│   ├── adapters/
│   │   ├── embeddings/       # bge-m3
│   │   ├── retrieval/        # faiss, bm25, fusión RRF
│   │   ├── graph/            # networkx
│   │   ├── explain/          # llm_explainer.py + template_explainer.py
│   │   └── repository/       # loaders CSV/MD + provenance
│   └── interface/          # Sprint-06 (ADR-013): FastAPI + Jinja2, un proceso
│       ├── composition.py     # composition root: arma el pipeline UNA vez + caché de consulta
│       ├── presenters.py      # DTO -> dict de presentación (PURO); mini-grafo SVG; serialize_metrics (Sprint-07)
│       ├── metrics_report.py  # Sprint-07: LEE evaluation/results.json (no lo importa como paquete)
│       ├── app.py             # monta static/templates, ambos routers, lifespan
│       ├── api/                # rutas JSON: /api/discover, /api/connection, /api/opportunity, /api/audit, /api/metrics
│       ├── ui/                  # rutas HTML: /, /results, /connection/{id}, /opportunity, /audit, /metrics
│       ├── templates/          # Jinja — base + 6 pantallas + 3 parciales
│       └── static/               # knexus.css (tokens de DESIGN.md) + fonts/ vendorizadas
├── evaluation/             # Sprint-07: evidencia de desempeño (FUERA del hexágono de src/)
│   ├── metrics.py             # P@K, R@K, MRR — funciones puras
│   ├── qrels.py                # carga/valida el set etiquetado contra el repositorio real
│   ├── qrels.csv                # set etiquetado: cluster de application_context por NEED
│   └── harness.py                # orquesta los 3 brazos del ablation (full/cosine/dense) -> dict
├── scripts/
│   ├── query_cli.py         # CLI manual de consulta (reusa interface/composition.build_pipeline)
│   └── evaluate.py           # Sprint-07: corre harness.run_all -> evaluation/results.json
├── database/
│   └── schema.sql
├── tests/                # espejo de domain/, application/, interface/ y evaluation/
└── .sprints/
```

## 5. Puertos (contratos)

| Puerto | Responsabilidad | Adapter(s) |
|---|---|---|
| `EntityRepository` | Cargar entidades con provenance. | loaders CSV/MD |
| `EmbeddingProvider` | Texto → vector. | bge-m3 |
| `LexicalIndex` | Búsqueda por términos. | rank-bm25 |
| `GraphStore` | Relaciones explícitas y caminos. | NetworkX |
| `Explainer` | Redactar explicación y oportunidad. | `LlmExplainer` **/** `TemplateExplainer` |

## 6. Reglas de arquitectura (verificables en Review)

| # | Regla | Cómo se verifica |
|---|---|---|
| A1 | `domain/` no importa `adapters/`, `ports/`, `application/`, ni librerías externas. | Test de arquitectura (grep de imports). |
| A2 | Los use-cases dependen de puertos, no de adapters concretos. | Inyección de dependencias en el arranque. Desde Sprint-06, `interface/composition.py` es el ÚNICO módulo autorizado a instanciar adapters concretos (`DatasetEntityRepository`, `DenseIndex`, `BM25Index`, `NetworkXGraphStore`); las rutas los reciben ya construidos vía `Depends(get_query_service)`. |
| A3 | Todo resultado conserva su provenance hasta la UI. | Test de trazabilidad end-to-end. Desde Sprint-06 esto se verifica también a nivel HTML renderizado (`tests/interface/test_trazabilidad_ui.py`), no sólo a nivel de datos. |
| A4 | Existe al menos un adapter de degradación por cada dependencia externa. | `TemplateExplainer` presente y probado. |

**Nota (Sprint-07):** `evaluation/` no pertenece al hexágono de `src/` — es un paquete de medición dev-only con su propio arranque (`scripts/evaluate.py`, que reusa `interface/composition.build_pipeline`, Regla A2) que tarda varios minutos con el modelo real, incompatible con un request HTTP. `interface/metrics_report.py` NO importa `evaluation/`: sólo LEE el archivo de datos (`evaluation/results.json`) que ese paquete produce. Así el runtime de la app queda desacoplado del paquete de medición — `evaluation/` puede evolucionar (o faltar) sin afectar los imports de `interface/`.

## 7. Flujo de una consulta (secuencia)

| Orden | Capa | Acción |
|---|---|---|
| 1 | Interface | Recibe la query (necesidad/entidad/texto). |
| 2 | Application | `DescubrirConexiones` orquesta el pipeline. |
| 3 | Adapters | Recuperación híbrida → candidatos. |
| 4 | Domain | Features + score + tipo (auditable). |
| 5 | Domain + GraphStore | Ensamblado de oportunidad. |
| 6 | Explainer | Redacción (LLM o plantilla). |
| 7 | Interface | Devuelve las 7 respuestas + oportunidad. |
