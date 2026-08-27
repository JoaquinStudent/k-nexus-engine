# BACKLOG.md — KNexus Engine

> Backlog maestro del proyecto. Gestionado por el PO.
> Estados: `🔲 Pendiente` · `🔄 En curso` · `✅ Done` · `⏸️ Bloqueado`
> DoD = Definition of Done (criterios de aceptación verificables).

---

## Tablero de Sprints

| ID Sprint | Épica | Estado | Criterios de Aceptación (DoD) |
|---|---|---|---|
| **Sprint-00** | Scaffolding & Infraestructura documental (SDD+Scrum) | ✅ Done | Los 9 artefactos existen · arquitectura Pipeline+Hexagonal documentada en `ARCHITECTURE.md` · `schema.sql` con placeholder `ChaparroVillavicencioJoaquin` · `BACKLOG.md` tabulado. |
| **Sprint-01** | Núcleo de Dominio: features + scoring + tipado | ✅ Done | Tests Rojo→Verde de las 7 features · `scoring.py` combina features ponderadas · `relation_type.py` clasifica la conexión · `domain/` sin imports externos (test de arquitectura A1 verde). |
| **Sprint-02** | Ingesta + Provenance + Entity Store | 🔲 Pendiente | Carga CSV + 60 MD · cada texto arrastra `archivo/registro/campo` · `EntityRepository` implementado contra su puerto · test de trazabilidad end-to-end verde · **inferir `problem_types` del texto de los NEED (vocabulario controlado) y minar `methods` de `projects.methodology`/`keywords` para alimentar `compat_metodo` híbrido (ADR-007).** |
| **Sprint-03** | Representación: índices denso + léxico + grafo | 🔲 Pendiente | Embeddings bge-m3 en FAISS flat · BM25 operativo · grafo NetworkX con aristas explícitas desde tablas de relación · consulta cruza ES↔EN. |
| **Sprint-04** | Recuperación híbrida + Reranking explicable | 🔲 Pendiente | Fusión RRF genera candidatos · reranker produce score desglosado en 7 features · demo "¿por qué A antes que B?" reproducible. |
| **Sprint-05** | Ensamblado de Oportunidad + Explainer | 🔲 Pendiente | Cadena necesidad→antecedente→investigador→capacidad→currículo · `TemplateExplainer` funciona sin red · `LlmExplainer` opcional con grounding. |
| **Sprint-05.5** | Diseño & Mocks en Google Stitch (`DESIGN.md`) | 🔄 En curso | Sistema de diseño definido · 9 módulos con prompt de Stitch · paleta índigo+lavanda+semánticos · Relevance Breakdown Bar como signature. |
| **Sprint-06** | Interfaz (FastAPI + Streamlit) + mini-grafo | 🔲 Pendiente | UI minimalista alto contraste, azul oscuro, Montserrat · panel score+evidencia+procedencia · responde a query nueva en vivo · fiel a `DESIGN.md`. |
| **Sprint-07** | Evidencia de desempeño (Precision@K + ablation) | 🔲 Pendiente | Mini-set de validación etiquetado · P@5 y P@10 reportados · ablation coseno-solo vs reranker completo demuestra la mejora. |
| **Sprint-08** | Empaque de entregables (README, diagrama, declaración) | 🔲 Pendiente | README reproducible · diagrama = lo implementado · declaración de tecnologías externas · 2-3 casos demostrables ensayados. |

---

## Épicas → valor en la rúbrica

| Épica | Criterio de rúbrica que ataca | Puntos aprox. |
|---|---|---|
| Núcleo de Dominio (S-01) | Priorización · Calidad de conexiones · Explicabilidad | Específicos KN |
| Ingesta + Provenance (S-02) | Explicabilidad y trazabilidad · Representación | 4 + 6 |
| Representación (S-03) | Representación e integración del conocimiento | 6 |
| Recuperación + Reranking (S-04) | Calidad y pertinencia de conexiones · Priorización | 8 + 5 |
| Oportunidad + Explainer (S-05) | Generación de oportunidades y valor académico | 7 |
| Interfaz (S-06) | Funcionamiento del prototipo · Arquitectura | 20 + 20 |
| Evidencia (S-07) | Validación técnica · Innovación | 5 + 15 |
| Empaque (S-08) | Impacto y escalabilidad · reproducibilidad | 10 |

---

## Orden de ejecución recomendado

| Prioridad | Sprint | Razón |
|---|---|---|
| 1 | S-01 (Dominio) | Es lo más testeable y desbloquea el valor central; independiente de datos. |
| 2 | S-02 (Ingesta) | Alimenta todo lo demás; sin provenance no hay trazabilidad. |
| 3 | S-03 (Representación) | Habilita la recuperación. |
| 4 | S-04 (Reranking) | Integra dominio + representación = corazón demostrable. |
| 5 | S-05 → S-06 | Oportunidad y cara visible. |
| 6 | S-07 → S-08 | Evidencia y empaque final. |

> **Nota de paralelización (3 personas):** S-01 (Dominio) y S-02 (Ingesta) pueden correr en paralelo si se acuerda primero el formato del entity store. S-06 (UI) puede adelantarse con datos mock que respeten el contrato de salida.
