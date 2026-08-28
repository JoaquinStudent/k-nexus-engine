# DESIGN.md — KNexus Engine

> **Herramienta de modelado:** Google Stitch (todos los mocks se generan aquí).
> **Uso:** copiar cada prompt tal cual en Stitch, generar, iterar. Un prompt = una pantalla/módulo.
> **Ley de marca (de `AGENTS.md`):** minimalista · alto contraste · azul oscuro base · tipografía Montserrat (Bold / Semi-Bold en encabezados).

---

## 0. Cómo usar este documento

| Paso | Acción |
|---|---|
| 1 | Abrir Google Stitch en modo **Text** (o Figma-to-Stitch si parten de un boceto). |
| 2 | Pegar el **Prompt Global de Estilo** (sección 3) como contexto base en cada sesión. |
| 3 | Pegar el prompt del módulo que toca (sección 5). Generar. |
| 4 | Iterar con los *refinamientos* listados bajo cada módulo. |
| 5 | Exportar a Figma/HTML y registrar el resultado en `MEMORY.md`. |

> **Regla de consistencia:** Stitch olvida contexto entre sesiones largas. Reinyectar el Prompt Global cada vez que se abra un módulo nuevo.

---

## 1. Dirección de diseño (el "porqué")

El producto conecta conocimiento fragmentado y **demuestra por qué** una conexión es relevante. El diseño debe transmitir **rigor y confianza**, no un dashboard genérico de startup. Decisiones:

| Decisión | Racional |
|---|---|
| Base azul-índigo profundo (`#251D4B`) | Autoridad académica, seriedad, alto contraste sobre fondos claros. Es tu color subido, ya casi azul-oscuro: encaja con la ley de marca sin traicionar tu paleta. |
| Lavandas como acentos (no como base) | Tus tres violetas quedan para estados, chips y datos, no para grandes áreas — así el índigo manda y la UI no se vuelve "pastel". |
| Montserrat en todo | Geométrica, legible, profesional. Bold/Semi-Bold en títulos; Regular/Medium en cuerpo. |
| Datos con color funcional propio | Un sistema con scores y grafos necesita verde/ámbar/rojo semánticos que 4 lavandas no dan. Se añaden abajo. |
| **Signature element** | El **"Relevance Breakdown Bar"**: la barra horizontal que descompone el score en sus 7 features. Es lo único que ningún competidor tendrá igual. Todo el diseño gira en torno a hacerla legible. |

---

## 2. Paleta completa (fusionada y extendida)

### 2.1 Marca — base y acentos (tu paleta)

| Token | Hex | Uso |
|---|---|---|
| `--brand-900` (base) | `#251D4B` | Fondo de barras laterales, headers, texto sobre claro, botones primarios. **Color ancla.** |
| `--brand-700` | `#3A2E6E` | Hover de primarios, bordes activos. *(derivado, aclarando el base)* |
| `--brand-500` | `#5B4F9E` | Enlaces, iconos activos. *(derivado)* |
| `--accent-blue` | `#CADFFD` | Chips informativos, fondos de tarjeta seleccionada, estado "neutral". *(tu #CADFFD)* |
| `--accent-lavender` | `#C3BEEF` | Aristas de grafo secundarias, badges de tipo de relación. *(tu #C3BEEF)* |
| `--accent-orchid` | `#CCA9E8` | Highlight de evidencia, resaltado de texto citado. *(tu #CCA9E8)* |

### 2.2 Neutros (añadidos — imprescindibles)

| Token | Hex | Uso |
|---|---|---|
| `--bg` | `#F7F8FC` | Fondo general de la app (casi blanco, frío, combina con índigo). |
| `--surface` | `#FFFFFF` | Tarjetas, paneles, modales. |
| `--border` | `#E4E7F0` | Divisores, bordes de tarjeta en reposo. |
| `--text-strong` | `#1A1533` | Titulares (variante aún más oscura del índigo). |
| `--text-body` | `#3D3A57` | Texto de cuerpo. |
| `--text-muted` | `#6E6B85` | Labels, captions, metadatos, procedencia. |

### 2.3 Semánticos de datos (añadidos — el sistema los necesita)

| Token | Hex | Significado en KNexus |
|---|---|---|
| `--rel-high` | `#2F9E6B` | Relevancia **alta** / conexión accionable / método compatible. |
| `--rel-mid` | `#E0A030` | Relevancia **media** / señal parcial. |
| `--rel-low` | `#C24D53` | Relevancia **baja** / `coincidencia_superficial` (la trampa). |
| `--evidence` | `#CCA9E8` | Marca de evidencia institucional verificable (reusa orchid). |
| `--generated` | `#8A86A6` | Marca de contenido generado por LLM (gris-violáceo: "esto NO es evidencia"). |

> **Regla de color semántico:** verde/ámbar/rojo NUNCA decoran; solo comunican nivel de relevancia. Evidencia (orchid) y Generado (gris) siempre visualmente distintos: es la separación evidencia-vs-generación que exige el reto.

### 2.4 Colores para el grafo (features de red)

| Token | Hex | Uso |
|---|---|---|
| `--node-need` | `#251D4B` | Nodo Necesidad (índigo, el origen). |
| `--node-project` | `#5B4F9E` | Nodo Proyecto. |
| `--node-thesis` | `#C3BEEF` | Nodo Tesis. |
| `--node-researcher`| `#CADFFD` | Nodo Investigador. |
| `--node-capability`| `#2FADB0` | Nodo Capacidad *(teal añadido para diferenciar del resto)*. |
| `--node-curricular`| `#CCA9E8` | Nodo Asignatura/Competencia. |
| `--node-research-group`| `#3A2E6E` | Nodo Grupo de investigación (vecino real vía `project_group`/`researcher_group`). |
| `--node-publication`| `#9C7A3C` | Nodo Publicación (vecino real vía `publication_researcher`/`publication_project`; tono cálido a propósito — todo lo demás es frío). |
| `--edge-explicit` | `#3D3A57` | Arista explícita (viene de tabla de relación) — sólida. |
| `--edge-inferred` | `#C3BEEF` | Arista inferida (descubierta) — punteada. |

---

## 3. Prompt Global de Estilo (pegar en CADA sesión de Stitch)

```
STYLE SYSTEM — reuse for every screen of this app.

Product: "KNexus Engine", an academic knowledge-connection tool for a university.
Serious, trustworthy, data-dense but calm. NOT a generic pastel startup dashboard.

Typography: Montserrat everywhere.
- Headings: Montserrat Bold and SemiBold, tight letter-spacing.
- Body: Montserrat Regular / Medium.
- Data & captions: Montserrat Medium, slightly smaller, muted color.

Color palette (use exactly these):
- Base / primary: deep indigo #251D4B (headers, sidebars, primary buttons, strong text)
- Primary hover: #3A2E6E ; links/icons: #5B4F9E
- Accents: soft blue #CADFFD, lavender #C3BEEF, orchid #CCA9E8 (chips, badges, highlights — NEVER large fills)
- App background: #F7F8FC ; surfaces/cards: #FFFFFF ; borders/dividers: #E4E7F0
- Text: strong #1A1533, body #3D3A57, muted #6E6B85
- Relevance semantics: high = green #2F9E6B, medium = amber #E0A030, low = red #C24D53
- Evidence tag = orchid #CCA9E8 ; AI-generated tag = grey-violet #8A86A6

Layout language: minimalist, high contrast, generous white space, 8px spacing grid,
12px card radius, subtle 1px borders (#E4E7F0), soft shadow only on modals.
No gradients on large areas. No drop shadows on flat cards. Flat, precise, editorial.

Tone of copy: plain, active voice, sentence case. Never salesy.
```

---

## 4. Inventario de módulos a modelar

| # | Módulo | Capa de arquitectura | Prioridad demo |
|---|---|---|---|
| M1 | Pantalla de Consulta (Query) | Interface → entrada al pipeline | ★★★ |
| M2 | Resultados: lista de conexiones rankeadas | F3+F4 | ★★★ |
| M3 | Detalle de Conexión + **Relevance Breakdown** (signature) | F4 | ★★★ |
| M4 | Panel de Evidencia y Procedencia | F6 | ★★★ |
| M5 | Vista de Oportunidad (cadena ensamblada) | F5 | ★★ |
| M6 | Grafo interactivo de conocimiento | F2/F5 | ★★ |
| M7 | Auditoría "¿por qué A antes que B?" (comparador) | validación en vivo | ★★★ |
| M8 | Dashboard de métricas (Precision@K + ablation) | F7/evidencia | ★ |
| M9 | Estados: vacío, cargando, error, sin-resultados | transversal | ★ |

---

## 5. Prompts por módulo (Google Stitch)

> Cada prompt asume que el **Prompt Global (sección 3)** ya está en contexto.

### M1 — Pantalla de Consulta

```
Screen: "Query / Discover".
A centered, calm search-first screen. Large Montserrat Bold H1: "Discover connections".
Sub-line muted: "Enter an institutional need, an entity ID, or free text."
A single prominent search input (rounded 12px, 1px #E4E7F0 border, white).
Primary button indigo #251D4B labelled "Discover".
Below the input: three quick-pick chips in soft blue #CADFFD:
"NEED-001 Deserción", "NEED-005 Cardiovascular", "NEED-009 Calidad del agua".
Left vertical sidebar in deep indigo #251D4B with small Montserrat SemiBold nav:
Discover · Results · Graph · Metrics. Active item highlighted lavender.
Lots of white space. No hero image. Editorial, precise.
```
*Refinamientos:* añadir un toggle "Explainer: AI / Template" arriba a la derecha; añadir contador "1.987 entities · 3 sources connected".

---

### M2 — Resultados (lista rankeada)

```
Screen: "Results — ranked connections".
Top: the query echoed in a slim bar ("Results for: NEED-001 · Deserción estudiantil").
A vertical list of result cards (white, 12px radius, 1px border).
Each card shows, left to right:
- a rank number in Montserrat Bold (01, 02, 03…),
- entity title + entity type badge (lavender chip, e.g. "PROJECT PRJ-004"),
- a RELEVANCE PILL on the right: green #2F9E6B "High", amber #E0A030 "Medium", red #C24D53 "Low",
- under the title, a thin horizontal "relevance breakdown" mini-bar split into 7 colored segments.
- a one-line reason in muted text: "Transferable method + exact domain + capability available".
Sorting control top-right: "Sort by relevance ▼".
Make relevance the loudest visual signal, not similarity.
```
*Refinamientos:* estado de card seleccionada con fondo `#CADFFD` al 30%; mostrar el score numérico pequeño junto al pill (ej. "0.87") pero secundario.

---

### M3 — Detalle de Conexión + Relevance Breakdown (SIGNATURE)

```
Screen: "Connection detail" — this is the signature screen, make it excellent.
Two-column layout.
LEFT (source→target): two entity cards stacked with an arrow between them:
"NEED-001 Deserción" → "PRJ-004 Clasificación supervisada".
A badge shows the relation type: "Antecedente metodológico" (lavender #C3BEEF).
RIGHT: the RELEVANCE BREAKDOWN BAR — the hero of the whole product.
A large horizontal stacked bar, full width, split into 7 labelled segments,
each a different width = its weighted contribution:
compat_metodo, compat_dominio, sim_semantica, soporte_capacidad,
densidad_evidencia, enlace_estructural, sim_lexica.
Each segment labelled with its value (0–1) in small Montserrat Medium.
Above the bar, the final score big: "Relevance 0.87" in Montserrat Bold indigo.
Below: a plain-language sentence explaining why, with an "Evidence" tag (orchid) and,
if AI-written, a small grey-violet "AI-generated" tag to separate it from evidence.
Keep everything else quiet so the breakdown bar dominates.
```
*Refinamientos:* al hover sobre un segmento, tooltip con el campo fuente (ej. `PRJ-004.methodology`); segmentos de features "débiles" (sim_lexica) en tono apagado para reforzar el mensaje "no premiamos la trampa".

---

### M4 — Evidencia y Procedencia

```
Screen: "Evidence & provenance".
A right-hand drawer or panel titled "Why we trust this".
List of evidence items, each a small card:
- the quoted field content (short), highlighted with orchid #CCA9E8 left border,
- below it, the provenance trail in muted mono-ish Montserrat Medium:
  "Data V1.0 / project_profile_004.md / methodology".
Clear visual separation between two groups with header labels:
"● Institutional evidence" (orchid dot) and "● AI-generated summary" (grey-violet dot).
A caption reminds: "AI text never counts as evidence."
Clean, legal-document calm. High contrast, no clutter.
```
*Refinamientos:* botón "Copy provenance"; icono de archivo por tipo de fuente (CSV vs MD).

---

### M5 — Vista de Oportunidad

```
Screen: "Opportunity".
Show an assembled opportunity as a horizontal chain of linked nodes:
NEED → ANTECEDENT (project/thesis) → RESEARCHER → CAPABILITY → CURRICULAR component → OPPORTUNITY.
Each step is a small pill-node with an icon, connected by arrows.
Node colors follow the graph palette (need indigo, project #5B4F9E, thesis lavender,
researcher soft-blue, capability teal #2FADB0, curricular orchid).
Below the chain: an opportunity card with:
- opportunity type badge (e.g. "RESEARCH_CONTINUITY", "CAPABILITY_ACTIVATION"),
- a short plain-language description,
- a priority tag (High/Medium/Low using the relevance semantic colors),
- an "Evidence" row linking back to the sources.
Make the chain feel like a reasoning path, left to right.
```
*Refinamientos:* permitir colapsar la cadena a "resumen" vs "detalle"; mostrar múltiples oportunidades como tabs.

---

### M6 — Grafo interactivo

```
Screen: "Knowledge graph".
Full-canvas interactive node-link graph on background #F7F8FC.
Nodes colored by type (need indigo #251D4B, project #5B4F9E, thesis #C3BEEF,
researcher #CADFFD, capability teal #2FADB0, curricular #CCA9E8).
Edges: explicit relations solid dark #3D3A57; inferred/discovered relations dashed lavender #C3BEEF.
A legend top-right maps color→entity type and solid/dashed→explicit/inferred.
Left filter panel (indigo sidebar) with checkboxes to toggle entity types and
a slider "min relevance". Clicking a node opens a side panel with its detail.
Calm, lots of space, not a hairball — show a focused subgraph of ~12 nodes.
```
*Refinamientos:* botón "focus on NEED-001"; animación suave al expandir vecinos; evitar saturación (máx. 15 nodos visibles).

---

### M7 — Comparador "¿por qué A antes que B?" (auditoría en vivo)

```
Screen: "Why A over B — audit".
Side-by-side comparison of two candidate connections for the same query.
Two columns, each with the entity title and its RELEVANCE BREAKDOWN BAR (7 segments),
aligned so segments line up row-by-row for direct comparison.
A middle column of feature labels so both bars read against the same rows.
Where A beats B on a feature, subtly mark A's segment with a green #2F9E6B tick;
where B is weaker, mark it muted. Bottom line, Montserrat SemiBold:
"PRJ-004 ranks higher: same topic, but transferable method + available capability."
This screen must let a judge instantly see the reason. Clarity over decoration.
```
*Refinamientos:* este es el módulo clave para la defensa ante el jurado — priorizar legibilidad de la comparación fila-por-fila sobre cualquier adorno.

---

### M8 — Dashboard de métricas (Precision@K + ablation)

```
Screen: "Performance".
Two clean bar-chart cards on white surfaces:
1) "Precision@K" with bars for P@5 and P@10.
2) "Ablation: cosine-only vs full reranker" — grouped bars showing the reranker
   beats cosine-only, with the delta highlighted in green #2F9E6B.
Above: three stat tiles (Montserrat Bold numbers, muted labels):
"Entities indexed", "Avg latency", "Evidence coverage %".
Minimal axis lines, indigo bars, no 3D, no gradient. Data-journalism calm.
Caption under ablation: "Similarity ≠ relevance, measured."
```
*Refinamientos:* mantener sobrio; el mensaje del ablation es la estrella, no la cantidad de gráficos.

---

### M9 — Estados (vacío, cargando, error, sin resultados)

```
Screens: system states, all in the same minimalist indigo/Montserrat system.
1) Empty (before first query): centered muted illustration-free message
   "Start by entering a need or an entity ID." with the quick-pick chips.
2) Loading: a slim indeterminate progress bar in lavender #C3BEEF, plus text
   "Connecting sources…". No spinner circus.
3) No results: "No connections passed the relevance threshold. Try lowering min relevance."
   with a clear action button.
4) Error / API down: "AI explainer is offline — showing template explanations instead."
   in amber #E0A030, reinforcing graceful degradation. System still usable.
All copy in active voice, sentence case, never apologetic-vague.
```
*Refinamientos:* el estado de error debe transmitir que el sistema sigue funcionando sin la IA (mensaje clave del reto).

---

## 6. Checklist de consistencia (antes de exportar de Stitch)

| # | Verificación | OK |
|---|---|---|
| C1 | Todos los encabezados en Montserrat Bold/SemiBold. | ☐ |
| C2 | Índigo `#251D4B` manda; lavandas solo en acentos, nunca en grandes áreas. | ☐ |
| C3 | Relevancia siempre con verde/ámbar/rojo; nunca decorativos. | ☐ |
| C4 | Evidencia (orchid) y Generado (gris) visualmente separados en toda pantalla. | ☐ |
| C5 | El Relevance Breakdown Bar es el elemento más prominente de M3 y M7. | ☐ |
| C6 | Copy en voz activa, sentence case, sin tono de venta. | ☐ |
| C7 | Contraste AA en texto sobre índigo y sobre claro. | ☐ |
| C8 | Estados de error comunican degradación elegante (sistema sigue vivo). | ☐ |

---

## 7. Mapa módulo → entregable del reto

| Módulo | Entregable / criterio que sustenta |
|---|---|
| M2, M3, M7 | Calidad y pertinencia de conexiones · Priorización · Explicabilidad |
| M4 | Trazabilidad · separación evidencia/generación |
| M5, M6 | Generación de oportunidades · Representación del conocimiento |
| M8 | Evidencia de desempeño · Validación técnica |
| M1, M9 | Funcionamiento del prototipo · robustez |
