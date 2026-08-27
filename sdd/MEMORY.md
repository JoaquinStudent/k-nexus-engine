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
