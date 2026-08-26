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
