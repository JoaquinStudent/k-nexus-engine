# Guion de pitch — KNexus Engine

> Sigue **exactamente** la estructura oficial del reto (5 secciones + preguntas del jurado).
> **Total: 3:30 min** + hasta 3 min de preguntas del jurado.
>
> **Formato elegido:** solo 2 slides en la PPT (puntos 1-2). Los puntos 3, 4 y 5 se explican **en
> vivo sobre la aplicación real** — el punto 4 (resultados y métricas) se muestra directo en la
> pantalla `/metrics`, no como gráfico estático en un slide. Menos slides, más prototipo funcionando
> — es justo lo que pide la sección "Condiciones de la demostración" del reto.

| # | Sección (oficial) | Tiempo | Dónde va |
|---|---|---|---|
| 1 | Problema y propuesta de solución | 0:00 – 0:30 | **Slide 1** |
| 2 | Arquitectura y enfoque técnico | 0:30 – 1:30 | **Slide 2** |
| 3 | Demostración funcional | 1:30 – 2:30 | Demo en vivo |
| 4 | Resultados y métricas | 2:30 – 3:00 | Demo en vivo (`/metrics`) |
| 5 | Impacto y evolución | 3:00 – 3:30 | Demo en vivo (hablado, sin slide) |

---

# PARTE A — Slides de la PPT (2 slides)

Cada slide trae: **texto para pegar tal cual** en el slide, **notas del orador** (lo que se dice en
voz alta, no va escrito en la diapositiva) y la **imagen** a usar.

## Slide 1 — Problema y propuesta de solución (0:00 – 0:30)

**Título (pegar en el slide):**
```
KNexus Engine
```

**Subtítulo (pegar en el slide):**
```
Conectar el conocimiento institucional disperso — con evidencia, no con parecido.
```

**Cuerpo / bullets (pegar en el slide):**
```
• Problema: proyectos, tesis, investigadores y capacidades viven repartidos entre sistemas que no
  se hablan. Buscar por palabra clave devuelve parecido, no relevancia.
• Solución: KNexus Engine descubre esas conexiones, las prioriza por pertinencia real y las
  explica con evidencia literal.
• Diferenciador: nunca rankeamos por similitud pura — cada conexión se audita con 7 criterios y
  trae su archivo, campo y registro de origen.
```

**Notas del orador (decir, no pegar):**
> Las universidades producen conocimiento sin parar — proyectos, tesis, investigadores, capacidades
> — pero vive repartido entre sistemas que no se hablan. Buscar por palabra clave devuelve parecido,
> no relevancia; y sin evidencia verificable detrás, la conexión no se puede confiar. KNexus Engine
> descubre esas conexiones, las prioriza por pertinencia real — nunca por coseno puro — y las
> explica con la evidencia literal que las sustenta. Ese es el diferenciador: relevancia auditable,
> no similitud disfrazada de recomendación.

**Imagen para este slide:** diagrama de "islas" — facultades/sistemas representados como nodos
aislados, con líneas punteadas o cortadas entre ellos — transformándose (o al lado, antes/después)
en un grafo conectado con un ícono de evidencia (check + documento) sobre una arista. No hay un
asset ya generado para esto: crearlo en Canva/Figma o pedirlo como imagen nueva. Es el gancho visual
más importante del pitch — antes/después en un solo golpe.

---

## Slide 2 — Arquitectura y enfoque técnico (0:30 – 1:30)

**Título (pegar en el slide):**
```
Cómo funciona
```

**Cuerpo / bullets (pegar en el slide):**
```
• Pipeline de 8 filtros sobre arquitectura hexagonal — dominio puro y auditable en el centro.
• Ingesta con procedencia: 22 tablas + 60 documentos, sin perder archivo ni campo de origen.
• Representación en 3 capas: denso (sentence-transformers + FAISS), léxico (BM25), grafo (NetworkX).
• Recuperación híbrida (RRF) solo genera candidatos — nunca decide el orden final.
• Reranking explicable: 7 features ponderadas deciden el score y el tipo de relación.
• LLM opcional (OpenRouter): sin red, degrada solo a plantillas — nada se cae.
```

**Notas del orador (decir, no pegar):**
> La arquitectura es un pipeline de 8 filtros sobre un núcleo hexagonal: el dominio no importa nada
> hacia afuera, así el scoring queda auditable y testeable sin red — decisión clave para poder
> explicar cada score en vivo. F1 ingiere 22 tablas y 60 documentos sin perder procedencia. F2
> representa el conocimiento en tres capas — denso con sentence-transformers y FAISS, léxico con
> BM25, y grafo con NetworkX sobre las tablas de relación — porque un investigador casi nunca
> comparte vocabulario con una necesidad; esa conexión la trae la arista, no el texto. F3 fusiona
> esas tres señales por RRF, pero solo para generar candidatos: nunca decide el orden final. Esa
> decisión es del dominio puro en F4 — 7 features ponderadas, donde método y capacidad pesan tanto
> como la similitud semántica, y el léxico pesa lo mínimo a propósito para no premiar la trampa
> léxica. Y el LLM en F6 es un puerto: sin conexión, degrada solo a plantillas — nada se cae.

**Imagen para este slide:** el diagrama de `sdd/ARCHITECTURE.md` simplificado a 5-6 cajas máximo (8
filtros en fila, dominio hexagonal al centro) — no meter el diagrama denso completo del documento
técnico. Tampoco hay un asset ya exportado; rehacerlo simple en Canva/Figma a partir del Mermaid del
README.

**Si preguntan por qué esta decisión y no otra**, el porqué de cada una está en `sdd/MEMORY.md`
(ADR-001 a ADR-014) — no memorizar detalle, saber que existe y dónde está.

---

# PARTE B — Demo en vivo (1:30 – 3:30), sin slides

A partir de acá no hay más diapositivas — pantalla compartida sobre la app real (o el CLI si falla
la red, ver Plan B al final). Los puntos 3, 4 y 5 del reto se cubren hablando sobre lo que se ve en
pantalla, en este orden.

## 3 — Demostración funcional (1:30 – 2:30)

> Consulta en vivo, un ID real del dataset, nada precargado — así se ve el flujo completo que pide
> el reto: información institucional → identificación y representación → conexión descubierta →
> valoración de pertinencia → evidencia → oportunidad generada.

| # | Pantalla | Ruta | Etapa del flujo oficial | Qué decir | Qué señalar |
|---|---|---|---|---|---|
| 1 | Descubrir | `/` → escribir `NEED-001` | Información institucional → identificación y representación | "Necesidad real del dataset: predicción y prevención de deserción estudiantil. 2.512 entidades ya indexadas con procedencia." | Contador "2.512 entidades indexadas" |
| 2 | Resultados | `/results?q=NEED-001` | Conexión descubierta | "62 resultados en menos de medio segundo — cada tarjeta ya trae su barra de 7 features, no es una lista por parecido de texto. PRJ-007 arriba, score 0.657." | Mini-barra + pill "Alta" en la tarjeta #1 |
| 3 | Conexión | `/connection/PRJ-007?q=NEED-001` (clic en la tarjeta) | Valoración de pertinencia + Evidencia | "Método transferible 0.90, capacidad institucional 1.00 dominan el score. Y la evidencia es la cita literal, con archivo, campo y registro — nada se fabrica." | Barra desglosada + leyenda, bloque de evidencia con procedencia |
| 4 | Oportunidad | `/opportunity?q=NEED-001` | Oportunidad generada | "De esa conexión sale la cadena completa: necesidad, antecedente, investigador, capacidad, currículo — cada eslabón etiquetado como recuperado, arista real o inferido, nunca mezclados como si fueran la misma clase de evidencia." | Etiquetas `[retrieved]` / `[edge]` / `[inferred]` bajo cada nodo |

> Cierre de este tramo: "Esto no es una búsqueda por palabras clave ni una generación de texto sin
> respaldo — cada paso queda trazado hasta el dato institucional que lo sustenta."

**Si sobra tiempo (bonus, no obligatorio):** flash de `/audit?q=NEED-001&a=PRJ-007&b=PRJ-002` (por
qué A gana a B, delta por feature) o de `/opportunity?q=NEED-009` (dominio distinto, calidad del
agua, para mostrar que no es un caso elegido a mano). Ambos quedan como respaldo para las preguntas
del jurado si no entran en el minuto.

---

## 4 — Resultados y métricas (2:30 – 3:00) — en vivo en `/metrics`

Sin volver a las slides: navegar a `/metrics` (queda un clic desde el header) y seguir hablando
sobre la pantalla real, señalando la tabla "Similitud no es lo mismo que relevancia".

> Comparamos nuestro sistema contra la forma más simple de ordenar resultados — solo por parecido de
> texto — sobre 20 necesidades reales de la universidad, revisadas a mano. Resultado: más del doble
> de las conexiones que mostramos arriba terminan siendo realmente útiles para tomar una decisión
> (0.55 contra 0.27), y bajamos a menos de la mitad los casos que solo comparten palabras pero no
> sirven de nada (de 0.65 a 0.28). Ahí está la pertinencia y el control: no confundimos "se parece"
> con "es relevante". Limitación honesta: si solo importara el tema, ordenar por parecido de texto
> gana más fácil — por eso medimos también si la conexión sirve de verdad, no solo si suena
> parecida.

**Qué señalar en pantalla:** la primera tabla de `/metrics` (columnas "Nuestro sistema" vs
"Ordenado solo por parecido"), fila "...son realmente útiles" y fila "...solo parecen relacionados,
pero no sirven" — esas dos filas son el dato más fuerte del proyecto, más que cualquier gráfico que
se pudiera armar en un slide aparte.

**Respaldo si falla la red/el server:** captura de pantalla de `/metrics` guardada de antemano (o
`mocks-stitch/performance_knexus_engine/screen.png` si no hay una más reciente) — mostrarla a pantalla
completa un momento en vez de un slide dedicado.

---

## 5 — Impacto y evolución (3:00 – 3:30) — cierre hablado, sin volver a las slides

Se queda en la misma pantalla (`/metrics` o `/opportunity`) mientras se cierra hablando — no hace
falta volver a la PPT para esto.

> Llevado a un ecosistema real, esto se conecta directo con procesos que ya existen: antecedentes
> metodológicos para nuevas líneas de investigación, comparadores para elegir asesor y enfoque de
> tesis, cadenas de oportunidad que activan colaboración interdisciplinaria entre grupos que hoy no
> se conocen, y activación de capacidades instaladas que hoy nadie encuentra. Y el eslabón
> curricular ya cierra el círculo: conecta esa evidencia con el proceso académico formal, para que
> lo que se investiga alimente lo que se enseña, no quede aislado en un reporte.

---

## Preguntas del jurado (hasta 3 min adicionales)

| Tema que pueden preguntar | Dónde está la respuesta lista |
|---|---|
| Arquitectura / código | `sdd/ARCHITECTURE.md` (reglas verificables A1-A4) |
| Representación del conocimiento | `sdd/SPEC.md` §4 (7 features) + `ARCHITECTURE.md` §3 (F2) |
| Algoritmos / modelos / APIs externas | `docs/DECLARACION_TECNOLOGICA.md` |
| Calidad de conexiones / priorización | `sdd/SPEC.md` §5-6 (pesos y tipado) |
| Métricas | `sdd/SPEC.md` §13, pantalla `/metrics` en vivo |
| Explicabilidad / trazabilidad | Regla A3, `tests/interface/test_trazabilidad_ui.py` |
| Escalabilidad | README §8 (FAISS exacto, no probado a mayor escala) |
| Limitaciones | README §8 |

## Condiciones de la demostración — autocheck

- Todo lo mostrado corre en el prototipo real (servidor en vivo o CLI) — nada mockeado.
- Las slides (solo 2) son apoyo, no sustituto: todo lo demás se hace en el navegador/CLI real.
- Sólo se afirma como implementado lo que se puede clicar o ejecutar en vivo.
- Cada conexión/oportunidad mostrada trae su evidencia (archivo/campo/registro) visible en pantalla.
- El origen del LLM (OpenRouter, opcional) y su degradación a plantillas quedan explícitos si
  preguntan — la redacción del LLM nunca se presenta como dato institucional.

---

## Plan B si falla el navegador o la red

```bash
python scripts/query_cli.py "NEED-001" --compare PRJ-002 --top 3
```

Mismo dato, sin depender de la demo web. Si el modelo real no llegó a descargarse, `--fast` da
resultados instantáneos (aclarándolo en voz alta si se usa). La salida literal de los tres casos,
capturada de una corrida real, está en [`docs/CASOS_DEMOSTRABLES.md`](CASOS_DEMOSTRABLES.md).
