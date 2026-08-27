# SPEC.md — Sprint-01

> **Épica:** Núcleo de Dominio — features + scoring + tipado
> **Estado:** 🔲 Pendiente (listo para Sprint Planning)
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
