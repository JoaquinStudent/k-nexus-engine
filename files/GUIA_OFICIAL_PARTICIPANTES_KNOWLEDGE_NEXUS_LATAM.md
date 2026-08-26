#### HACKATHON INTERNACIONAL - NIVEL AVANZADO

# KNOWLEDGE NEXUS LATAM

## Conectar el conocimiento

#### Guia oficial de contexto, escenario institucional, datos y orientacion tecnica para participantes

Este documento debe leerse junto con el dataset oficial Knowledge Nexus LATAM - Data V1.0. Su objetivo es que todos los equipos comprendan el escenario ficticio, el problema que deben resolver, la estructura de la informacion, las capacidades minimas esperadas y las reglas tecnicas de demostracion.

Elemento Definicion Entidad retadora Talento TECH Escenario Institucion de educacion superior ficticia de alcance latinoamericano Nivel Avanzado / Expertos Producto esperado Prototipo funcional de gestion inteligente y conexion del conocimiento Dataset Knowledge Nexus LATAM - Data V1.0 Principio central Conexiones utiles + priorizacion + evidencia + trazabilidad

Importante: la universidad, sus personas, proyectos, tesis, publicaciones, necesidades y demas registros del dataset son sinteticos y fueron construidos exclusivamente para el desafio. No representan una institucion real ni deben interpretarse como informacion de personas reales.

## 1. El escenario: una universidad ficticia intensiva en conocimiento

Para efectos del reto, los participantes trabajaran como si hubieran sido convocados por una universidad ficticia latinoamericana que ha crecido academicamente y produce una gran cantidad de conocimiento, pero no cuenta con una vision integrada de ese conocimiento. La institucion posee facultades, programas, investigadores, grupos, lineas de investigacion, proyectos, tesis, publicaciones, asignaturas, competencias, resultados de aprendizaje y capacidades institucionales. La universidad no tiene un problema de ausencia de informacion. Su problema es que la informacion se encuentra fragmentada : diferentes unidades conocen partes del ecosistema, pero no necesariamente saben que existe en otras facultades, que trabajos previos pueden servir como antecedentes, que capacidades son complementarias o que conocimiento investigativo podria conectarse con el curriculo. En consecuencia, la universidad necesita pasar de tener datos a comprender relaciones, y de comprender relaciones a descubrir oportunidades accionables.

### 1.1 Radiografia institucional del escenario

Componente Volumen en Data V1.0 Facultades 6 Programas academicos 18 Grupos de investigacion 24 Lineas de investigacion 60 Capacidades institucionales 96 Investigadores 180 Asignaturas 126 Competencias 252 Resultados de aprendizaje 378 Necesidades institucionales 42 Proyectos 320 Tesis / trabajos de grado 650 Publicaciones 360 La institucion ficticia cubre seis grandes dominios: Ingenieria y Tecnologias Digitales; Ciencias de la Salud; Ciencias Economicas, Administrativas y Financieras; Educacion y Ciencias Humanas; Ciencias Ambientales y Territoriales; y Ciencias Basicas y Aplicadas. La dificultad del reto surge precisamente de las conexiones que pueden existir entre estos dominios, no solo dentro de cada uno.

## 2. ¿Que esta ocurriendo dentro de la universidad?

La institucion identifica cinco dificultades estructurales: fragmentacion del conocimiento, desconexion semantica, dificultad para descubrir oportunidades, baja trazabilidad de las conexiones y baja capacidad para priorizar las recomendaciones realmente utiles.

### Fragmentacion

Un proyecto, una tesis, una publicacion y una capacidad pueden estar relacionados, pero encontrarse en fuentes distintas.

### Desconexion semantica

Dos unidades pueden trabajar sobre problemas conceptualmente similares usando vocabularios diferentes.

### Oportunidades ocultas

Un antecedente, un investigador o una capacidad pueden ser utiles para una necesidad sin estar vinculados de manera explicita.

### Trazabilidad

Una recomendacion pierde valor si no puede demostrarse que informacion la sustenta.

### Pertinencia

Encontrar muchas coincidencias no equivale a encontrar buenas conexiones; deben priorizarse las que realmente aportan valor. Ejemplo conceptual: ante una necesidad como prediccion y prevencion de desercion estudiantil , un sistema util no deberia limitarse a buscar la palabra 'desercion'. Podria necesitar relacionar permanencia estudiantil, riesgo academico, trayectorias educativas, analitica, investigadores, proyectos previos, grupos, capacidades y componentes curriculares, justificando por que cada elemento aporta al problema.

## 3. La pregunta del desafio

¿Como diseñar una solucion inteligente capaz de descubrir, representar y priorizar conexiones relevantes entre proyectos institucionales, investigacion, trabajos de grado, capacidades academicas y curriculos universitarios, generando oportunidades explicables que fortalezcan la investigacion, la colaboracion interdisciplinaria y la articulacion del conocimiento dentro de una institucion de educacion superior?

El objetivo no es construir un simple repositorio centralizado, un buscador documental ni un chatbot que responda de manera generica. La solucion debe transformar informacion institucional fragmentada en conocimiento conectado y verificable.

### Flujo conceptual esperado

Fuentes institucionales -> integracion y procesamiento -> representacion/comprension -> descubrimiento de relaciones -> valoracion de pertinencia -> oportunidades -> explicabilidad y trazabilidad -> apoyo a decisiones.

## 4. Data V1.0: que reciben los participantes

El dataset oficial esta organizado en tres capas publicas. Los identificadores permiten integrar entidades entre archivos. La solucion debe preservar la procedencia de la informacion y permitir regresar desde un resultado a los registros que lo sustentan. Carpeta Contenido Pregunta que ayuda a responder 01\_institution Facultades, programas, grupos, lineas, capacidades y ¿Que estructura y capacidades tiene la catalogo de fuentes. institucion? 02\_people\_curriculum Investigadores, expertise, pertenencia a grupos, ¿Quien sabe que y donde aparece ese asignaturas, competencias y resultados de conocimiento en la formacion? aprendizaje. 03\_knowledge\_needs Necesidades, proyectos, tesis, publicaciones, ¿Que problemas, antecedentes y productos relaciones y catalogo documental. de conocimiento existen?

### 4.1 Los IDs son parte del contrato de datos

Campos como faculty\_id, program\_id, group\_id, researcher\_id, project\_id, thesis\_id, publication\_id, need\_id y otros identificadores deben entenderse como mecanismos de integracion y trazabilidad. No todos los vinculos valiosos aparecen resueltos por una relacion directa: una parte central del reto consiste en descubrir conexiones que requieren interpretacion tematica, contextual o interdisciplinaria.

### 4.2 Que NO contiene la data publica

El paquete de participantes no contiene respuestas oficiales, rankings esperados, relaciones verdaderas ocultas, casos de evaluacion, hard negatives ni Gold Standard. Esos elementos forman parte del control interno de evaluacion y no son necesarios para desarrollar una solucion valida.

## 5. Capacidades minimas que debe demostrar la solucion

### Integrar

Procesar conjuntamente las fuentes y conservar sus relaciones y procedencia.

### Descubrir

Encontrar relaciones significativas, incluyendo conexiones que no dependan solo de coincidencias literales.

### Representar

Permitir comprender que entidades estan conectadas y la naturaleza de la relacion.

### Priorizar

Diferenciar conexiones superficiales de aquellas con mayor pertinencia o potencial institucional.

### Generar oportunidades

Convertir relaciones en posibilidades utiles de investigacion, colaboracion, antecedentes, capacidades o articulacion curricular.

### Explicar

Indicar por que una conexion se considera relevante.

### Trazar

Mostrar que archivo, registro o evidencia institucional sustenta el resultado.

### Explorar

Disponer de interfaz, API, dashboard, grafo, mecanismo de consulta u otro componente funcional para revisar los resultados.

La secuencia minima que debe poder observarse durante una demostracion es: consultar/procesar informacion -> descubrir una relacion -> valorar su pertinencia -> consultar la evidencia -> generar o identificar una oportunidad util.

## 6. Libertad tecnologica

No existe una arquitectura obligatoria. Los equipos pueden emplear procesamiento de lenguaje natural, recuperacion de informacion, embeddings, grafos, ontologias, sistemas de recomendacion, machine learning, modelos fundacionales, agentes, reglas, bases vectoriales, bases de grafos o enfoques hibridos, entre otras alternativas. Una tecnologia avanzada no otorga ventaja por si misma. Se evaluara si contribuye de manera verificable a resolver el problema. Un sistema sencillo pero bien sustentado puede superar a uno mas complejo si sus conexiones son mas pertinentes, trazables y utiles.

Si se utilizan servicios externos, APIs, modelos preentrenados o IA generativa, deben declararse. El equipo debe poder distinguir informacion proveniente de la data institucional de contenido generado o inferido por dichos componentes.

## 7. ¿Como luce un resultado de calidad?

No existe una unica interfaz ni un formato obligatorio. Sin embargo, una recomendacion importante deberia permitir reconstruir una cadena de razonamiento verificable. Necesidad -> antecedentes/proyectos/tesis -> investigadores o grupos -> capacidades -> componente curricular (cuando aplique) -> oportunidad propuesta -> nivel de pertinencia -> evidencia fuente. Un score de 0.92, por ejemplo, puede ayudar a priorizar, pero no constituye por si mismo evidencia. El evaluador debe poder preguntar "¿por que?" y el sistema/equipo debe poder responder mostrando los datos que sustentan la conexion. Tambien se espera que la solucion controle resultados irrelevantes, redundantes o engañosamente similares. Una alta similitud lexical no siempre implica una conexion academica pertinente.

## 8. Entregables tecnicos

Entregable Contenido minimo Prototipo funcional - MVP Flujo end-to-end implementado y demostrable sobre Data V1.0. Repositorio de codigo Codigo, configuraciones, dependencias, scripts, modelos/artefactos y estructura organizada. README tecnico Descripcion, arquitectura, tecnologias, instalacion/ejecucion, reproduccion de demo, mecanismo de descubrimiento/priorizacion y limitaciones. Diagrama de arquitectura Fuentes -> procesamiento -> representacion -> descubrimiento -> valoracion -> resultados. Evidencia de desempeño Metricas o evidencia experimental coherente con el enfoque implementado y explicacion de como se obtuvo. Casos demostrables Ejemplos donde se observe entidad/elementos -> relacion -> evidencia -> pertinencia -> oportunidad -> explicacion. Declaracion de componentes externos APIs, cloud, modelos, datasets complementarios, frameworks, herramientas generativas u otros recursos externos relevantes. No es suficiente presentar mockups, diapositivas, un modelo aislado o una visualizacion sin integracion funcional.

## 9. Como se evaluara tecnicamente

La evaluacion tecnica oficial se realiza sobre 100 puntos. El pitch final no suma ni resta puntos dentro de esta metrica tecnica. La organizacion podra utilizar el pitch como instancia posterior de comunicacion o seleccion conforme a la dinamica general del evento, pero no modifica retrospectivamente la calificacion tecnica. Criterio Puntos Arquitectura y calidad tecnica 20 Funcionamiento del prototipo 20 Innovacion 15 Impacto y escalabilidad 10 Calidad y pertinencia de las conexiones 8 Representacion e integracion del conocimiento 6 Generacion de oportunidades y valor academico 7 Priorizacion y calidad de recomendaciones 5 Explicabilidad y trazabilidad 4

Criterio Puntos Validacion tecnica durante la revision 5 TOTAL 100 Durante las revisiones, los evaluadores podran solicitar consultas o situaciones de validacion que permitan comprobar el comportamiento real del prototipo. Los equipos deben estar preparados para demostrar funcionamiento, no solo ejemplos previamente preparados.

## 10. Que esperar durante las revisiones

El reto se desarrolla con seguimiento tecnico progresivo. Los evaluadores no actuan como mentores ni revelaran respuestas. Su funcion es observar el proceso, solicitar evidencia y comprobar que la solucion evoluciona hacia un sistema funcional y sustentado. Momento Que debe poder mostrar el equipo Dia 1 - revision inicial Comprension de la data, estrategia, arquitectura inicial e integracion de fuentes. Dia 1 - revision de avance Primer flujo funcional, conexiones iniciales, criterio de priorizacion y evidencia disponible. Dia 2 - revision de consolidacion Solucion integrada, calidad de conexiones, oportunidades, explicabilidad y trazabilidad. Dia 2 - revision final Funcionamiento bajo solicitud del evaluador, auditoria de una conexion/evidencia y defensa tecnica de las decisiones. No es necesario preparar cuatro presentaciones. Las visitas buscan revisar el estado real del producto. El equipo debe poder abrir su solucion, mostrar resultados y explicar decisiones tecnicas de manera directa.

## 11. Checklist antes de la evaluacion final

n ¿Nuestra solucion procesa realmente Data V1.0 y no solo ejemplos manuales? n ¿Podemos demostrar al menos una conexion no trivial entre fuentes diferentes? n ¿Podemos explicar por que una conexion es relevante y por que otra no lo es? n ¿Existe un mecanismo de priorizacion o valoracion? n ¿Podemos llegar desde una recomendacion hasta el archivo/registro que la sustenta? n ¿Las oportunidades generadas se derivan de la evidencia institucional? n ¿Podemos mostrar conexiones con investigacion, capacidades y/o curriculo? n ¿Nuestro prototipo funciona end-to-end durante una consulta nueva? n ¿La arquitectura mostrada corresponde a lo que realmente implementamos? n ¿El README permite comprender y ejecutar la solucion? n ¿Declaramos modelos, APIs y componentes externos? n ¿Podemos explicar limitaciones y evitar afirmar mas de lo que los datos permiten?

## 12. Errores que reducen el valor de una propuesta

(cid:127) Construir solo un buscador por palabras clave sin capacidad de relacionar y priorizar. (cid:127) Generar recomendaciones con IA sin evidencia rastreable en el dataset. (cid:127) Presentar gran cantidad de coincidencias sin distinguir relevancia. (cid:127) Mostrar una arquitectura ideal que no corresponde al prototipo ejecutable. (cid:127) Usar un score sin explicar su significado o como fue obtenido. (cid:127) Depender de ejemplos precargados que no responden ante nuevas consultas. (cid:127) Confundir una visualizacion atractiva con la resolucion integral del problema.

## 13. La idea que debe guiar todo el reto

Knowledge Nexus LATAM no pregunta solamente "¿que informacion existe?" . Pregunta "¿como se conecta, que oportunidad surge de esa conexion y como puedo demostrar que la recomendacion tiene fundamento?" El resultado esperado es una solucion capaz de pasar de informacion dispersa -> conocimiento estructurado -> conexiones relevantes -> oportunidades priorizadas -> decisiones mejor informadas .

La aprobacion de trabajos de grado, cambios curriculares, decisiones investigativas u otras actuaciones institucionales seguirian dependiendo de los mecanismos academicos correspondientes. La solucion funciona como apoyo inteligente a la toma de decisiones, no como sustituto del juicio academico.

#### Documento para participantes - Knowledge Nexus LATAM - Data V1.0
