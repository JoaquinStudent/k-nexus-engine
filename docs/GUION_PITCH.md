# Guion de pitch — KNexus Engine

> Sigue **exactamente** la estructura oficial del reto (5 secciones + preguntas del jurado). Texto para
> decir en voz alta, no para leer — memorizar la idea de cada bloque, no la frase literal.
> **Total: 3:30 min** + hasta 3 min de preguntas del jurado.

| # | Sección (oficial) | Tiempo | Duración |
|---|---|---|---|
| 1 | Problema y propuesta de solución | 0:00 – 0:30 | 30s |
| 2 | Arquitectura y enfoque técnico | 0:30 – 1:30 | 60s |
| 3 | Demostración funcional (en vivo) | 1:30 – 2:30 | 60s |
| 4 | Resultados y métricas | 2:30 – 3:00 | 30s |
| 5 | Impacto y evolución | 3:00 – 3:30 | 30s |

---

## 1 — Problema y propuesta de solución (0:00 – 0:30)

> Las universidades producen conocimiento sin parar — proyectos, tesis, investigadores, capacidades —
> pero vive repartido entre sistemas que no se hablan. Buscar por palabra clave devuelve parecido, no
> relevancia; y sin evidencia verificable detrás, la conexión no se puede confiar. KNexus Engine
> descubre esas conexiones, las prioriza por pertinencia real — nunca por coseno puro — y las explica
> con la evidencia literal que las sustenta. Ese es el diferenciador: relevancia auditable, no
> similitud disfrazada de recomendación.

**Imagen:** diagrama de "islas" (facultades/sistemas aislados, líneas cortadas) transformándose en un
grafo conectado con un ícono de evidencia (check + documento) sobre una arista. Antes/después en un
solo golpe visual.

---

## 2 — Arquitectura y enfoque técnico (0:30 – 1:30)

> La arquitectura es un pipeline de 8 filtros sobre un núcleo hexagonal: el dominio no importa nada
> hacia afuera, así el scoring queda auditable y testeable sin red — decisión clave para poder explicar
> cada score en vivo. F1 ingiere 22 tablas y 60 documentos sin perder procedencia. F2 representa el
> conocimiento en tres capas — denso con sentence-transformers y FAISS, léxico con BM25, y grafo con
> NetworkX sobre las tablas de relación — porque un investigador casi nunca comparte vocabulario con
> una necesidad; esa conexión la trae la arista, no el texto. F3 fusiona esas tres señales por RRF,
> pero solo para generar candidatos: nunca decide el orden final. Esa decisión es del dominio puro en
> F4 — 7 features ponderadas, donde método y capacidad pesan tanto como la similitud semántica, y el
> léxico pesa lo mínimo a propósito para no premiar la trampa léxica. Y el LLM en F6 es un puerto: sin
> conexión, degrada solo a plantillas — nada se cae.

**Imagen:** el diagrama de `sdd/ARCHITECTURE.md` simplificado a 5-6 cajas máximo (8 filtros en fila,
dominio hexagonal al centro) — no meter el diagrama denso completo del documento técnico.

**Si preguntan por qué esta decisión y no otra**, el porqué de cada una está en `sdd/MEMORY.md`
(ADR-001 a ADR-014) — no memorizar detalle, saber que existe y dónde está.

---

## 3 — Demostración funcional en vivo (1:30 – 2:30)

> Consulta en vivo, un ID real del dataset, nada precargado — así se ve el flujo completo que pide el
> reto: información institucional → identificación y representación → conexión descubierta →
> valoración de pertinencia → evidencia → oportunidad generada.

| # | Pantalla | Ruta | Etapa del flujo oficial | Qué decir | Qué señalar |
|---|---|---|---|---|---|
| 1 | Descubrir | `/` → escribir `NEED-001` | Información institucional → identificación y representación | "Necesidad real del dataset: predicción y prevención de deserción estudiantil. 2.512 entidades ya indexadas con procedencia." | Contador "2.512 entidades indexadas" |
| 2 | Resultados | `/results?q=NEED-001` | Conexión descubierta | "62 resultados en menos de medio segundo — cada tarjeta ya trae su barra de 7 features, no es una lista por parecido de texto. PRJ-007 arriba, score 0.657." | Mini-barra + pill "Alta" en la tarjeta #1 |
| 3 | Conexión | `/connection/PRJ-007?q=NEED-001` (clic en la tarjeta) | Valoración de pertinencia + Evidencia | "Método transferible 0.90, capacidad institucional 1.00 dominan el score. Y la evidencia es la cita literal, con archivo, campo y registro — nada se fabrica." | Barra desglosada + leyenda, bloque de evidencia con procedencia |
| 4 | Oportunidad | `/opportunity?q=NEED-001` | Oportunidad generada | "De esa conexión sale la cadena completa: necesidad, antecedente, investigador, capacidad, currículo — cada eslabón etiquetado como recuperado, arista real o inferido, nunca mezclados como si fueran la misma clase de evidencia." | Etiquetas `[retrieved]` / `[edge]` / `[inferred]` bajo cada nodo |

> Cierre de la demo: "Esto no es una búsqueda por palabras clave ni una generación de texto sin
> respaldo — cada paso queda trazado hasta el dato institucional que lo sustenta."

**Si sobra tiempo (bonus, no obligatorio):** flash de `/audit?q=NEED-001&a=PRJ-007&b=PRJ-002` (por qué
A gana a B, delta por feature) o de `/opportunity?q=NEED-009` (dominio distinto, calidad del agua, para
mostrar que no es un caso elegido a mano). Ambos quedan como respaldo listo para las preguntas del
jurado si no entran en el minuto.

**Imagen de respaldo** (si falla red/proyección): capturas reales en `mocks-stitch/`, en orden
`query_discover_knexus_engine` → `results_ranked_connections_knexus_engine` →
`connection_detail_knexus_engine` + `evidence_provenance_knexus_engine` →
`opportunity_knexus_engine`.

---

## 4 — Resultados y métricas (2:30 – 3:00)

> Comparamos nuestro sistema contra la forma más simple de ordenar resultados — solo por parecido de
> texto — sobre 20 necesidades reales de la universidad, revisadas a mano. Resultado: más del doble de
> las conexiones que mostramos arriba terminan siendo realmente útiles para tomar una decisión
> (**0.55** contra **0.27**), y bajamos a menos de la mitad los casos que solo comparten palabras pero
> no sirven de nada (de **0.65** a **0.28**). Ahí está la pertinencia y el control: no confundimos "se
> parece" con "es relevante". Limitación honesta: si solo importara el tema, ordenar por parecido de
> texto gana más fácil — por eso medimos también si la conexión sirve de verdad, no solo si suena
> parecida.

**Imagen:** barras `actionable_rate` (0.55 vs 0.27) y `trap_rate` (0.28 vs 0.65), `full` vs `cosine`,
colores semánticos (verde=bueno, rojo=trampa). Es el dato más fuerte del proyecto.

---

## 5 — Impacto y evolución (3:00 – 3:30)

> Llevado a un ecosistema real, esto se conecta directo con procesos que ya existen: antecedentes
> metodológicos para nuevas líneas de investigación, comparadores para elegir asesor y enfoque de
> tesis, cadenas de oportunidad que activan colaboración interdisciplinaria entre grupos que hoy no se
> conocen, y activación de capacidades instaladas que hoy nadie encuentra. Y el eslabón curricular ya
> cierra el círculo: conecta esa evidencia con el proceso académico formal, para que lo que se
> investiga alimente lo que se enseña, no quede aislado en un reporte.

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
- Las slides son apoyo, no sustituto: la demo se hace en el navegador/CLI real.
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
