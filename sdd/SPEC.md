# SPEC.md — Sprint-01 (con amendments de Sprint-01.5, 03 y 04)

> **Épica:** Núcleo de Dominio — features + scoring + tipado
> **Estado:** ✅ Implementado y en producción (Sprint-04 lo orquesta de punta a punta)
> **Capa:** `domain/` (PURO, sin imports externos — Regla A1)

---

## 1. Objetivo del Sprint

Construir el corazón auditable del sistema: dado un par **(consulta, candidato)** ya recuperado, calcular un **vector de 7 features**, combinarlas en un **score de relevancia** y clasificar el **tipo de relación** — todo con funciones puras y testeables sin red ni datos reales.

Este Sprint materializa la tesis del reto: **similarity ≠ relevance**.

## 2. Alcance

| Incluye | NO incluye |
|---|---|
| `features.py`, `scoring.py`, `relation_type.py` | Ingesta de datos (Sprint-02) |
| Tests unitarios Rojo→Verde | Embeddings / índices reales (Sprint-03) |
| Test de arquitectura A1 (dominio puro) | UI / API (Sprint-06) |

## 3. Contrato de datos (entrada al dominio)

El dominio recibe estructuras ya normalizadas (dicts/dataclasses), NO archivos. Ejemplo de par de entrada:

```
CandidatePair:
  query:      { entity_type, text, keywords[], domains[], methods[] }
  candidate:  { entity_id, entity_type, text, keywords[], domains[],
                methods[], filled_fields[], has_capability_support: bool,
                graph_linked: bool }
  sim_semantic: float   # provisto por la capa de recuperación (0..1)
```

## 4. Las 7 features (contrato de cálculo)

| Feature | Rango | Regla de cálculo (determinista) |
|---|---|---|
| `sim_semantica` | 0..1 | Pasa a través desde recuperación (coseno normalizado). |
| `sim_lexica` | 0..1 | Jaccard entre keywords de query y candidato. |
| `compat_metodo` | 0..1 o **N/A** | Híbrido (ADR-007): (1) consulta con métodos → Jaccard; (2) consulta sin método pero con `problem_types` inferido → **transferabilidad** contra el método real del candidato (`method_compat.py`); (3) sin señal → **N/A** (excluida del score, re-normaliza). Los NEED caen en (2)/(3) porque no prescriben método. |
| `compat_dominio` | 0..1 o **N/A** | Solape de `domains`. Igual que `compat_metodo`, N/A (ADR-009, Sprint-03) si `query.domains` viene vacío — le pasa a TODO NEED (`institutional_needs.csv` no tiene ninguna columna de dominio). La ingesta infiere un **sector** institucional del texto del NEED (`vocabulary.py:NEED_SECTOR_PHRASES`) y lo cruza contra el sector del candidato. |
| `densidad_evidencia` | 0..1 | Proporción de `filled_fields` sobre campos esperados del tipo. |
| `soporte_capacidad` | 0..1 | 1.0 si `has_capability_support` else 0.0. |
| `enlace_estructural` | 0..1 | 1.0 si `graph_linked` else 0.0. |

## 5. Scoring (contrato)

```
score = Σ (peso_i · feature_i),  con Σ pesos = 1.0
```

| Peso | Feature | Racional |
|---|---|---|
| 0.20 | compat_metodo | Penaliza "mismo tema, método inaplicable". |
| 0.20 | compat_dominio | Dominio compatible pesa como método. |
| 0.18 | sim_semantica | Importa, pero no domina. |
| 0.15 | soporte_capacidad | Accionabilidad institucional. |
| 0.12 | densidad_evidencia | Registros ricos > registros vacíos. |
| 0.10 | enlace_estructural | Señal de grafo. |
| 0.05 | sim_lexica | La más débil: evita premiar la trampa léxica. |

> Los pesos son configurables y se justifican en el pitch. La suma DEBE ser 1.0 (test lo verifica).
>
> **Features N/A y re-normalización (ADR-007 / ADR-009).** Una feature puede ser N/A cuando no es medible para el par — `compat_metodo` (ADR-007, Sprint-01.5) y `compat_dominio` (ADR-009, Sprint-03), ambas ante consultas que no traen la señal correspondiente. En ese caso se **excluye** del sumatorio y los pesos restantes se **re-normalizan** a 1.0. Con las 7 features presentes el resultado es idéntico al cálculo directo. Esto evita el techo artificial de ~0.80 sin inventar datos ni alterar `WEIGHTS`.
>
> **`soporte_capacidad` y `enlace_estructural` (ADR-008, Sprint-03).** Antes de Sprint-03 estas dos features (peso combinado 0.25) eran `False` constante para todo candidato real — 2 de los 6 tipos de relación (`activacion_capacidad`, `investigador_complementario`) eran inalcanzables. `enlace_estructural` ahora es relacional (adyacencia real en el grafo NetworkX respecto a otros candidatos de la misma consulta, no "existe en el grafo" — eso sería casi-constante). `has_capability_support` cruza sector + tema de `capability_name` + madurez≥4 (`capability_match.py`) — el primer diseño, por `capability_type`, se descartó por dar `True` al 97.8% de los proyectos (esa columna resultó estar decorrelacionada del tema real de la capacidad).

## 6. Tipado de la relación (contrato)

| Tipo | Condición dominante |
|---|---|
| `antecedente_metodologico` | `compat_metodo` alto + evidencia densa. |
| `antecedente_relevante` | `compat_dominio` alto + `sim_semantica` alta. |
| `investigador_complementario` | `enlace_estructural` vía investigador. |
| `activacion_capacidad` | `soporte_capacidad` = 1.0 dominante. |
| `integracion_curricular` | candidato de tipo subject/competency. |
| `coincidencia_superficial` | solo `sim_lexica` / `sim_semantica` altas, resto bajo → **relevancia baja**. |

## 7. Criterios de Aceptación (DoD)

| # | Criterio | Verificación |
|---|---|---|
| DoD-1 | Cada feature retorna un float en [0,1] para entradas válidas — excepto `compat_metodo`/`compat_dominio`, que retornan `None` (N/A, ADR-007/ADR-009) cuando la consulta no aporta señal comparable; `scoring.py` los excluye y re-normaliza. | Test unitario por feature + `test_need_sin_senal_es_na_y_renormaliza`. |
| DoD-2 | `score` = combinación ponderada; pesos suman 1.0. | Test de invariante. |
| DoD-3 | Dos candidatos con misma `sim_semantica` pero distinto `compat_metodo` reciben score distinto. | **Test estrella "A vs B"**. |
| DoD-4 | Un candidato de solo-similitud-léxica se tipa `coincidencia_superficial`. | Test de tipado. |
| DoD-5 | `domain/` no importa librerías externas ni otras capas. | Test de arquitectura A1 (grep imports). |
| DoD-6 | Todos los tests pasan (Verde) y hubo commit previo en Rojo. | Log de ejecución. |

## 8. Plan TDD (Rojo → Verde)

| Orden | Test primero (Rojo) | Código después (Verde) |
|---|---|---|
| 1 | `test_features_rango` | `features.py` |
| 2 | `test_scoring_pesos_suman_uno` | `scoring.py` |
| 3 | `test_A_vs_B_metodo_desempata` | ajuste de `scoring.py` |
| 4 | `test_tipado_superficial` | `relation_type.py` |
| 5 | `test_arquitectura_dominio_puro` | (verificación eststructural) |

## 9. Caso de referencia para el test estrella (DoD-3)

Caso **ilustrativo** (fixture inyectado a mano, `test_A_vs_B_metodo_desempata`), no tomado literalmente del dataset — sirve para fijar el contrato del test antes de tener ingesta real:

| Candidato | sim_semantica | compat_metodo | compat_dominio | Resultado esperado |
|---|---|---|---|---|
| PRJ-004 (clasificación supervisada, permanencia↔attrition) | 0.88 | 0.90 | 0.95 | score alto · `antecedente_metodologico` |
| PRJ-007 (mismo tema, completado, menor soporte) | 0.88 | 0.60 | 0.80 | score medio |
| Tesis solo-tema, método distinto, campos vacíos | 0.85 | 0.20 | 0.50 | score bajo · `coincidencia_superficial` |

> Mismo `sim_semantica` ≈ 0.88 en los dos primeros, pero el método desempata. **Ese es el examen.**
>
> **Corrección (Sprint-02):** en el dataset real, PRJ-004 y PRJ-007 comparten el mismo método (`clasificación supervisada`) — no existe ningún proyecto con `encuesta`. La fila PRJ-007 de esta tabla es una construcción didáctica, no un candidato real. Ver §9.1 para el caso reproducido con datos reales.

### 9.1 Reproducción sobre datos reales (ADR-007 + Sprint-02, ingesta real)

El caso §9 hand-inyectaba métodos en el NEED (que los datos reales no tienen) y un "PRJ-007 con encuesta" que no existe en el dataset. El caso real, cargado por `DatasetEntityRepository` y proyectado con `to_query_entity`/`to_candidate_entity` (`src/adapters/repository/`), parte de **NEED-001 sin método**, con `problem_types=("prediccion",)` inferido de su texto ("predicción y prevención de deserción estudiantil"), contra dos proyectos reales y temáticamente afines (permanencia estudiantil / student attrition):

| Candidato | método real minado | `compat_metodo` (transferabilidad `prediccion→·`) | Resultado |
|---|---|---|---|
| PRJ-004 ("Estrategia basada en clasificación supervisada...") | `clasificacion_supervisada` | **0.90** | score **0.458** · `antecedente_metodologico` |
| PRJ-002 ("Modelo institucional para riesgo académico...") | `analitica_educativa` | **0.70** | score **0.418** · `antecedente_metodologico` |

> Verificado sobre las 2.512 entidades reales cargadas (`test_cierre_adr007_need001_desempata_sobre_datos_reales`, `knexus/tests/adapters/test_ingestion.py`). El método desempata **sin inventar método en el NEED** — se infiere el tipo de problema del texto y se puntúa el método real y documentado del candidato.

## 10. Contrato de salida del pipeline (Sprint-04)

`src/application/descubrir_conexiones.py` orquesta F3+F4 de `ARCHITECTURE.md`. Contrato de entrada/salida:

```
descubrir_conexiones(query_input: str, *, repo, dense_index, lexical_index, graph,
                      top_n=50, top_k_seeds=10, retrieval_k=200) -> tuple[RankedConnection, ...]

RankedConnection:
  rank: int
  scored: ScoredResult(entity_id, feature_vector, score, relation_type)   # domain/
  entity: StoredEntity                                                    # ports/
  evidence: Provenance          # campo que justificó la recuperación (o el mejor campo propio si entró por grafo)
  evidence_text: str
  top_features: tuple[(nombre, valor, contribución_normalizada), ...]     # datos, NO prosa (eso es Sprint-05)
```

**Invariante verificado por test:** `scored.score == compute_score(scored.feature_vector)` para **todo** resultado — el `rrf_score` de la fusión (RRF sobre denso+léxico) nunca entra al score final; sólo decide qué candidatos llegan a puntuarse.

**Pipeline en dos pasadas** (`graph_linked` es relacional, ADR-008): pasada 1 sin contexto de grafo → top-K se vuelven `seed_ids` → **expansión del pool con los vecinos de esos seeds** (hallazgo de Sprint-04: un investigador casi nunca comparte vocabulario con una necesidad, así que si sólo se puntúa lo que trajo la búsqueda textual, `graph_linked` queda correcto pero vacío en la práctica) → pasada 2 con grafo ya informado.

**Auto-exclusión:** si la consulta es una entidad del dataset, se excluye de sus propios resultados antes de fusionar (si no, aparecería como su propio mejor match).

**Texto libre:** `application/query_builder.py` infiere `problem_types`/`domains` del texto con el mismo mecanismo que un NEED (`src/domain/text_matching.py`, movido desde `adapters/` en Sprint-04 — Regla A2: es vocabulario puro, no una implementación swappeable). Nunca se le asigna método.

**Comparador "¿por qué A antes que B?"** (`application/auditar_resultado.py`, módulo M7 de `DESIGN.md`): `comparar(a, b)` descompone el delta de score en deltas por feature — la suma de los 7 deltas reproduce exacto `score_a - score_b` (mismo principio de aditividad que `compute_score`).

**Caché de vectores** (`adapters/retrieval/vector_cache.py`): clave = modelo + hash del corpus; evita recodificar ~14.000 textos (~40s) en cada arranque. Instanciar el modelo real (`SentenceTransformer(...)`) sigue costando su tiempo de carga (~5-15s) cada vez — la caché evita el *encoding*, no la carga del modelo en memoria.

## 11. Contrato de ensamblado de oportunidad + Explainer (Sprint-05)

`src/application/generar_oportunidad.py` orquesta F5+F6 de `ARCHITECTURE.md`, reutilizando `descubrir_conexiones` (Sprint-04) para los antecedentes — no rehace recuperación.

```
generar_oportunidad(query_input: str, *, repo, dense_index, lexical_index, graph,
                     top_antecedentes=3) -> tuple[Opportunity, ...]

ChainLink (domain/opportunity.py):
  role: necesidad | antecedente | investigador | capacidad | curriculo
  entity_id, entity_type
  link_type: retrieved | edge | inferred     # fuerza probatoria del eslabón
  score: float | None                         # None si es un hecho puro, sin score propio
  relation_type: str                          # sólo poblado en el antecedente
  rationale_features: tuple[(nombre, valor), ...]

Opportunity:
  need_id, links: tuple[ChainLink, ...]
  opportunity_type: continuidad_investigativa | activacion_capacidad |
                    integracion_curricular | colaboracion_interdisciplinaria | exploratoria
  priority: alta | media | baja
  score: float    # score del antecedente — el ancla de la oportunidad
```

**Por qué `link_type` es obligatorio, no cosmético.** Los 4 eslabones NO tienen la misma fuerza probatoria: antecedente = puntuado (`retrieved`); investigador = arista real de `researcher_project.csv` (`edge`); capacidad = inferida sin tabla de enlace (`inferred`, ADR-008); currículo = FK real (`primary_program_id`) pero el subject/competency específico se elige por score (`edge`, igual criterio que investigador — el "cómo se sabe que existe la conexión" es un hecho duro, aunque cuál instancia se muestre sea puntuado). Presentar los tres tipos como si fueran lo mismo es la "trazabilidad de mentira" que la rúbrica penaliza.

**Eslabón curricular puntuado, no traversado.** De los ~7 subjects/competencies del programa de un investigador, se puntúan TODOS con `to_candidate_entity`+`compute_features`+`compute_score` contra la misma consulta (mismas 7 features que el resto del sistema) y sólo entra el de mayor score si supera `CURRICULAR_SCORE_THRESHOLD=0.30`. Verificado con el modelo real: para NEED-001, "Analítica educativa" (SUB-083) puntúa por encima de "Lenguaje y conocimiento" (SUB-084) del mismo programa y sector.

**Degradación honesta.** Un eslabón sin evidencia real (antecedente sin investigador conectado, ninguna capacidad institucional coincidente, ningún componente curricular sobre el umbral) simplemente **no aparece** en la cadena — nunca se fabrica. `opportunity_priority` penaliza esto de forma natural: menos eslabones "edge" ⇒ prioridad más baja a igual score del antecedente.

**`Explainer` (ADR-002, `ports/explainer.py`):** `explain_connection`/`explain_opportunity` reciben sólo los DTO ya ensamblados (nunca el repositorio) y producen prosa. `TemplateExplainer` es el adapter por defecto (determinista, sin red); `LlmExplainer` es opcional (vía OpenRouter, API compatible con OpenAI chat completions, llamada con `httpx`) y **degrada automáticamente a `TemplateExplainer`** si no hay `OPENROUTER_API_KEY` en el entorno, o si la llamada falla por cualquier motivo (`adapters/explain/factory.py:build_explainer()`, Regla A4). Grounding verificado por test: ningún identificador ni cifra en la salida del `TemplateExplainer` puede faltar en su input.

## 12. Contrato de la interfaz (Sprint-06)

> **Estado:** ✅ Implementado. **Capa:** `interface/` (FastAPI + Jinja2, ADR-013 — reemplaza a Streamlit del `TECH_STACK.md` original). Un solo proceso: `/api/*` (JSON) y las páginas HTML consumen los MISMOS DTO de `interface/presenters.py`.

### 12.1 Composition root

`interface/composition.py` es el ÚNICO módulo autorizado a instanciar adapters concretos (Regla A2). Expone:

```
build_pipeline(fast: bool = False, *, log=...) -> (repo, dense_index, lexical_index, graph)

class QueryService:
    QueryService(repo, dense_index, lexical_index, graph, explainer=None)
    .discover(query: str) -> tuple[RankedConnection, ...]        # lru_cache(maxsize=64)
    .opportunities(query: str) -> tuple[Opportunity, ...]        # lru_cache(maxsize=64)
    .explainer_degraded: bool                                     # isinstance(explainer, TemplateExplainer)
    QueryService.build(fast=False, *, log=...) -> QueryService   # atajo: build_pipeline + build_explainer()
```

`scripts/query_cli.py` reusa `build_pipeline` (una sola definición del arranque, movida desde el propio CLI en Sprint-06). `interface/app.py` construye UN `QueryService` en el `lifespan` de FastAPI y lo expone vía `Depends(get_query_service)` — las rutas nunca arman el pipeline.

**Por qué la caché.** `generar_oportunidad` llama por dentro a `descubrir_conexiones` con la MISMA query (`generar_oportunidad.py`). Sin caché, navegar Resultados → Oportunidad → Auditoría sobre la misma consulta repetiría todo el pipeline en cada salto.

### 12.2 Rutas

| Ruta | Método | Devuelve | Estado M9 si falla |
|---|---|---|---|
| `GET /` | HTML | M1 — Discover | vacío por defecto (sin query) |
| `GET /results?q=` | HTML | M2 — lista rankeada | sin resultados: mensaje + acción; query vacía redirige a M1 |
| `GET /connection/{entity_id}?q=` | HTML | M3+M4+M6 | 404 si `entity_id` no está en los resultados de `q` |
| `GET /opportunity?q=` | HTML | M5 — cadena(s) | `generar_oportunidad` ya devuelve `()`; se muestra "no se pudo ensamblar" |
| `GET /audit?q=&a=&b=` | HTML | M7 — comparador | sin `a`/`b` pide seleccionar candidatos de `q` |
| `GET /api/discover?q=` | JSON | `{query, results: [...]}` | `results: []` si `q` vacía |
| `GET /api/connection/{entity_id}?q=` | JSON | `{query, connection}` | 404 |
| `GET /api/opportunity?q=` | JSON | `{query, opportunities: [...]}` | `opportunities: []` |
| `GET /api/audit?q=&a=&b=` | JSON | `{query, a, b, comparison}` | 404 si `a`/`b` no están en los resultados |
| `GET /api/stats` | JSON | `{entities, sources}` | — |

### 12.3 Presentación (`interface/presenters.py`)

Funciones puras, testeadas sin FastAPI/Jinja (`tests/interface/test_presenters.py`):

- **`breakdown_segments(feature_vector)`** — los 7 segmentos de la Relevance Breakdown Bar (signature, DESIGN.md M3), reusando `application/descubrir_conexiones.feature_contributions` (misma re-normalización de ADR-007/ADR-009, no reimplementada). Invariante verificado: `sum(pct)/100 == compute_score(fv)` exacto. Una feature en `None` se marca `na=True` — se pinta como "no medible", NUNCA como 0.
- **`relevance_band(score)`** — alta/media/baja usando `ALTO=0.6`/`MEDIO=0.4` de `domain/opportunity.py`; ningún umbral nuevo inventado para la UI. Medido con datos reales (`query_cli.py --fast` y con el modelo real): los scores viven en 0.40-0.66, así que la mayoría de resultados cae en "media" — honesto, no se ajustó el umbral para inflar la demo.
- **`subgraph_svg(viewed_entity, query_entity, connections, *, graph, repo=None)`** — mini-grafo (M6 embebido en M3): SVG inline, sin JS ni CDN (Regla R5), posiciones deterministas (`spring_layout(seed=42)`). Nodos: la entidad EN VISTA + sus vecinos REALES del `GraphStore` (tope `SUBGRAPH_MAX_NODES=15`) + la entidad de la consulta si es distinta. Dos tipos de arista, mismo principio que `link_type` de `domain/opportunity.py`: sólida oscura = arista REAL (tabla de relación); punteada lavanda = cómo se llegó a la entidad vista desde la consulta (reranking, no una arista).
- **`title_of(entity)`** — título legible por tipo de entidad (primera columna indexable de `dataset_paths.ENTITY_TABLES`); trunca a `TITLE_MAX_WORDS=12` para los tipos sin nombre propio (COMPETENCY, LEARNING_OUTCOME, cuyo primer campo indexable es su descripción larga).
- **`serialize_connection`/`serialize_opportunity`/`serialize_comparison`** — shape JSON compartida entre `/api/*` y las plantillas Jinja; `explanation`/`title` quedan vacíos si no se pasa `explainer`/`repo` (no fallan).

### 12.4 Vendorización (Regla R5)

Cero CDN: `static/knexus.css` define los tokens de `DESIGN.md §2` como custom properties; Montserrat es un único `.woff2` variable (`static/fonts/montserrat-variable.woff2`, weight range 100-900) servido por el propio backend. Verificado manualmente sin red (V5 de la sección de verificación del sprint).

### 12.5 Nota de infraestructura (macOS)

`faiss` y `torch` (vía `sentence-transformers`) empaquetan cada uno su propio runtime OpenMP; cargar ambos en el mismo proceso en macOS aborta con `SIGABRT` ("OMP: Error #15") al registrar el segundo — no depende de esta app, es un conflicto conocido entre esas dos librerías nativas. Fix aplicado en `adapters/retrieval/dense_index.py` y `adapters/embeddings/sentence_transformer_provider.py`: `os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")` antes de sus respectivos imports pesados — inocuo porque ninguna de las dos librerías usa paralelismo OpenMP dentro de la otra en este pipeline. Mismo patrón que la nota de infra de Sprint-03 (venv en ruta corta para Windows).

## 13. Contrato de evidencia de desempeño (Sprint-07)

> **Estado:** ✅ Implementado. **Capa:** `evaluation/` (fuera del hexágono de `src/`, Regla A2 extendida) + `interface/metrics_report.py` (lectura) + pantalla `/metrics` (M8).

### 13.1 Metodología del set etiquetado

No existe una tabla `need -> project/thesis` en el dataset (L4/R7: nada se fabrica). La relevancia de un NEED se aproxima por el **cluster de `application_context`** de sus proyectos/tesis: `evaluation/qrels.csv` (97 filas, 20 NEEDs — NEED-001..020; NEED-021..042 son meta/institucionales sin candidato temático real y quedan deliberadamente fuera, `test_meta_needs_fuera_de_alcance_no_estan_en_qrels`) lista, por NEED, las variantes ES/EN y sinónimos directos de su contexto de aplicación. `evaluation/qrels.py:build_relevant_sets` resuelve cada término contra `PROJECT`/`THESIS` reales y arma la unión — el "cluster" (variante por defecto, `strict=False`) — o sólo la primera fila (más literal) por NEED — la variante **estricta**, un análisis de sensibilidad, nunca el número principal.

`evaluation/qrels.py:validation_errors` se corre ANTES de cualquier medición (`harness.run_all` revienta con `ValueError` si no pasa): todo `need_id` debe existir en el repositorio, todo `application_context` debe matchear al menos una entidad real (caza typos — "label rot"), y ningún cluster de relevancia puede quedar vacío.

### 13.2 Los tres brazos del ablation

| Brazo | Qué hace | Qué aísla |
|---|---|---|
| `full` | Pipeline real completo: RRF (denso+léxico) + expansión por grafo + reranking de 7 features (`descubrir_conexiones`). | El sistema tal como lo usa el usuario. |
| `cosine` | LOS MISMOS candidatos de `full`, re-ordenados por `feature_vector.sim_semantica`. | La DECISIÓN DE ORDEN — comparten pool, así que los sesgos del pool se cancelan en el delta. |
| `dense` | Top-K directo del índice denso (`DenseIndex.search`), agregado campo→entidad (`aggregate_by_entity`), SIN RRF/grafo/reranking. | El SISTEMA completo de "similarity" puro — el examen literal de R6. Sus candidatos pueden no haber sido puntuados nunca por `full` (nunca entraron al pool fusionado de 50); esa fracción se reporta como `unscored_rate`, nunca como un 0 falso (mismo principio que N/A + re-normalización de ADR-007). |

Métricas por brazo (`evaluation/metrics.py`, puras): `precision_at_k` (P@5, P@10 — `k` siempre en el denominador, un ranking corto no infla el score), `recall_at_k` (R@10, R@30), `mrr`. **El techo teórico de recall se reporta siempre junto al número** (`_recall_ceiling`): con clusters de 21-34 entidades relevantes sobre un top-30, R@30 no puede exceder ~0.97-1.0 — un R@30 alto es parcialmente estructural, no sólo mérito del sistema.

`construct_validity` (top-5, sobre candidatos que `full` sí puntuó): `trap_rate` (fracción tipada `coincidencia_superficial`), `capability_rate` (`soporte_capacidad>=1.0`), `method_rate` (`compat_metodo>=0.6`), `actionable_rate` (tipo ∈ `{antecedente_metodologico, activacion_capacidad}`) — mide lo que P@K, construido sobre una etiqueta temática, no puede ver.

### 13.3 Sesgos declarados (nunca escondidos, R7)

- **La etiqueta de relevancia es temática** (`application_context`), no "conexión de valor decisorio". Esto favorece estructuralmente a los brazos de similitud pura: un candidato puede compartir vocabulario con el NEED (alto `sim_semantica`) sin tener método transferible ni capacidad institucional real. `construct_validity` existe precisamente para medir lo que P@K, sobre esta etiqueta, no puede ver.
- **Candidatos que entran por arista (ADR-011)** tienen `sim_semantica=0.0` por diseño (un investigador no comparte vocabulario textual con la necesidad) — esto penaliza a `full` frente a `cosine`/`dense` en P@K de forma estructural: un investigador correctamente enlazado por grafo puntúa 0 de similitud textual y cae fuera del top-5 de los brazos de similitud pura.
- **Hallazgo real medido (2026-08-27, modelo `paraphrase-multilingual-MiniLM-L12-v2`, 20 NEEDs, `evaluation/results.json`):** P@5 cluster = `full` 0.480 vs `cosine` 0.540 vs `dense` 0.540 — el pipeline real puntúa MÁS BAJO que los dos brazos de similitud pura en esta métrica. No se ocultó ni se ajustó nada para revertirlo (compromiso de honestidad de este sprint). La lectura correcta no es "el reranker es peor": es que P@K sobre una etiqueta temática mide relevancia temática, y el reranker deliberadamente pondera método/capacidad/evidencia por encima de la similitud textual (R6: "similarity ≠ relevance" es una elección de diseño, no un accidente). La evidencia de que esa elección vale la pena está en `construct_validity` del mismo run: `actionable_rate` del top-5 es 0.55 (`full`) vs 0.27 (`cosine`/`dense`) — el doble de conexiones con valor de decisión directo — y `trap_rate` es 0.28 (`full`) vs 0.65 (`cosine`/`dense`) — menos de la mitad de coincidencias superficiales. `cosine` y `dense` coinciden casi exactamente en este dataset (ambos brazos convergen al mismo orden dominado por `sim_semantica`, aunque parten de pools distintos: top-50 fusionado vs top-200 denso puro) — evidencia adicional de que P@K por sí solo no distingue "más similar" de "más accionable".

### 13.4 `results.json` y las rutas

`scripts/evaluate.py` (reusa `interface/composition.build_pipeline`, Regla A2) corre `harness.run_all` sobre el pipeline real y serializa `evaluation/results.json`: los bloques de `run_all()` (`precision_recall`, `recall_ceilings`, `construct_validity`, `per_need`, `avg_latency_ms`, `avg_dense_latency_ms`, `evidence_coverage`) más un bloque `meta` — `generated_at`, `provider`, `fast`, `entities_indexed`, `qrels_rows`, `needs_evaluated`, los `top_k_*` usados, `elapsed_s`. **El número siempre se muestra con su procedencia** (`meta`) — un P@5 sin fecha/modelo/tamaño de set no es auditable.

La medición NO corre en vivo por request (20 NEEDs con el modelo real toma varios segundos a minutos, incompatible con un request HTTP) — `interface/metrics_report.py` sólo LEE el JSON ya generado; sin archivo, degrada a `{"available": false}` (200, estado válido — M9 — nunca un 500). `interface/` no importa `evaluation/` (ver ARCHITECTURE.md §4).

| Ruta | Método | Devuelve | Estado M9 si falla |
|---|---|---|---|
| `GET /metrics` | HTML | M8 — stat tiles + Precision@K + ablation de 3 brazos + construct validity + tabla por NEED + procedencia | sin `results.json`: "No measurement recorded yet — run `scripts/evaluate.py`" |
| `GET /api/metrics` | JSON | `presenters.serialize_metrics(...)` — mismo DTO que consume la plantilla | `{"available": false}` (200) |
