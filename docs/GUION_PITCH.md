# Guion de pitch — KNexus Engine

> Cronometrado a **3:00 min exactos**. Texto para decir en voz alta, no para leer — memorizar la idea de cada
> slide, no la frase literal. 5 slides: los primeros 30s son el problema, los siguientes 30s la solución en
> frases cortas, dos slides de sustento (arquitectura y resultados/evolución), y el quinto slide es la demo en
> vivo. El paso a paso de clics de la demo está al final.

| Slide | Contenido | Tiempo | Duración |
|---|---|---|---|
| 1 | Problema | 0:00 – 0:30 | 30s |
| 2 | Solución | 0:30 – 1:00 | 30s |
| 3 | Arquitectura y enfoque técnico | 1:00 – 1:35 | 35s |
| 4 | Resultados, métricas e impacto | 1:35 – 2:05 | 30s |
| 5 | Demo funcional (en vivo) | 2:05 – 3:00 | 55s |

---

## Slide 1 — Problema (0:00 – 0:30)

> Las universidades producen conocimiento sin parar: proyectos, tesis, investigadores, capacidades. Pero vive
> repartido entre facultades y sistemas que no se hablan entre sí. Buscar por palabra clave no basta — devuelve
> parecido, no relevancia. Y sin evidencia verificable detrás, no se puede confiar en la conexión.

**Recomendación de imagen:** algo que muestre fragmentación, no una foto genérica de estudiantes. Por ejemplo:
un diagrama simple de "islas" — facultades/sistemas representados como nodos aislados, con líneas punteadas o
cortadas entre ellos (contraste directo con el grafo conectado que aparece en el Slide 3). También funciona un
mosaico de capturas de hojas de cálculo/PDFs sueltos con una "X" o candado entre ellos, comunicando "esto no se
habla entre sí".

---

## Slide 2 — Solución (0:30 – 1:00)

> KNexus Engine descubre, prioriza y explica esas conexiones. Recuperación híbrida — semántica, léxica y de
> grafo — más un reranking de 7 features auditables, nunca coseno puro. Cada conexión trae su evidencia
> literal, con archivo y campo de origen. Nunca la inventa.

**Recomendación de imagen:** el mismo diagrama de "islas" del Slide 1 pero ahora CONECTADO — nodos unidos por
líneas sólidas con una etiqueta de score o un ícono de "evidencia verificada" (check + documento) sobre una de
las aristas. Es el antes/después visual más directo del pitch. Si hay tiempo de diseño, usar el logo/nombre
"KNexus Engine" como ancla del slide.

---

## Slide 3 — Arquitectura y enfoque técnico (1:00 – 1:35)

> Pipeline de 8 filtros sobre arquitectura hexagonal: dominio puro en el centro, todo depende hacia adentro.
> Cargamos 22 tablas y 60 documentos sin perder procedencia. La recuperación combina denso, léxico y grafo —
> porque un investigador rara vez comparte vocabulario con una necesidad, lo trae la arista, no el texto. El
> corazón es el reranking: 7 features ponderadas, nunca coseno puro. Y la explicación por IA es opcional: sin
> red, degrada sola a plantillas.

**Recomendación de imagen:** el diagrama de arquitectura/pipeline de `sdd/ARCHITECTURE.md` simplificado a un
esquema de cajas y flechas (8 filtros en fila, dominio hexagonal al centro) — evitar meter el diagrama completo
y denso del documento técnico, usar una versión limpia con 5-6 cajas máximo. Si no hay tiempo de rediseñarlo,
la captura `mocks-stitch/knowledge_graph_knexus_engine/screen.png` sirve como apoyo visual del grafo real.

---

## Slide 4 — Resultados, métricas e impacto (1:35 – 2:05)

> Medido, no sólo mostrado. Sobre 2.512 entidades y 20 necesidades etiquetadas, el pipeline real sube la tasa
> de conexiones accionables del top-5 a **0.55** contra **0.27** del coseno puro, y baja las coincidencias
> superficiales de 0.65 a 0.28. Y cada pieza vive detrás de un puerto: cambiar el embedding o el repositorio de
> datos es una línea de código, no una reescritura — listo para pasar de un dataset sintético a un ecosistema
> universitario real.

**Recomendación de imagen:** un gráfico de barras simple comparando dos métricas por brazo (`full` vs
`cosine`): `actionable_rate` (0.55 vs 0.27) y `trap_rate` (0.28 vs 0.65) — dos pares de barras, colores
semánticos (verde=bueno, rojo=trampa). Es el dato más fuerte del proyecto, merece su propio gráfico y no un
texto suelto. La captura `mocks-stitch/performance_knexus_engine/screen.png` puede usarse como referencia de
estilo o directamente como imagen de apoyo.

---

## Slide 5 — Demo funcional en vivo (2:05 – 3:00)

> Consulta en vivo, un ID real del dataset, nada precargado.

Recorrido de 4 pantallas (detalle de clics en la sección **Paso a paso** más abajo):

1. **Descubrir** (`/`) → escribo `NEED-001`.
2. **Resultados** (`/results?q=NEED-001`) → PRJ-007 arriba, score 0.657, barra de 7 features.
3. **Conexión** (`/connection/PRJ-007?q=NEED-001`) → evidencia literal + procedencia exacta.
4. **Auditoría** (`/audit?q=NEED-001&a=PRJ-007&b=PRJ-002`) → por qué PRJ-007 gana, delta por feature.

> Y esto no es un truco para "deserción estudiantil": *(flash rápido)* `NEED-009` es calidad del agua, dominio
> totalmente distinto, con la cadena completa necesidad→antecedente→investigador→capacidad→currículo.

**Recomendación de imagen:** este slide no necesita imagen propia si la demo es en vivo (navegador compartido).
Como respaldo por si falla la red/proyección, dejar como slide oculto (o como imagen de transición) las
capturas reales ya generadas en `mocks-stitch/`, en este orden:
- `query_discover_knexus_engine/screen.png` (pantalla 1)
- `results_ranked_connections_knexus_engine/screen.png` (pantalla 2)
- `connection_detail_knexus_engine/screen.png` + `evidence_provenance_knexus_engine/screen.png` (pantalla 3)
- `why_a_over_b_audit_knexus_engine/screen.png` (pantalla 4)
- `opportunity_knexus_engine/screen.png` (paso 5 opcional, NEED-009)

Son capturas reales de la interfaz (no mockups genéricos), así que sirven tanto de respaldo como de imagen de
apoyo si se decide no compartir pantalla en vivo.

---

## Paso a paso por pantalla (para el Slide 5)

| # | Pantalla | Acción | Qué decir | Qué señalar |
|---|---|---|---|---|
| 1 | `/` Descubrir | Escribir `NEED-001`, clic en Descubrir | "Necesidad institucional real del dataset — predicción y prevención de deserción estudiantil." | Contador "2.512 entidades indexadas" |
| 2 | `/results?q=NEED-001` | — | "62 resultados en menos de medio segundo. Cada tarjeta ya trae su barra de 7 features — no es una lista por parecido de texto. PRJ-007 arriba, score 0.657, banda alta." | Mini-barra de la tarjeta #1, pill "Alta" |
| 3 | `/connection/PRJ-007?q=NEED-001` | Clic en la tarjeta #1 | "Método transferible 0.90, capacidad institucional 1.00 dominan. Y la evidencia es la cita literal, con archivo, campo y registro — nada se fabrica." | Barra desglosada + leyenda, bloque de evidencia, mini-grafo |
| 4 | `/audit?q=NEED-001&a=PRJ-007&b=PRJ-002` | Clic en "Comparar con…" | "PRJ-007 gana por soporte de capacidad, +0.15, aun con similitud semántica levemente menor. El sistema no cae en la trampa léxica." | Fila `soporte_capacidad` con check a favor de A, delta al pie |
| 5 | `/opportunity?q=NEED-009` | — | "Dominio distinto — calidad del agua. Cadena completa: necesidad, antecedente, investigador, capacidad, currículo. Cada eslabón etiquetado como recuperado, arista real o inferido." | Etiquetas `[retrieved]/[edge]/[inferred]` bajo cada nodo |

*(Paso 5 es opcional si el tiempo del Slide 5 se ajustó bien — úsalo solo si van sobrados de segundos.)*

---

## Plan B si falla el navegador o la red

```bash
python scripts/query_cli.py "NEED-001" --compare PRJ-002 --top 3
```

Mismo dato, sin depender de la demo web. Si el modelo real no llegó a descargarse, `--fast` da resultados
instantáneos (aclarándolo en voz alta si se usa). La salida literal de los tres casos, capturada de una
corrida real, está en [`docs/CASOS_DEMOSTRABLES.md`](CASOS_DEMOSTRABLES.md).
