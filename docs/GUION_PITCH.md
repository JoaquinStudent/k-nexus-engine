# Guion de pitch — KNexus Engine

> Cronometrado a **3:00 min exactos**. Texto para decir en voz alta, no para leer — memorizar la idea de cada
> acto, no la frase literal. El paso a paso de clics de la demo está al final.

| Acto | Tiempo | Duración |
|---|---|---|
| 1. Problema | 0:00 – 0:20 | 20s |
| 2. Arquitectura y enfoque | 0:20 – 1:15 | 55s |
| 3. Demo funcional | 1:15 – 2:10 | 55s |
| 4. Resultados y métricas | 2:10 – 2:35 | 25s |
| 5. Impacto y evolución | 2:35 – 3:00 | 25s |

---

## 1. Problema (0:00 – 0:20)

> Las universidades producen conocimiento sin parar — proyectos, tesis, investigadores, capacidades — pero
> vive repartido entre facultades y sistemas que no se hablan. No hace falta otro buscador de palabras clave:
> hace falta poder **confiar** en la conexión. KNexus Engine descubre, prioriza y explica esas conexiones con
> evidencia verificable — nunca las inventa.

---

## 2. Arquitectura y enfoque técnico (0:20 – 1:15)

> Pipeline de 8 filtros sobre arquitectura hexagonal: dominio puro en el centro, todo depende hacia adentro.
> Cargamos 22 tablas y 60 documentos sin perder procedencia — archivo, registro y campo de origen. La
> recuperación es híbrida: denso con FAISS, léxico con BM25, fusionados por RRF, más expansión por vecinos del
> grafo, porque un investigador rara vez comparte vocabulario con una necesidad — lo trae la arista, no el
> texto. El corazón es el reranking: 7 features ponderadas, auditables, nunca coseno puro. Cada eslabón de una
> oportunidad declara si es un dato recuperado, una arista real o una inferencia. Y la explicación por IA es
> opcional: sin la API de Claude, degrada sola a plantillas — la demo nunca depende de la red.

---

## 3. Demo funcional (1:15 – 2:10)

> Consulta en vivo, un ID real del dataset, nada precargado.

Recorrido de 4 pantallas (detalle de clics en la sección **Paso a paso** más abajo):

1. **Descubrir** (`/`) → escribo `NEED-001`.
2. **Resultados** (`/results?q=NEED-001`) → PRJ-007 arriba, score 0.657, barra de 7 features.
3. **Conexión** (`/connection/PRJ-007?q=NEED-001`) → evidencia literal + procedencia exacta.
4. **Auditoría** (`/audit?q=NEED-001&a=PRJ-007&b=PRJ-002`) → por qué PRJ-007 gana, delta por feature.

> Y esto no es un truco para "deserción estudiantil": *(flash rápido)* `NEED-009` es calidad del agua, dominio
> totalmente distinto, con la cadena completa necesidad→antecedente→investigador→capacidad→currículo.

---

## 4. Resultados y métricas (2:10 – 2:35)

> Medido, no sólo mostrado. Sobre 2.512 entidades y 20 necesidades etiquetadas, el pipeline real sube la tasa
> de conexiones accionables del top-5 a **0.55** contra **0.27** del coseno puro, y baja las coincidencias
> superficiales de **0.65** a **0.28**. 174 tests, incluido uno que verifica que ningún ID o cifra de una
> explicación de IA puede faltar en el dato que la sustenta.

---

## 5. Impacto y evolución (2:35 – 3:00)

> Cada pieza vive detrás de un puerto: cambiar el embedding a bge-m3, o el repositorio de CSV a una base de
> datos institucional real, es una línea de código, no una reescritura. La arquitectura ya está lista para
> pasar de un dataset sintético a un ecosistema universitario real — sin tocar el dominio que decide qué
> conexión es relevante y por qué.

---

## Paso a paso por pantalla (para el Acto 3)

| # | Pantalla | Acción | Qué decir | Qué señalar |
|---|---|---|---|---|
| 1 | `/` Descubrir | Escribir `NEED-001`, clic en Descubrir | "Necesidad institucional real del dataset — predicción y prevención de deserción estudiantil." | Contador "2.512 entidades indexadas" |
| 2 | `/results?q=NEED-001` | — | "62 resultados en menos de medio segundo. Cada tarjeta ya trae su barra de 7 features — no es una lista por parecido de texto. PRJ-007 arriba, score 0.657, banda alta." | Mini-barra de la tarjeta #1, pill "Alta" |
| 3 | `/connection/PRJ-007?q=NEED-001` | Clic en la tarjeta #1 | "Método transferible 0.90, capacidad institucional 1.00 dominan. Y la evidencia es la cita literal, con archivo, campo y registro — nada se fabrica." | Barra desglosada + leyenda, bloque de evidencia, mini-grafo |
| 4 | `/audit?q=NEED-001&a=PRJ-007&b=PRJ-002` | Clic en "Comparar con…" | "PRJ-007 gana por soporte de capacidad, +0.15, aun con similitud semántica levemente menor. El sistema no cae en la trampa léxica." | Fila `soporte_capacidad` con check a favor de A, delta al pie |
| 5 | `/opportunity?q=NEED-009` | — | "Dominio distinto — calidad del agua. Cadena completa: necesidad, antecedente, investigador, capacidad, currículo. Cada eslabón etiquetado como recuperado, arista real o inferido." | Etiquetas `[retrieved]/[edge]/[inferred]` bajo cada nodo |

*(Paso 5 es opcional si el tiempo del Acto 3 se ajustó bien — úsalo solo si van sobrados de segundos.)*

---

## Plan B si falla el navegador o la red

```bash
python scripts/query_cli.py "NEED-001" --compare PRJ-002 --top 3
```

Mismo dato, sin depender de la demo web. Si el modelo real no llegó a descargarse, `--fast` da resultados
instantáneos (aclarándolo en voz alta si se usa). La salida literal de los tres casos, capturada de una
corrida real, está en [`docs/CASOS_DEMOSTRABLES.md`](CASOS_DEMOSTRABLES.md).
