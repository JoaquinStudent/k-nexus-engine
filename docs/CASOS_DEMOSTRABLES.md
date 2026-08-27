# Casos demostrables — KNexus Engine

> Entregable técnico oficial (`GUIA_OFICIAL_PARTICIPANTES...md §8`, `DOCUMENTO_TECNICO.md §10`).
> Estructura exigida: **elementos involucrados → relación identificada → evidencia que la sustenta →
> valoración de pertinencia → oportunidad generada → explicación del resultado.**
>
> **Los tres casos de abajo son la salida REAL del sistema**, capturada el 2026-08-27 con el modelo real
> (`paraphrase-multilingual-MiniLM-L12-v2`, sin `--fast`), no texto redactado a mano (R7 de
> `sdd/AGENTS.md`: nada se documenta que no se haya corrido). Reproducibles tal cual desde `knexus/`:
>
> ```bash
> PYTHONIOENCODING=utf-8 python scripts/query_cli.py "<consulta>" --top 3 [--compare ID] [--opportunity]
> ```
> (`PYTHONIOENCODING=utf-8` evita que Windows corrompa los acentos al redirigir la salida a un archivo —
> ver "Nota de reproducibilidad" al final de este documento.)

---

## Caso A — Antecedente + comparador "¿por qué A antes que B?"

**Consulta:** `NEED-001` (necesidad institucional real del dataset: *predicción y prevención de deserción
estudiantil*).

**Comando:** `python scripts/query_cli.py "NEED-001" --compare PRJ-002 --top 3`

| Componente | Respuesta |
|---|---|
| **Origen** | `NEED-001` — necesidad institucional. |
| **Destino** | `PRJ-007` (mejor resultado, rank #1). |
| **Tipo de relación** | `antecedente_metodologico` — el proyecto aporta un método transferible al problema de la necesidad (ADR-007). |
| **Relevancia** | score `0.657` (banda "alta", `domain/opportunity.py:ALTO=0.6`). |
| **Evidencia** | `03_knowledge_needs_projects.csv` · campo `keywords` · `PRJ-007`: *"riesgo académico;clasificación supervisada;student attrition"*. |
| **Procedencia** | archivo + registro + campo, verificable en `/connection/PRJ-007?q=NEED-001` de la interfaz. |
| **Explicación** | `compat_metodo=0.90` y `soporte_capacidad=1.00` dominan el score; `sim_semantica=0.69` confirma además cercanía temática — no es sólo una coincidencia léxica. |

Salida real (top-3 + comparador):

```
=== Consulta: 'NEED-001' ===
[62 resultados en 0.467s]

#1   PRJ-007    score=0.657  antecedente_metodologico
      evidencia: 03_knowledge_needs_projects.csv · keywords
      "riesgo académico;clasificación supervisada;student attrition"
      features: compat_metodo=0.90, soporte_capacidad=1.00, sim_semantica=0.69

#2   PRJ-001    score=0.655  antecedente_metodologico
      evidencia: 03_knowledge_needs_projects.csv · keywords
      "permanencia estudiantil;clasificación supervisada;trayectorias educativas"
      features: compat_metodo=0.90, soporte_capacidad=1.00, sim_semantica=0.67

#3   PRJ-004    score=0.652  antecedente_metodologico
      evidencia: project_profile_004.md · expected_results
      "Se esperan relaciones priorizadas, evidencia reproducible y orientaciones para decisiones relacionad..."
      features: compat_metodo=0.90, soporte_capacidad=1.00, sim_semantica=0.66

=== ¿Por qué PRJ-007 antes que PRJ-002? ===
delta de score: +0.188 · feature dominante: soporte_capacidad
  soporte_capacidad    A=1.0  B=0.0  delta=+0.150  favorece=A
  compat_metodo        A=0.9  B=0.7  delta=+0.040  favorece=A
  sim_semantica        A=0.6851376295089722  B=0.6949293613433838  delta=-0.002  favorece=B
  compat_dominio       A=0.5  B=0.5  delta=+0.000  favorece=empate
  densidad_evidencia   A=0.8666666666666667  B=0.8666666666666667  delta=+0.000  favorece=empate
  enlace_estructural   A=0.0  B=0.0  delta=+0.000  favorece=empate
  sim_lexica           A=0.0  B=0.0  delta=+0.000  favorece=empate
```

**Qué demuestra:** una conexión no trivial entre fuentes distintas (necesidad ↔ proyecto), con evidencia
verificable campo-por-campo, y el requisito explícito de la guía — *"¿por qué A aparece antes que B?"*
(`DOCUMENTO_TECNICO.md §6`) — respondido con el delta EXACTO por feature, no con una frase vaga. Nótese
que `PRJ-007` gana a pesar de tener `sim_semantica` ligeramente menor que `PRJ-002` — el sistema no
rankea por coseno crudo (R6): `soporte_capacidad` (capacidad institucional real disponible) es la
feature dominante del delta.

---

## Caso B — Cadena de oportunidad completa, segundo dominio

**Consulta:** `NEED-009` (necesidad real: *monitoreo inteligente de calidad del agua*) — dominio
completamente distinto al Caso A, para descartar sobreajuste a "deserción estudiantil".

**Comando:** `python scripts/query_cli.py "NEED-009" --opportunity --top 3`

| Componente | Respuesta |
|---|---|
| **Elementos involucrados** | `NEED-009` → `PRJ-068` (antecedente) → `INV-132` (investigador) → `CAP-003` (capacidad) → `SUB-099` (asignatura). |
| **Relación** | `continuidad_investigativa` — cadena necesidad→antecedente→investigador→capacidad→currículo (F5 de `ARCHITECTURE.md`). |
| **Evidencia** | `03_knowledge_needs_projects.csv` · campo `expected_results` para el antecedente; cada eslabón siguiente trae su propia procedencia. |
| **Pertinencia** | score del antecedente `0.598`, prioridad "media". |
| **Oportunidad** | continuidad investigativa: el proyecto antecedente tiene un investigador con capacidad institucional real y un componente curricular articulable. |
| **Explicación** | generada por `TemplateExplainer`, grounding verificado — cada frase cita sólo IDs que están en la cadena. |

Salida real (top-3 + primera cadena de oportunidad):

```
=== Consulta: 'NEED-009' ===
[72 resultados en 0.473s]

#1   PRJ-068    score=0.598  antecedente_metodologico
      evidencia: 03_knowledge_needs_projects.csv · expected_results
      "Se esperan relaciones priorizadas, evidencia reproducible y orientaciones para decisiones relacionad..."
      features: soporte_capacidad=1.00, compat_metodo=0.70, sim_semantica=0.75

=== Cadena(s) de oportunidad ===

  tipo=continuidad_investigativa  prioridad=media  score=0.598
  cadena: necesidad:NEED-009[retrieved] -> antecedente:PRJ-068[retrieved] -> investigador:INV-132[edge] -> capacidad:CAP-003[inferred] -> curriculo:SUB-099[edge]
  explicación: Oportunidad de continuidad investigativa para NEED-009 (prioridad media, score del antecedente 0.60): necesidad NEED-009 [recuperado por búsqueda y puntuado] -> antecedente PRJ-068 [recuperado por búsqueda y puntuado] -> investigador INV-132 [vínculo verificado en los datos] -> capacidad institucional CAP-003 [inferido por reglas explícitas] -> componente curricular SUB-099 [vínculo verificado en los datos].
```

**Qué demuestra:** la cadena completa que pide `DOCUMENTO_TECNICO.md §7` (necesidad → antecedente →
investigador → capacidad → currículo → oportunidad), en un dominio (calidad del agua) distinto al de
todos los ejemplos de `sdd/DESIGN.md` — sin ajustes específicos para este caso. Nótese que cada eslabón
declara su `link_type` entre corchetes (`[retrieved]`/`[edge]`/`[inferred]`, ADR-012): el investigador
y el currículo son **hechos duros** (aristas reales de `researcher_project.csv`/FK de programa), la
capacidad es **inferida** por regla explícita (ADR-008, sin tabla de enlace en el dataset) — los tres no
se presentan como si tuvieran la misma fuerza probatoria.

---

## Caso C — Consulta nueva en texto libre, cruzando idioma

**Consulta:** texto libre en **inglés**, escrito para este documento, que **no existe literalmente en
ningún registro del dataset**: *"predicting which university students are likely to drop out before it
is too late"*.

**Comando:** `python scripts/query_cli.py "predicting which university students are likely to drop out before it is too late" --top 3`

| Componente | Respuesta |
|---|---|
| **Origen** | texto libre en inglés, sin ID de entidad — el sistema lo trata como una necesidad inferida (`query_builder.py:_from_free_text`). |
| **Destino** | `PRJ-001` — *"Análisis aplicado de permanencia estudiantil..."* (título en **español**). |
| **Tipo de relación** | `activacion_capacidad` — sin método declarado en el texto libre, el sistema no fuerza `antecedente_metodologico`; tipa honestamente por la capacidad institucional disponible. |
| **Relevancia** | score `0.757` — la más alta de los tres casos. |
| **Evidencia** | `03_knowledge_needs_projects.csv` · campo `title`. |
| **Explicación** | `sim_semantica=0.56` conecta el inglés de la consulta con el español del título vía el modelo multilingüe — sin traducir nada explícitamente. |

Salida real:

```
=== Consulta: 'predicting which university students are likely to drop out before it is too late' ===
[65 resultados en 0.109s]

#1   PRJ-001    score=0.757  activacion_capacidad
      evidencia: 03_knowledge_needs_projects.csv · title
      "Análisis aplicado de permanencia estudiantil para fortalecer trayectorias educativas"
      features: soporte_capacidad=1.00, densidad_evidencia=0.87, sim_semantica=0.56

#2   PRJ-007    score=0.598  activacion_capacidad
      evidencia: 03_knowledge_needs_projects.csv · title
      "Integración de evidencia sobre riesgo académico en escenarios de student attrition"
      features: soporte_capacidad=1.00, sim_semantica=0.58, densidad_evidencia=0.87

#3   PRJ-004    score=0.590  activacion_capacidad
      evidencia: project_profile_004.md · institutional_context
      "permanencia estudiantil"
      features: soporte_capacidad=1.00, densidad_evidencia=0.87, sim_semantica=0.56
```

**Qué demuestra:** el requisito que la guía marca como falla técnica grave si no se cumple —
*"depender de ejemplos precargados que no responden ante nuevas consultas"* (`DOCUMENTO_TECNICO.md
§11`) y el checklist §11: *"¿podemos responder a una consulta nueva sin depender de respuestas
precargadas?"*. Esta consulta se escribió para este documento y nunca fue vista por el pipeline antes de
esta corrida; responde en 0.109s con conexiones pertinentes cruzando inglés→español.

---

## Nota de reproducibilidad

Estos tres comandos fueron ejecutados desde `knexus/` con un entorno virtual limpio en ruta corta
(ver `README.md §Instalación`), con el modelo real descargado (no `--fast`). En Windows, la consola por
defecto usa `cp1252` al redirigir salida a archivo — los acentos se corrompen (visualmente, no crashea:
lección L8 de `sdd/MEMORY.md`) salvo que se fije `PYTHONIOENCODING=utf-8`, como en los comandos de
arriba.

Los mismos tres resultados son navegables en la interfaz web (`uvicorn src.interface.app:app`, ver
`README.md`): `/results?q=NEED-001`, `/opportunity?q=NEED-009`, `/results?q=predicting...` — con el
panel de score desglosado, el mini-grafo y la procedencia visibles en pantalla, no sólo en el CLI.
