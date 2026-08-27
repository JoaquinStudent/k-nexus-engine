# MEMORY.md — Retrospectiva Continua

> Bitácora viva de lecciones aprendidas y errores a evitar.
> Se actualiza **al cierre de cada Sprint** (paso 4 del bucle de trabajo).
> Objetivo: no repetir errores entre Sprints.

---

## 1. Principios destilados (aprendizajes transversales)

| # | Lección | Origen | Regla derivada |
|---|---|---|---|
| L0 | El reto NO se gana con tecnología sofisticada, sino con conexiones pertinentes, trazables y demostrables. | Lectura de las bases | Priorizar end-to-end funcional sobre features vistosas. |
| L1 | El dataset es pequeño (~2.000 entidades): todo cabe en memoria. | Auditoría de datos | Prohibido vector DB cloud / GPU / microservicios. Sería sobre-ingeniería. |
| L2 | El dataset mezcla español e inglés a propósito ("deserción" ↔ "student attrition"). | Análisis de documentos | Embeddings multilingües obligatorios; nunca TF-IDF solo. |
| L3 | "Similarity ≠ Relevance" es el examen central. | Documento Técnico | El score se descompone en features auditables, no en coseno. |
| L4 | Lo que no corre en vivo se considera "trabajo futuro". | Rúbrica | El sistema debe responder a consultas nuevas sin precargados. |
| L5 | Los NEED no traen método (el MD lo declara a propósito); el Jaccard simétrico de `compat_metodo` degenera a 0 en todo par NEED→candidato y volvía inalcanzable `antecedente_metodologico`. | Auditoría del dataset (Sprint-01.5) | Feature con un lado estructuralmente vacío: puntuar por **transferabilidad** (tipo-de-problema inferido → método real del candidato) y, sin señal, marcar **N/A + re-normalizar** — nunca un 0 falso. |
| L6 | Una feature "casi-constante" (siempre `False`, siempre 0, o auto-saturada en 1.0) no rompe ningún test escrito con fixtures a mano — sólo se ve midiendo la distribución sobre datos reales. Pasó 3 veces (`compat_metodo` en Sprint-01.5, `graph_linked`/`has_capability_support`/`compat_dominio`/`densidad_evidencia` en Sprint-03). | Auditorías repetidas antes de cada plan de sprint | Todo sprint que toque features debe correr (o extender) `test_feature_discrimination.py` sobre una muestra real antes de darse por cerrado — no basta con que los tests con fixtures pasen. |
| L7 | Implementar correctamente la LÓGICA de una feature relacional (`graph_linked`) no basta si el pipeline nunca le da la oportunidad de activarse — hacía falta EXPANDIR el pool de candidatos por el grafo, no solo puntuar lo que la búsqueda textual trajo. El síntoma (0 investigadores enlazados) sólo apareció corriendo el pipeline COMPLETO end-to-end, nunca en tests unitarios de la feature aislada. | Prueba manual del pipeline completo (Sprint-04) | Una feature relacional necesita que su fuente de candidatos también sea relacional, no sólo textual — probar la pieza aislada no sustituye probar el recorrido completo con datos reales. |
| L8 | Un test que compara strings en memoria no prueba que ese string sea seguro de IMPRIMIR — `TemplateExplainer` usaba "→" (Unicode) y pasaba todos sus tests, pero reventaba con `UnicodeEncodeError` al redirigir la salida del CLI en Windows (`cp1252` por defecto). | Ejecución manual de la demo, no de los tests (Sprint-05) | Para cualquier texto que vaya a stdout/un archivo/un log, preferir ASCII plano en vez de Unicode decorativo, o probar explícitamente la escritura a un stream con encoding restringido — no basta con `assert texto == esperado`. |

---

## 2. Registro de Sprints

### Sprint-00 — Scaffolding (Infraestructura SDD + Scrum)

| Dimensión | Detalle |
|---|---|
| **Objetivo** | Auditar entorno y crear infraestructura documental (9 artefactos). |
| **✅ Qué funcionó** | Directorio raíz limpio; scaffolding creado sin colisiones; arquitectura Pipeline+Hexagonal confirmada por el PO antes de codificar. |
| **⚠️ Qué vigilar** | El dominio puro debe permanecer sin imports externos; verificar en cada Sprint con un test de arquitectura. |
| **❌ Errores a evitar** | No arrancar a codificar el reranker antes de tener el `EntityRepository` con provenance. Sin provenance, no hay trazabilidad recuperable. |
| **🔁 Acción para el próximo Sprint** | Sprint-01 = núcleo de dominio (features + scoring), lo más testeable y lo que desbloquea todo. |

---

### Sprint-01 — Núcleo de Dominio (features + scoring + tipado)

| Dimensión | Detalle |
|---|---|
| **Objetivo** | Construir features.py, scoring.py, relation_type.py puros y testeados TDD Rojo→Verde. |
| **✅ Qué funcionó** | TDD estricto: los 5 tests se escribieron antes que la implementación y fallaron por `ModuleNotFoundError` (Rojo real, no simulado). El caso estrella A vs B (DoD-3) validó que compat_metodo desempata con sim_semantica idéntica. |
| **⚠️ Qué vigilar** | El test de arquitectura A1 inicialmente marcó falso positivo en imports intra-`domain/` (`src.domain.models` importado por `features.py`/`scoring.py`/`relation_type.py`); se corrigió el propio test para no confundir import intra-paquete con dependencia externa. |
| **❌ Errores a evitar** | No asumir Python 3.11 disponible en el entorno del PO; el sistema traía 3.14 vía Homebrew. Se creó `.venv` local en `knexus/` para aislar pytest sin tocar el Python del sistema. |
| **🔁 Acción para el próximo Sprint** | Sprint-02 = ingesta + provenance + EntityRepository. Los tipos `QueryEntity`/`CandidateEntity` de `models.py` ya definen el contrato de entrada que la ingesta deberá producir. |

---

### Sprint-01.5 — Endurecimiento del núcleo: `compat_metodo` para NEED (ADR-007)

| Dimensión | Detalle |
|---|---|
| **Objetivo** | Resolver que los NEED no traen método (el MD lo declara a propósito), lo que dejaba `compat_metodo` (peso 0.20) en 0 para todo par NEED→candidato y volvía **inalcanzable** el tipo estrella `antecedente_metodologico`. |
| **✅ Qué funcionó** | Híbrido en 3 escalones (Jaccard simétrico → transferabilidad `problem_type→método` → N/A + re-normalización). TDD Rojo real (`ModuleNotFoundError` de `method_compat`). No-regresión exacta verificada (0.872000 == 0.872000). Titular reproducido sobre datos reales: NEED-001→PRJ-004 = 0.678 `antecedente_metodologico` vs PRJ-007 = 0.448. 8/8 verdes. |
| **⚠️ Qué vigilar** | La tabla `TRANSFERABILITY` de `method_compat.py` es vocabulario controlado: mantenerla pequeña y explícita (auditable). Un NEED sin señal derivable cae a N/A (correcto, degrada sin fallar), pero si muchos caen ahí conviene ampliar la tabla, no bajar el listón. |
| **❌ Errores a evitar** | No representar N/A como 0 (falsea el score y bloquea el tipado). No asignar método al NEED: se infiere *tipo de problema* del texto y se puntúa el método **real del candidato** — la UI debe rotularlo como "transferabilidad inferida". |
| **🔁 Acción para el próximo Sprint** | Sprint-02 implementa la inferencia de `problem_types` (texto del NEED) y el minado de `methods` (`projects.methodology`/`keywords`) que alimentan este híbrido. Reconciliar el entorno de pruebas (ver nota de infra abajo). |

> **Nota de infraestructura (corrección).** La retro de Sprint-01 dice que se creó un `.venv` en `knexus/`; **ese venv no está en el repo**. En este entorno (Windows, Python 3.12 de Microsoft Store) `pytest` se instaló en el Python del sistema para verificar. Pendiente: crear `requirements.txt` (mín. `pytest`) y decidir venv vs. sistema; añadir `.pytest_cache/` y `__pycache__/` a `.gitignore`.

---

### Sprint-02 — Ingesta + Provenance + Entity Store

| Dimensión | Detalle |
|---|---|
| **Objetivo** | Cargar las 22 tablas CSV + 60 MD de Data V1.0 con provenance campo-por-campo, servidas por `EntityRepository` (puerto), y cerrar el lazo de ADR-007 sobre entidades reales. |
| **✅ Qué funcionó** | `pandas.read_csv(..., keep_default_na=False)` respeta la "controlled missingness" del manifest sin inventar NaN. El vocabulario de `enrichment.py` se valida por `assert` contra `method_compat.TRANSFERABILITY` (anti-drift) — imposible que ingesta y dominio diverjan en silencio. 19/19 tests verdes a la primera corrida completa; 2.512 entidades cargadas cuadran exacto con la suma de los 3 manifests (Block A+B+C). |
| **⚠️ Qué vigilar** | **El ejemplo "verificado" que se escribió en `SPEC.md §9.1` durante Sprint-01.5 estaba mal etiquetado**: los números venían de un fixture de test inyectado a mano, no del dataset real — y de hecho el dataset real no tiene ningún proyecto con método "encuesta" (PRJ-004 y PRJ-007 reales comparten el mismo método). Se corrigió `SPEC.md` con el par real (PRJ-004 vs PRJ-002). **Lección: nunca marcar un número como "verificado sobre datos reales" hasta que la ingesta exista** — antes de Sprint-02 sólo estaba verificado contra fixtures. |
| **❌ Errores a evitar** | No usar `str.split(',')` sobre los CSV: `projects.methodology` trae comas embebidas dentro de campos entrecomillados; requiere parser CSV real (pandas ya lo maneja). No olvidar `encoding='utf-8-sig'` — los headers traen BOM. |
| **🔁 Acción para el próximo Sprint** | Sprint-03 = representación (embeddings bge-m3 + FAISS + BM25 + grafo NetworkX). Las 7 tablas de relación ya están cargadas como aristas (`repo.edges(relation)`) — el grafo de Sprint-03 las consume directo, sin re-parsear CSV. `has_capability_support`/`graph_linked` en `projection.py` siguen en `False` por defecto hasta que Sprint-03/04 los conecten. |

---

### Sprint-03 — Representación (denso + léxico + grafo) y revivir el 25% inerte

| Dimensión | Detalle |
|---|---|
| **Objetivo** | Construir los 3 índices (denso, léxico, grafo) y, al auditar antes de planear, cerrar el 25% de peso (`soporte_capacidad`+`enlace_estructural`) que `projection.py` dejaba fijo en `False` desde Sprint-02. |
| **✅ Qué funcionó** | El patrón N/A + re-normalización de ADR-007 se reutilizó tal cual para ADR-009 (`compat_dominio`) — cero cambios en `scoring.py`. El test de discriminación sistémico (`test_feature_discrimination.py`) **cazó 3 problemas reales antes de que llegaran a producción**: (1) mi primer diseño de `has_capability_support` por `capability_type` daba `True` al 97.8% de los proyectos — se descartó y se rediseñó sobre el tema real de `capability_name` (21.6%/78.4%, discrimina de verdad); (2) `densidad_evidencia` estaba auto-saturada en 1.0 para el 96% de la muestra por un bug de Sprint-02 (`expected_fields = max(declarado, len(filled_fields))` nunca podía ser menor que lo ya llenado); (3) el muestreo inicial del propio test no encontraba investigadores conectados (slice ciego de `by_type()`, los IDs con arista real no caían en las primeras filas del CSV) — se corrigió el test, no el código. `venv` en ruta corta (`C:\kvenv`) resolvió el fallo de `torch` por `MAX_PATH` de Windows con el Python de Microsoft Store (ver nota de infra). |
| **⚠️ Qué vigilar** | **Un cuarto hallazgo del mismo patrón, encontrado pero NO corregido a propósito**: `sim_lexica` también es 0 constante para todo NEED (`institutional_needs.csv` no tiene columna `keywords`) — pero a diferencia de `compat_dominio`, esto se dejó así porque el SPEC pesa `sim_lexica` en 0.05 *a propósito* como "la más débil, evita premiar la trampa léxica"; forzarla a variar iría contra el diseño. Documentado con un test dedicado (`test_sim_lexica_es_cero_constante_por_diseno_no_por_bug`) para que no se confunda con una regresión en el futuro. |
| **❌ Errores a evitar** | No usar `capability_type` como señal de capacidad institucional en este dataset: es prácticamente ruido (cada uno de los 12 temas de `capability_name` aparece con los 7 `capability_type` casi por igual — decorrelacionados). La señal real siempre está en el campo de texto más específico (`capability_name`), nunca en la categoría gruesa, si la categoría gruesa no se audita primero contra la variable que se quiere predecir. |
| **📋 Nota de rigor TDD** | A diferencia de Sprint-01/01.5 (Rojo real antes de cada línea de implementación), Sprint-03 fue más exploratorio: varias piezas (`capability_match.py`, el rediseño de `has_capability_support`, `MD_SECTION_COUNTS`) se escribieron auditando primero la forma real de los datos, y los tests de cierre se escribieron después de tener una implementación candidata — no antes. El Rojo real que sí se observó fue el de módulos inexistentes al importar. Es una desviación honesta del proceso estricto, no un intento de ocultarla. |
| **🔁 Acción para el próximo Sprint** | Sprint-04 (recuperación híbrida + reranking) es quien arma `seed_ids` de verdad (candidatos ya recuperados por RRF) para alimentar `graph_linked` en producción — hoy sólo se probó con seeds construidos a mano en tests. Ampliar `NEED_SECTOR_PHRASES`/`METHOD_PHRASES` sigue siendo incremental, no bloqueante (cobertura ya en mayoría clara). |

> **Nota de infraestructura.** `sentence-transformers` (→ torch) **no instala** en el Python de Microsoft Store de este equipo: la ruta de `site-packages` es tan profunda (`...LocalCache\local-packages\Python312\site-packages\...`) que un header interno de torch llega a los 260 caracteres exactos (`MAX_PATH` de Windows sin long-paths). Fix: `python -m venv C:\kvenv` (ruta corta) + instalar ahí. Comando de tests de esta sesión: `/c/kvenv/Scripts/python.exe -m pytest tests/ -v` (no el `python` del PATH). `requirements.txt` ya lista `sentence-transformers`; documentar este workaround en el README de Sprint-08.

---

### Sprint-04 — Recuperación híbrida + Reranking explicable

| Dimensión | Detalle |
|---|---|
| **Objetivo** | Orquestar dominio + ingesta + representación en un pipeline real: RRF genera candidatos, el reranker de 7 features decide el orden, y queda un comparador "¿por qué A antes que B?" para la defensa. |
| **✅ Qué funcionó** | El patrón de invariante aditivo se repite con éxito: igual que `compute_score` es la suma de contribuciones normalizadas, `auditar_resultado.comparar` reproduce el delta de score exacto como suma de deltas por feature — un test lo verifica byte a byte. `ScoredResult` (definido en Sprint-01, nunca usado) por fin tiene consumidor real. |
| **✅ Regla A2 corregida antes de construir sobre ella** | `BM25Index`/`NetworkXGraphStore` no heredaban de sus puertos y `DenseIndex` no tenía puerto (funcionaban por duck typing desde Sprint-03) — se corrigió con un test de arquitectura A2 nuevo. En el camino, el primer borrador de ese test prohibía a `application/` importar CUALQUIER cosa de `adapters/`, lo cual habría hecho inviable el propio plan aprobado (`to_query_entity`/`to_candidate_entity` son mappers, no adapters swappeables). Se corrigió el test para prohibir solo la instanciación de CLASES concretas de puertos, no la reutilización de funciones utilitarias — la regla real de A2 es "no acoplarse a una implementación intercambiable", no "cero imports". |
| **✅ Vocabulario reubicado a `domain/` (mismo motivo)** | `query_builder.py` necesitaba `infer_problem_types`/`infer_sectors` para texto libre, pero vivían en `adapters/repository/enrichment.py`. Se movieron (junto con `vocabulary.py`) a `domain/text_matching.py` y `domain/vocabulary.py` — son puros (sin librerías externas más allá de `unicodedata`), así que pertenecían ahí desde Sprint-02/03. Los módulos viejos quedaron como shims de re-export: cero cambios en los call-sites existentes. |
| **⚠️ Hallazgo grave encontrado probando contra datos reales (no en el plan original)** | El primer `descubrir_conexiones.py` dejaba `graph_linked` **correctamente implementado pero vacío en la práctica**: 0 investigadores llegaban al top-50 de candidatos, con `HashingProvider` Y con el modelo real, porque el pool de candidatos salía SÓLO de la búsqueda textual — y el perfil académico de un investigador casi nunca comparte vocabulario con el texto de una necesidad. Fix: tras la pasada 1, el pool se **expande** con los vecinos de grafo de los candidatos fuertes antes de la pasada 2 (`_expand_by_graph`). Es la versión literal del argumento que ya estaba en ADR-008: "el investigador no lo trae el texto, lo trae la arista" — pero antes de este fix esa frase no estaba realmente implementada, solo el mecanismo de puntuación lo estaba. |
| **⚠️ HashingProvider satura el pool con boilerplate entre NEEDs** | Con `HashingProvider` (y hasta cierto punto BM25), los 42 NEED comparten tanta estructura de plantilla ("La institución requiere fortalecer su capacidad para abordar X mediante...") que 34/50 candidatos del top-N terminaban siendo OTROS NEEDs, no proyectos/tesis. Con el modelo real (embeddings semánticos) esto casi desaparece — es una limitación conocida y aceptada del adapter de degradación A4 (léxico/morfológico, no semántico), no un bug del pipeline. El test de `graph_linked` en producción se diseñó para tolerar esto (offline, con expansión de grafo cubriendo el hueco) en vez de exigir el modelo real. |
| **❌ Errores a evitar** | No filtrar top-N de un índice y ASUMIR que ya viene sin la propia entidad de la consulta — si la consulta es una entidad real del dataset, hay que excluirla explícitamente de sus propios resultados antes de fusionar (si no, se autoincluye como su "mejor match"). No medir discriminación de `soporte_capacidad` sobre una mezcla de tipos donde la mayoría estructuralmente no puede tenerla (NEED/RESEARCHER no minan `methods`) — hay que filtrar a los tipos elegibles (PROJECT/THESIS) o la métrica mide la composición del pool, no la regla. |
| **🔁 Acción para el próximo Sprint** | Sprint-05 (Oportunidad + Explainer) consume `RankedConnection.top_features` (datos) para producir prosa — `TemplateExplainer` sin red primero, `LlmExplainer` opcional después. La cadena necesidad→antecedente→investigador→capacidad→currículo ya tiene sus piezas sueltas (expansión de grafo, `soporte_capacidad`, `integracion_curricular`); falta ensamblarla como recorrido explícito. |

---

### Sprint-05 — Ensamblado de Oportunidad + Explainer

| Dimensión | Detalle |
|---|---|
| **Objetivo** | Ensamblar la cadena necesidad→antecedente→investigador→capacidad→currículo (F5) y redactarla en lenguaje natural (F6), sin fabricar ningún eslabón que no exista realmente. |
| **✅ Qué funcionó** | El hallazgo de diseño previo al código (auditoría antes de planear) evitó un error caro: los 4 eslabones NO tienen la misma fuerza probatoria (puntuado / hecho duro / inferido), así que cada `ChainLink` declara `link_type` explícito — sin esto habría sido el antipatrón "grafo bonito pero hueco" ya fichado en la lista negra, pero aplicado a una cadena en vez de a un grafo visual. El patrón de invariante aditivo se repitió una tercera vez con éxito: `opportunity_priority` combina score + nº de eslabones "edge" de forma explícita y testeable, sin números mágicos escondidos. Reutilizar `capability_match.find_matching_capability` (refactor de una línea sobre `has_capability_support` ya existente) evitó duplicar la regla de ADR-008 para saber CUÁL capacidad, no sólo si hay alguna. |
| **✅ El eslabón curricular se verificó con el modelo real, no con HashingProvider** | Con HashingProvider, "Analítica educativa" (SUB-083) ni siquiera entraba en el top-1000 de similitud para NEED-001, y "Diseño curricular" ganaba por casualidad léxica. Con el modelo real, SUB-083 puntuó claramente por encima de SUB-084 ("Lenguaje y conocimiento", mismo programa, mismo sector) — confirma que la discriminación semántica real es indispensable para el eslabón curricular, no solo deseable; el test que lo prueba está marcado `@slow` a propósito. |
| **✅ Probado en 2 dominios sin sobre-ajuste** | NEED-001 (deserción estudiantil) y NEED-009 (calidad del agua) producen cadenas completas y coherentes, cada una con su propia capacidad (CAP-002 vs CAP-003) y su propio componente curricular (SUB-083 vs SUB-085) — nada hardcodeado al caso de deserción que domina los ejemplos de `DESIGN.md`. |
| **🐛 Bug encontrado en la demo, no en los tests** | `TemplateExplainer` usaba "→" (U+2192) en la cadena legible; al redirigir la salida del CLI a un archivo en Windows, Python usa `cp1252` por defecto y la ejecución revienta con `UnicodeEncodeError`. Los tests nunca lo cazaron porque comparan el string en memoria, no lo escriben a un stream con encoding restringido. Fix: usar `->` (ASCII) en vez del carácter Unicode. Lección: un test que sólo compara strings en memoria no prueba que el string sea SEGURO de imprimir en cualquier consola/redirección. |
| **❌ Errores a evitar** | No traversar el currículo a ciegas (primer subject del programa) — de los 7 subjects de un programa típico, sólo 1-2 son pertinentes a una necesidad dada; hay que puntuarlos con las mismas 7 features que todo lo demás, una sola vara de medir. No comparar `researcher.faculty_id` contra `need.originating_unit` con igualdad exacta — `originating_unit` es texto libre ("Unidad asociada a FAC-004"); usar `in` (substring). |
| **🔁 Acción para el próximo Sprint** | Sprint-06 (Interfaz) consume `Opportunity`/`RankedConnection` + el texto del `Explainer` para las pantallas M2/M5/M7 de `DESIGN.md`. `LlmExplainer` sigue sin probarse contra la API real (sin key configurada en este entorno) — validarlo con una key real antes de la demo si se decide usarlo en vivo. |

## 3. Antipatrones detectados (lista negra)

| Antipatrón | Por qué es peligroso |
|---|---|
| Rankear por coseno pelado | Cae en todas las trampas del reto; el jurado lo desarma en la auditoría. |
| Grafo "bonito pero hueco" | Visual impactante sin scoring defendible = puntaje bajo en pertinencia. |
| Depender de la API del LLM para la lógica | Si cae la red en la demo, se cae el sistema. Usar adapter de plantillas como respaldo. |
| Devolver muchos resultados | "Más resultados ≠ mejor solución". Priorizar y podar. |
| Dejar la trazabilidad para el final | Si no se captura en la ingesta, no se reconstruye. |

---

## 4. Decisiones arquitectónicas registradas (ADR ligero)

| ID | Decisión | Estado |
|---|---|---|
| ADR-001 | Arquitectura Pipeline (Pipes & Filters) + Hexagonal + dominio puro. | Aceptada |
| ADR-002 | `Explainer` como puerto con doble adapter (`LlmExplainer` / `TemplateExplainer`). | Aceptada |
| ADR-003 | Índices en memoria: FAISS flat (denso) + rank-bm25 (léxico); NetworkX para grafo. | Aceptada |
| ADR-004 | Sistema de diseño en `DESIGN.md`; mocks se modelan en Google Stitch con prompts por módulo. | Aceptada |
| ADR-005 | Paleta: índigo `#251D4B` como base (cumple "azul oscuro"); lavandas del PO solo como acentos; se añaden neutros, semánticos de relevancia y colores de grafo. | Aceptada |
| ADR-006 | Signature element del producto: "Relevance Breakdown Bar" (descompone el score en 7 features). | Aceptada |
| ADR-007 | `compat_metodo` híbrido: Jaccard simétrico si la consulta trae métodos; si no, transferabilidad `problem_type→método` (tabla explícita en `method_compat.py`); sin señal, N/A + re-normalización de pesos. `problem_types` de los NEED se infiere en ingesta (Sprint-02), no en el dominio. | Aceptada |
| ADR-008 | `has_capability_support` cruza sector + **tema de `capability_name`** (no `capability_type`, decorrelacionado del tema real) + madurez≥4 (`capability_match.py`). `graph_linked` es relacional: adyacencia real a otro candidato fuerte de la MISMA consulta (`graph`/`seed_ids` en `to_candidate_entity`), no "existe en el grafo" — sin contexto, ambas quedan en `False` (cero regresión). | Aceptada |
| ADR-009 | `compat_dominio` sigue el mismo patrón N/A + re-normalización que ADR-007: los NEED no tienen ninguna columna de dominio, así que se infiere un **sector** institucional (8 valores) del texto del NEED (`vocabulary.py:NEED_SECTOR_PHRASES`) y el candidato se etiqueta con el mismo sector (`capability_match.domain_sector`, reutilizado de ADR-008) para que Jaccard tenga vocabulario común. | Aceptada |
| ADR-010 | Regla A2 explícita: `application/` puede reutilizar funciones/mappers de `adapters/` (`to_query_entity`, `build_corpus`, `fuse`...) pero NUNCA instancia una clase concreta que implemente un puerto (`SentenceTransformerProvider`, `DatasetEntityRepository`, `BM25Index`, `DenseIndex`, `NetworkXGraphStore`) — esas se inyectan ya construidas desde el composition root. Vocabulario puro (`vocabulary.py`, `text_matching.py`) se reubicó a `domain/` porque tanto ingesta como consulta en vivo lo necesitan sin crear esa dependencia. | Aceptada |
| ADR-011 | `descubrir_conexiones` expande el pool de candidatos con los vecinos de grafo de los seeds de la pasada 1, además de lo que trajo la búsqueda textual — sin esto, `graph_linked` es correcto pero vacío en la práctica (un investigador rara vez comparte vocabulario con una necesidad). El candidato "entra por la arista, no por el texto": evidencia = su propio campo más largo, `sim_semantica=0.0` (honesto: no hay señal de recuperación textual para él). | Aceptada |
| ADR-012 | Cada `ChainLink` de la cadena de oportunidad declara `link_type` ∈ {`retrieved`, `edge`, `inferred`} — antecedente puntuado, investigador/currículo como hecho duro (arista/FK real), capacidad inferida (ADR-008, sin tabla de enlace). Presentar los tres como equivalentes sería la "trazabilidad de mentira" que la rúbrica penaliza. El eslabón curricular se elige por score (`compute_features`/`compute_score`, mismas 7 features que el resto) entre los subjects/competencies del programa del investigador — nunca por traversal ciega al primero encontrado. Un eslabón ausente (sin investigador, sin capacidad, sin currículo pertinente) simplemente no aparece; nunca se fabrica. | Aceptada |
