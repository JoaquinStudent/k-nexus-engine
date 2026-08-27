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
| `compat_dominio` | 0..1 | Solape de `domains` (application_domains / disciplinary_area). |
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
> **Features N/A y re-normalización (ADR-007).** Una feature puede ser N/A cuando no es medible para el par (hoy sólo `compat_metodo`, ante consultas que no prescriben método). En ese caso se **excluye** del sumatorio y los pesos restantes se **re-normalizan** a 1.0. Con las 7 features presentes el resultado es idéntico al cálculo directo. Esto evita el techo artificial de ~0.80 sin inventar datos ni alterar `WEIGHTS`.

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
| DoD-1 | Cada feature retorna un float en [0,1] para entradas válidas. | Test unitario por feature. |
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

Basado en el dataset real (NEED-001 deserción):

| Candidato | sim_semantica | compat_metodo | compat_dominio | Resultado esperado |
|---|---|---|---|---|
| PRJ-004 (clasificación supervisada, permanencia↔attrition) | 0.88 | 0.90 | 0.95 | score alto · `antecedente_metodologico` |
| PRJ-007 (mismo tema, completado, menor soporte) | 0.88 | 0.60 | 0.80 | score medio |
| Tesis solo-tema, método distinto, campos vacíos | 0.85 | 0.20 | 0.50 | score bajo · `coincidencia_superficial` |

> Mismo `sim_semantica` ≈ 0.88 en los dos primeros, pero el método desempata. **Ese es el examen.**

### 9.1 Reproducción sobre datos reales (ADR-007)

El caso 9 hand-inyectaba métodos en el NEED, cosa que los datos reales no tienen. La variante reproducible parte de un NEED **sin método** y `problem_types=("prediccion",)` inferido del texto ("predicción y prevención"):

| Candidato | `compat_metodo` (fuente) | Resultado |
|---|---|---|
| PRJ-004 (`methods=clasificacion_supervisada`) | **0.90** por transferabilidad `prediccion→clasificacion_supervisada` | `score` alto · `antecedente_metodologico` |
| PRJ-007 (`methods=encuesta`) | **0.30** por transferabilidad `prediccion→encuesta` | `score` menor · `antecedente_relevante` |

> Verificado: PRJ-004 = 0.678 / `antecedente_metodologico`; PRJ-007 = 0.448. El método desempata **sin inventar método en el NEED**. Cubierto por `test_A_vs_B_need_transferabilidad_desempata`.
