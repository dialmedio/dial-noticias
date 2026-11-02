# Referentes · lo que aprendemos de los diseños que Martín ve a diario

Este manual crece con cada referente que Martín manda (`/calco <enlace>`). El objetivo no es copiar piezas ni
esquivarlas: es **aprender sus técnicas y conceptos**, traducirlos a la materia de Dial y dejarlos como
posibilidades para todas las líneas. Cada referente deja tres cosas:

1. una **ficha** aquí: qué hace, por qué funciona, cómo lo traduce Dial y cuándo usarlo (diseño y escritura);
2. **herramientas** en el código del kit (hoy: `iluminado.py`);
3. una **pieza de prueba** que las usa en un tema nuestro.

## Cómo se aprende de un referente (el método, tal como quedó el 2 nov 2026)

Lo que salió del primer ejercicio, en seis rondas con Martín:

| Ronda | Qué se hizo | Qué dijo Martín | Lección |
|---|---|---|---|
| 1 | Copia casi literal: misma frase, río turquesa, mancha lima, afiche ondulado | «Nada literal; que sea irreconocible» | Copiar no es aprender |
| 2-3 | Se tomó solo el recorrido y se volvió al manual viejo (hoja de periódico) | «Está mejor», pero «no le estamos sacando provecho» | Esquivar el referente tampoco es aprender |
| 4 | Se sacaron las técnicas, se tradujeron a otro oficio y se volvieron herramientas | «Va mucho mejor» | El método correcto |
| 5 | Se quitaron las personas porque se veían feas | «No quites las personas: serán importantes en muchos diseños» | Ante una crítica, mejorar la ejecución antes que quitar el recurso |
| 6 | Personas en fotograbado, sin delineado, color solo en la ropa, recortes limpios | «Textura aprobada… ¡Excelente!» | La técnica de personas queda fijada |

Reglas que salen de ahí:

- Se toma **el concepto y el procedimiento**, no la ejecución: si el referente pinta un río de turquesa plano, Dial
  pinta el agua con aguada de añil que sangra sobre un grabado. Mismo principio (el color solo en lo vivo), otro oficio.
- Se puede cambiar paleta, textura, letra y materia; no se pierde lo que hace bonita y eficaz a la pieza.
- Nunca pasan: frases, palabras clave, la paleta de identidad de la otra cuenta, sus fuentes, sus ornamentos tal cual,
  ni testimonios que no podamos verificar.
- Las ideas de fondo del texto sí pasan, dichas desde Colombia y llevadas a **lo común** cuando el referente vende algo
  (curso, club, producto): la junta, la minga, la olla, el acueducto comunitario, la asamblea.
- Prueba de distancia: al lado del referente se reconoce el parentesco de oficio, no la pieza.
- Se aprende de **diseño y de escritura** a la vez: cómo conceptualiza, desde qué persona habla, en qué orden van
  emoción y dato.

---

## Ficha 1 · @ecologiasensible, «crisis de sensibilidad» (24 oct 2026) · aprobada

Carrusel de 7 láminas sobre la ecoansiedad que termina invitando a un club. Collage de paisaje en blanco y negro con
el río pintado a mano, texto de dos voces, un ritmo de luz y oscuridad. Dejó la técnica **grabado iluminado**.
Pieza de prueba aprobada: `D:/AA Dialmedio/Noticias/Al Aire/2026-11-02 Nada nos conmueve (calco)/` (`calco.py` es el
ejemplo de uso de todo el kit).

### Diseño

| En el referente | Por qué funciona | Cómo lo hace Dial | Herramienta |
|---|---|---|---|
| El mismo cañón aparece en todas las láminas | El carrusel se siente una sola pieza; deslizar es seguir mirando | **Paisaje continuo**: una panorámica de N láminas de ancho que corre sin corte. Cambia de luz: día en las láminas de papel, noche en las de cartulina, como capítulos | `paisaje_continuo()` |
| Foto en gris y solo el río en turquesa | El ojo va a lo vivo; el gris dice «pérdida» sin decirlo | **Grabado de buril** (líneas que engordan en la sombra) y **aguada** a mano solo en lo vivo: sangra, se acumula en el borde, se corre del dibujo. Color por tema: añil (agua), salvia (monte), ocre (tierra) | `grabado()`, `aguada()` |
| El cerro recortado contra el papel | El paisaje sale de la hoja; el texto vive en el cielo | **Horizonte recortado** | `horizonte()` |
| La cola de ballena que sale del agua y del borde | Una figura que rompe el marco da escala y emoción | **Figura que sale del paisaje**, pie en el borde de abajo. **Personas en fotograbado**: tono continuo con grano de aguatinta, impresas en el mismo papel de la lámina, sin delineado, con la prenda de color iluminada (nunca la piel). Plantas y objetos en buril | `persona()`, `figura_buril()` |
| Mancha verde de resaltador detrás de la itálica | Marca la frase que se siente, no la que informa | **Pincelada seca** de brasa, de canto nítido. Una o dos por pieza | `pincelada()`, `renglones(pincel=…)` |
| Hoja de papel rasgado sobre la foto | Separa una reflexión del paisaje sin cajas digitales | **Hoja rasgada** en sus cuatro lados, girada 1-2°, con sombra; lo escrito encima se recorta con la hoja | `hoja()` |
| Curvas de nivel en una esquina | Dicen «territorio» sin mostrarlo | **Isolíneas** de añil que se desvanecen desde una esquina | `isolineas()` |
| Palo seco negrita + itálica de exhibición | Dos voces: la que afirma y la que siente | **Afirma**: Instrument Sans 700. **Siente**: Fraunces itálica 800, SOFT 100 | `afirma()`, `siente()` |
| Lámina oscura con palabras de dos colores | La lista se lee como poema; el color marca el sustantivo | Cartulina con tinta clara; acentos en itálica alternando brasa clara y añil claro | `mixto()`, `TINTA_CLARA`, `ANIL_CLARO` |
| Láminas oscuras con materia, no negro plano | Profundidad | **Cielo rayado**: rayas finísimas (13 % de tinta) que pesan arriba, continuas entre láminas de noche | `cielo_rayado()` |
| Afiche del club: letra ondulada, cinta, filas de palabras | Cambia de registro: de reflexión a convocatoria | **Cartel de junta**: fila de lugares (barrio, vereda, resguardo), cifra grande grabada y pintada con aguada, cinta de papel rasgado | `cifra()`, `cartel()`, `hoja()` |
| Testimonio con trazos de resaltador | «Esto me tocó» | **Subrayado de marcador** fino bajo la frase que hay que llevarse, o bajo una cita real verificada | `subrayado()` |
| La cuenta centrada abajo, pequeña | No compite | `@dialmedio` con el aro; tinta automática según el fondo; a la izquierda si una figura ocupa el centro | `firma()` |

**Lo que no pasa:** el verde lima, el lila y el turquesa; Playfair y Arial; las curvas rosadas; la tarjeta en punta;
la letra ondulada de caricatura; sus frases.

### Escritura y concepto

| En el referente | Por qué funciona | Cómo lo usa Dial |
|---|---|---|
| Diagnóstico en primera persona plural | Incluye al lector sin señalarlo | «Vivimos entre pérdidas»: el medio habla desde adentro, no desde arriba |
| Nombra la emoción antes que el dato | Valida lo que el lector ya siente | El duelo como marco: «un duelo, aunque nadie haga velorio» |
| La anestesia es del sistema, no culpa de cada quien | Quita la vergüenza, abre la puerta a actuar | «No es culpa de cada quien, y tampoco se cura a solas» |
| Lista de hechos como poema | Se lee en voz alta; pesa sin tablas | Lista-poema sin números: cada renglón un hecho verificado, el último cambia de escala («y todo cabe en la misma pantalla») |
| Anáfora que sube hasta el giro | Ritmo que prepara la salida | «Cuando… duele / Cuando… duele / Cuando lo hablamos entre todos, pesa menos» |
| De lo individual a lo colectivo | La salida es práctica y cercana | Siempre lo común concreto: la junta, la minga, la olla, el acueducto |
| Prueba social | Otra voz confirma | Dato verificado (53.153 juntas) o voz real con fuente; jamás inventada |
| Llamado de baja fricción | Pide poco, conversa | «¿Tú en cuál estás?»; en la descripción, «cuéntanos cómo se llama la de tu barrio» |
| Respeta los ritmos | Nadie se siente regañado | «Cada quien llega a esto a su ritmo» antes de invitar |

### La pieza, lámina por lámina (para repetir la estructura)

1. **Portada**: isolíneas arriba, rótulo de sección, la pregunta en dos voces con pincelada arriba a la izquierda, bajada
   corta; una persona que mira a cámara sale del paisaje a la derecha. El texto nunca toca la cara.
2. **Golpe**: hoja rasgada sobre el paisaje; el hecho en palo seco con subrayado; el sentir en itálica de añil.
3. **Noche · lista-poema**: cartulina, cielo rayado, palabras de color; una planta en buril sale del paisaje.
4. **Noche · anáfora**: tres tiempos, el último en itálica de brasa clara.
5. **Lo común**: texto a la izquierda con los nombres en añil, la frase que se siente con pincelada; una persona sale de
   la orilla.
6. **Cartel de junta**: fila de lugares, cifra en aguada, cinta, pregunta con pincelada, misión de Dial, firma.

### Cuándo usar el grabado iluminado

- Temas de ambiente, territorio, memoria, duelo y comunidad (Termómetro, Al Aire reflexivo, Arte y memoria, Quynza).
- Reflexiones con recorrido (hasta 6 láminas), no breves de último minuto.
- Con una panorámica para el paisaje continuo (Commons tiene muchas de páramos y lagunas) y una o dos personas
  recortables (Prensa Rural en Flickr, CC BY 2.0).

### Cómo se usa en código (resumen; el ejemplo completo es `calco.py` de la pieza)

```python
import iluminado as il
dia, noche = il.paisaje_continuo(Image.open("panoramica.jpg"), n=6, recorte=(x0, y0, x1, y1), cache=carpeta)
img = il.pliego(1080, 1350, semilla, noche=False)
img.alpha_composite(dia.crop((0, 0, 1080, 600)), (0, 750))              # el tramo de la lámina 1
papel = lambda w, h: il.pliego(1080, 1350, semilla).crop((x, 1350 - h, x + w, 1350))
img.alpha_composite(il.persona(Image.open("cara.jpg"), 820, papel, cache=..., caja=..., claro=[...]), (x, 1350 - 820))
il.renglones(img, ["nada nos", "conmueve?"], 384, il.siente(128), il.SEPIA, 126, centro=False, pincel=BRASA)
il.firma(img)
```

### Decisiones de Martín sobre las tensiones con las máximas

- Personas recortadas: **sí**, en fotograbado y sin delineado (2 nov). Son centrales para los diseños de Dial.
- Portada: la cara sale del paisaje en fotograbado y la pregunta manda al lado, sin tocarla (aprobada en la pieza).
- Pendiente de confirmar: el añil como segunda tinta junto a la brasa (la v5 pide una sola luz) y la lista-poema (las
  máximas piden prosa; esta no lleva números).

### Revisión de oficio (errores ya cometidos con esta técnica; revisar antes de entregar)

Personas
- Nunca en buril ni con delineado: se ven de billete o de plantilla. Fotograbado (`persona`).
- Ningún texto ni hoja encima de una cara: se mueve la figura o el texto antes que taparla.
- El color va en la prenda, jamás en la piel. `color_de("rojo")` mide proporción (en la tela el verde y el azul son
  menos de la mitad del rojo; la piel al sol conserva verde); se queda la mancha grande, se rellenan sus brillos y llega
  hasta el borde. Nada de cortes por altura: dejan un filo recto.
- Si el color en una prenda o mochila parece mancha, va sin color (`tinte=None`).
- Encuadre con el cuerpo entero hasta el borde de abajo: si el encuadre corta un hombro, se amplía la caja.
- Otras personas pegadas: polígono `quitar` que siga la línea del hombro; nada de cortes rectos.
- Fondo claro entre mechones o bajo un sombrero: polígono `claro` (quita lo claro, deja el pelo oscuro).
- Para cortar más arriba, `hasta` (después de la máscara): si se cambia la caja, rembg recalcula y puede pegar manchas.
- Objetos borrosos en primer plano (una bandera, una mano) se dejan fuera del encuadre.
- Las máscaras se guardan en `fuentes/` con el nombre de la caja; si se cambia la caja, se borra la máscara vieja.
- Revisar cada figura con acercamiento al 100 %: halos, astillas, huecos en la ropa.

Paisaje y texturas
- El agua es todo lo que queda bajo la orilla, aun los reflejos oscuros; si no, quedan manchas negras que parecen error.
- El agua clara en el grabado y la aguada mandando; de noche, la aguada a media fuerza.
- El borde de la panorámica no puede dejar escalón en la orilla (se recorta la foto o se iguala el borde).
- Isolíneas sin escalones de píxel ni manchas en las cimas; se desvanecen desde una esquina, nunca en caja.
- Pincelada de canto nítido; cielo rayado casi invisible.
- Revisar la tira continua entera (`versiones/tira-continua.jpg`): sin saltos en el filo de los cerros ni en la orilla.

Composición
- La portada al mismo nivel que el resto: si las demás láminas tienen paisaje y dos voces, la portada también.
- Pincelada una o dos veces por pieza; subrayado una vez.
