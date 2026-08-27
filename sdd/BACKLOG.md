# BACKLOG.md — KNexus Engine

> Backlog maestro del proyecto. Gestionado por el PO.
> Estados: `🔲 Pendiente` · `🔄 En curso` · `✅ Done` · `⏸️ Bloqueado`
> DoD = Definition of Done (criterios de aceptación verificables).

---

## Tablero de Sprints

| ID Sprint | Épica | Estado | Criterios de Aceptación (DoD) |
|---|---|---|---|
| **Sprint-00** | Scaffolding & Infraestructura documental (SDD+Scrum) | ✅ Done | Los 8 artefactos de `sdd/` existen (auditoría Sprint-03: el 9º contado originalmente es `README.md` del proyecto, correctamente diferido a Sprint-08 per `TECH_STACK.md` §4) · arquitectura Pipeline+Hexagonal documentada en `ARCHITECTURE.md` · `schema.sql` con placeholder `ChaparroVillavicencioJoaquin` · `BACKLOG.md` tabulado. |
| **Sprint-01** | Núcleo de Dominio: features + scoring + tipado | ✅ Done | Tests Rojo→Verde de las 7 features · `scoring.py` combina features ponderadas · `relation_type.py` clasifica la conexión · `domain/` sin imports externos (test de arquitectura A1 verde). |
| **Sprint-02** | Ingesta + Provenance + Entity Store | ✅ Done | Carga CSV (22 tablas, 2.512 entidades + 3.536 aristas) + 60 MD fusionados por entidad · cada texto arrastra `archivo/registro/campo` (`Provenance`, placeholder `ChaparroVillavicencioJoaquin`) · `DatasetEntityRepository` implementa `EntityRepository` (puerto) · enriquecimiento (`methods`/`problem_types`/`keywords`/`domains`) alimenta `compat_metodo` híbrido (ADR-007) · test de trazabilidad end-to-end y cierre ADR-007 sobre datos reales verdes (19/19). |
| **Sprint-03** | Representación: índices denso + léxico + grafo + revivir 25% inerte | ✅ Done | Embeddings multilingües (`paraphrase-multilingual-MiniLM-L12-v2`, no bge-m3 — swap de una línea) en FAISS flat (fallback numpy) · BM25 operativo con folding de acentos · grafo NetworkX sobre las 7 relaciones ya cargadas (3.536 aristas) · consulta cruza ES↔EN verificado con el modelo real · `graph_linked`/`has_capability_support` dejan de ser `False` constante (ADR-008) · `compat_dominio` deja de ser 0 constante para NEEDs (ADR-009) · cobertura de vocabulario 17-18-40% → 97.8%-96.8%-76.2% (método/método/problem_type) · bug de `densidad_evidencia` auto-saturada en 1.0 corregido · test de discriminación sistémico (49/49 verdes) que habría cazado los tres hallazgos el día que se introdujeron. |
| **Sprint-04** | Recuperación híbrida + Reranking explicable | ✅ Done | Fusión RRF (denso+léxico, agregación campo→entidad) genera candidatos, nunca entra al score final (invariante verificado) · `descubrir_conexiones` (capa `application/`, nueva) produce `RankedConnection` con score desglosado en 7 features y evidencia trazable · pipeline en 2 pasadas + expansión por grafo cierra `graph_linked` en producción (sin seeds a mano) · `auditar_resultado.comparar` reproduce "¿por qué A antes que B?" (PRJ-004 vs PRJ-002, delta exacto por feature) · consulta en texto libre infiere señal como un NEED · caché de vectores (arranque 15s→cache hit evita recodificar) · Regla A2 corregida (adapters heredan de sus puertos; vocabulario puro movido a `domain/`) · 88/88 tests verdes. |
| **Sprint-05** | Ensamblado de Oportunidad + Explainer | 🔲 Pendiente | Cadena necesidad→antecedente→investigador→capacidad→currículo · `TemplateExplainer` funciona sin red · `LlmExplainer` opcional con grounding. |
| **Sprint-05.5** | Diseño & Mocks en Google Stitch (`DESIGN.md`) | ✅ Done | Sistema de diseño definido · 9 módulos con prompt de Stitch · paleta índigo+lavanda+semánticos · Relevance Breakdown Bar como signature. Mocks generados en `mocks-stitch/` (12 pantallas: query, results, connection_detail, evidence_provenance, knowledge_graph, opportunity, why_a_over_b_audit, empty/no_results/loading/system_alert/performance). |
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
