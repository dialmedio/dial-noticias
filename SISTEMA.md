# Sistema de noticias del día · Dial Medio

Martín manda foto(s), contexto y enfoque. Claude investiga, verifica, arma el carrusel con `dial_noticias.py` y entrega las imágenes más las descripciones listas para subir. **Este archivo es la fuente de verdad: no rediseñar, no cambiar tamaños ni colores. Solo se escriben el JSON y los textos.**

## 0. Preparar

- **Kit público:** https://github.com/dialmedio/dial-noticias. En un sandbox: `git clone --depth 1 https://github.com/dialmedio/dial-noticias` (o bajar `https://github.com/dialmedio/dial-noticias/archive/refs/heads/main.zip`). Si no hay internet en el sandbox, pedirle a Martín que adjunte el zip del kit.
- **En el PC de Martín (Claude Code):** el kit está en `D:\Claude Code\dial-noticias\`. Las fotos van a `D:\AA Dialmedio\AudiovisualDial\Noticias\<AAAA-MM-DD> <Tema>\fuentes\` y el JSON a `noticias/<AAAA-MM-DD>-<tema>.json`, con `salida` = la carpeta de la noticia.
- **En el sandbox:** ejecutar `pip install pillow numpy` si falta algo y trabajar con rutas relativas: el JSON va junto a las fotos (o con rutas relativas a ellas), y la salida por defecto es `salida/` junto al JSON. Los videos usan ffmpeg: si no está instalado, el generador instala `imageio-ffmpeg` por su cuenta.
- Uso: `python dial_noticias.py <noticia>.json [--solo=2,4]`. Genera `<prefijo>-NN.jpg` (o `.mp4` si la lámina es un video) y `<prefijo>.zip` con todo.

## Diseño: Al Aire v2 (vigente desde el 18 oct 2026)

Lo aprobó Martín con el carrusel "Protestas en el mundo". Referentes: Mutante (campos planos, titulares condensados, collage en semitono, etiquetas en caja) y La Linterna de Cali (tipos de madera, tinta de prensa). Lo dibuja `al_aire.py`; `dial_noticias.py` lo usa por defecto (`"estilo": "v1"` vuelve al diseño anterior).

- **Cabecera fija** en todas las láminas: caja brasa con el punto "en vivo" y `AL AIRE` en mono, luego `meta` (lugar · fecha) en caja carbón, y el logo arriba a la derecha.
- **Color:** la brasa `#E58A3A` es el color de Al Aire (el manual ya la reserva para lo "en vivo"). Terracota, carbón y papel, como siempre. No se agregan colores.
- **Titulares:** Instrument Sans 700 al 75 % de ancho (condensada), caja mixta. El acento (`*así*`) va en carbón sobre una franja brasa. Las líneas se equilibran solas.
- **Rótulos:** IBM Plex Mono en mayúsculas dentro de una caja (papel sobre fotos, carbón sobre terracota). Créditos y fuentes, en mono abajo.
- **Láminas sin foto** (`"tipo": "texto"`), según `estilo` (si no se pone, se deduce):
  - `pais`: campo terracota con el `titulo` en tipo de madera (papel, con la pasada corrida en carbón), `rotulo`, `texto`, `items` numerados y `citas` en serif. Para países o lugares sin foto libre.
  - `citas`: papel limpio, sin textura en las letras. Comillas grandes en terracota, la cita en Sans 600 y el autor en mono. Es la lámina de "la versión del Gobierno".
  - `analisis`: carbón con una foto en semitono brasa (`"semitono": "fuentes/x.jpg"`, `"foco_semitono": [x, y]`) con borde rasgado, el `titulo` con franja, `items` numerados en mono y `cierre` con filete. Para la lámina de análisis o cierre.
  - `ficha`: solo en Nuevos Mundos Posibles (ver esa sección).
  - `cta`: **siempre la última lámina** (desde el 19 oct 2026). Carbón con un signo de pregunta grande en tipo de madera terracota, rótulo `TU OPINIÓN`, la `pregunta` en titular de impacto (con *acento*), un `texto` opcional que la aterriza, las cajas `● COMENTA · GUARDA · COMPARTE` y la firma (logotipo, "Sintonizar es conversar." y @dialmedio). La pregunta es abierta, sobre el tema de la pieza y **sin tomar partido** (p. ej. "¿*Negociar o someter*? ¿Cuál crees que es el camino hacia la paz?"). La misma pregunta va al final de las dos descripciones, antes de los créditos.
- **Rótulo de persona (v2):** un punto brasa sobre la persona y una guía horizontal hacia dos cajas planas, como la cabecera: el nombre (papel, titular condensado) y el cargo (carbón, mono). `"persona": {"nombre", "cargo", "x", "y", "lado"}`: `x`, `y` es el punto, **sobre el hombro o el pecho, nunca sobre la cara**; `lado` (`"izq"` o `"der"`) es hacia dónde sale el rótulo. Hay que elegir el lado con espacio libre, sin tapar otras caras. El rótulo queda centrado a la altura del punto.
- **Franja del acento:** se pintan todas las franjas antes que el texto, para que las letras que bajan (g, j, p, q, y) de la línea de arriba no queden cortadas. La puntuación pegada al acento (¿ ? , :) entra en la franja.
- **Texturas:** solo de impresión y evidentes. Tipo de madera (v3, 19 oct 2026): borde nítido y mordido, veta horizontal larga, huecos de canto nítido y poros sueltos; la segunda pasada, corrida y en otra tinta, solo asoma por fuera de la letra. Moteado amplio en los campos planos. Nunca grano sobre las fotos ni en el texto corrido.

## Línea Nuevos Mundos Posibles (desde el 21 oct 2026)

Buenas noticias: conservación, ciencia y biología, clima, comunidades y economías propias, ciudades que cambian. Es una línea propia de Al Aire, con corrida de propuestas los lunes y los jueves. Se activa con `"seccion": "nuevos-mundos"` arriba en el JSON (sin `"seccion"` todo sale como Al Aire, idéntico). Misma estructura, tipografía, rótulos, rótulo de persona y lámina `cta`; cambia la tinta y la textura, con la idea de un **cuaderno de campo**:

- **Sello:** `NUEVOS MUNDOS POSIBLES` con una **hoja** donde Al Aire lleva el punto "en vivo". No se pone `sello` en el JSON. Como el nombre es largo, el lugar y la fecha (`meta`) bajan solos a una segunda caja bajo el sello.
- **Color:** el **brote** `#A8C656` reemplaza a la brasa (franjas del acento, sello, numeración, punto del rótulo de persona). **Selva** `#162C21` es el fondo de `analisis` y `cta` (en vez de carbón) y **musgo** `#345C40` el campo de la lámina de lugar (en vez de terracota). Carbón, papel y el logo no cambian.
- **Texturas propias:** cuadrícula de libreta de campo en las láminas de papel (`citas` y `ficha`) y **grabado de línea** en las fotos de las láminas sin foto (`analisis` y `ficha`), como las láminas de historia natural, en vez del semitono de puntos. El tipo de madera se mantiene (lugar, dato, signo del cierre).
- **Lámina `ficha`** (propia de esta línea, `"tipo": "texto", "estilo": "ficha"`; se deduce si trae `dato` o `campos`): papel cuadriculado con, en orden y todo opcional, la foto en grabado (`semitono`, `foco_semitono`, `pie_foto`: "Fig. 1 · …"), `rotulo`, el **dato** grande en tipo de madera (`"dato": "+40 %"`, corto, con su `dato_pie`), `titulo` con acento, `texto` y la **etiqueta de herbario** `campos`: `[["Especie", "Rana de cristal (Nymphargus …)"], ["Dónde", "…"], ["Quién", "…"]]`. Es la lámina del dato que prueba la buena noticia. Si el generador avisa que se pasa de alto, quitar la foto o un campo.
- **Criterio:** que esté probado, no solo anunciado; los límites van en la pieza (una lámina de "lo que falta"); sin maquillaje verde (nunca solo el comunicado de una empresa o un gobierno sobre sus logros). Ciencia: nombre común y científico, y "especie nueva" solo si está descrita formalmente.
- **Fotos de especies:** también de iNaturalist, solo CC0, CC BY o CC BY-SA (nunca NC ni ND), con las mismas reglas de 3c.
- **Descripción:** `📍 Cómo funciona` cuando no hay versión del Gobierno, y siempre `📍 Lo que falta`. Hashtags con `#NuevosMundosPosibles` y `#DialMedio` al final.
- Ejemplo: `ejemplo/nuevos-mundos-muestra.json` (muestra de diseño, sin noticia real).

## 1. Investigar y verificar (antes de escribir una sola lámina)

1. Fijar la fecha real del hecho. "Ayer" u "hoy" se calculan con la fecha actual. Si las fotos pueden ser de días distintos, decirlo en las notas.
2. Buscar el hecho en medios confiables (El Tiempo, El Espectador, La Silla Vacía, Cambio, Infobae, Semana, Blu, Caracol, RCN, agencias) y en fuentes primarias (comunicados, Defensoría, Policía, ministerios, Alcaldía).
3. Cada cifra, cita y nombre debe salir de una fuente primaria o de al menos un medio que lo reporte; si se puede, de dos. Lo que no se encuentre se deja por fuera. Las discrepancias entre medios (horas, cifras) se resuelven con una formulación que no tome partido ("al anochecer", "al menos 500, según la Defensoría") y se anotan para Martín.
4. Nombres institucionales precisos y vigentes. Ejemplo: los antidisturbios son la **Unidad Nacional Antidisturbios (Unadi)** desde la Resolución 03226 del 13 oct 2026, que reemplazó a la UNDMO y reincorporó al Esmad. En las láminas se escribe "Unadi (antes Esmad)".
5. Redactar con palabras propias. No copiar frases de otros medios.

## 2. Criterio editorial

- **Periodístico, balance y no ataque.** Siempre va la versión oficial o de la contraparte, con cita textual verificada. El enfoque de Martín (p. ej., "fue pacífico") se sostiene con hechos y con calificativos **atribuidos** a una fuente ("pacífico, según la Defensoría").
- **Que se entienda sin contexto (regla de Martín, 20 oct 2026).** Quien ve la pieza puede no saber nada del tema. Cada lámina se entiende sola: es mejor quedar un poco más superficial pero 100 % autoexplicativo.
  - Nada se da por sabido: si hay un plazo, se dice de qué es y por qué existe; si hay una sigla, una entidad, un fondo o un trámite, se explica en pocas palabras la primera vez ("la JEP, el tribunal de paz"; "proposiciones, los cambios que proponen los congresistas").
  - Nada de jerga del Congreso, de la economía o del derecho sin traducir ("conciliación", "en bloque", "ponencia", "decreto").
  - Personas: nombre y qué son, aunque sean conocidas. Hechos anteriores: cuándo y qué pasó ("el terremoto del 10 de agosto").
  - Las cifras grandes se aterrizan cuando se puede ("seis de cada diez pesos").
  - Prueba antes de entregar: leer cada lámina como alguien que no ha visto ninguna otra ni ha oído de la noticia. Si queda una pregunta del tipo "¿de qué?" o "¿por qué?", se reescribe.
- Lo que dicen los carteles lo muestra la foto. Dial no repite insultos ni acusaciones en su propio texto.
- No evitar a ninguna persona de las fotos. No inventar nombres ni cargos.
- **Créditos.** Por defecto todo es de Martín: `Foto: Martín Perea / Dial Medio`. En los videos el generador cambia solo "Foto:" por "Video:". En la descripción: `Fotos: Martín Perea / Dial Medio`, o `Fotos y video: …` si hay video. Si Martín dice que algo es de otra persona (p. ej., Sergio Ruiz), se pone `"credito"` en esa lámina y se ajusta la descripción. Cualquier otro rol que haga falta nombrar (texto, edición) es de Martín, salvo que él diga otra cosa.

## 3. Estructura del carrusel

- Una lámina por foto, en el orden que cuente mejor la historia. **Portada** = la foto más fuerte y representativa. Después, el desarrollo y el contexto (qué se retiró, quién, por qué). Luego, la versión oficial en su propia lámina. **Cierre** = el desenlace o lo que sigue. Y siempre, al final, la lámina `cta` con la pregunta para comentar.
- Si Martín manda una sola foto, se hace solo la portada.
- **Formato: todo en vertical 4:5 (1080 × 1350) y todas las láminas iguales.** Lo decidió Martín el 18 oct 2026: en horizontal se veían muy pequeñas en el celular, y 4:5 es lo más grande que Instagram muestra en el feed. El generador lo aplica solo si el JSON no trae `formato`. Si la pieza es **un solo video**, el defecto es 9:16 (reel / TikTok). Solo se usa otro formato si Martín lo pide (`"formato": "9:16"`, `"1:1"` o `"original"`).
- **Recorte (lo más importante de cada lámina):** de una foto horizontal, 4:5 se queda con el 45 % del ancho. Por cada foto se decide qué es lo esencial (la persona, el cartel, el gesto, el contraste entre dos grupos) y se pone `"foco": [x, 0.5]`, con `x` = el centro horizontal de eso en fracciones de la foto original (p. ej. `0.57`). Hay que comprobar que el recorte no corte el texto de un cartel ni una cara.
- **Cuando el texto taparía lo esencial:** si el cartel o la persona están abajo, `"posicion": "arriba"` sube el bloque de texto bajo el logo (con degradado arriba). Si están a la derecha, `"ancho": 0.42` deja el texto en una columna a la izquierda.
- Límites de texto (en caracteres, con espacios):
  - Título: hasta 90. Lleva 1 a 3 palabras de acento entre asteriscos (`*danza y carteles*`), que salen sobre la franja brasa. El acento es la idea central del enfoque, no un adorno.
  - Titular interior (opcional, `"titulo"` en láminas con foto): de 2 a 5 palabras ("550.000 en la calle", "Agua a presión"). Le da a cada lámina su propia idea; el `texto` la desarrolla.
  - Bajada (solo portada): hasta 120. Dos frases: el hecho clave y el desenlace.
  - Rótulo (interiores): de 1 a 4 palabras, sin punto ("Frente al museo", "La versión del Gobierno", "Al anochecer").
  - Texto interior: hasta 110. Con `"ancho"` reducido, hasta 80.
- `"sello"`: **"Al aire"**, siempre (es el "en vivo" de la radio y cabe en vertical). `"meta"`: `CIUDAD · DD MES AAAA` en mayúsculas.
- **Formato 9:16 (historias, reels, TikTok):** el generador ya deja libre la franja de abajo y el borde derecho, donde Instagram y TikTok ponen sus botones. En esos casos el texto debe ser todavía más corto: título de hasta 70 caracteres.

## 3b. Videos

- Si Martín manda un video, la lámina lleva el video en `"foto"` (`"foto": "fuentes/clip.mp4"`; también sirven .mov, .m4v, .webm…). Sale el **video completo**, con su audio, con la misma colorización (convertida en LUT y medida sobre varios fotogramas para que no cambie a mitad del video), la misma viñeta y el mismo diseño encima durante todo el video.
- Un video solo suele ir con `"tipo": "portada"` (titular + bajada). Si va dentro de un carrusel con fotos, se trata como cualquier otra lámina, en su lugar del orden. Instagram admite carruseles mixtos.
- Un video solo sale en 9:16. Dentro de un carrusel sale en 4:5, como las fotos. El `foco` se usa igual que en las fotos.
- Salida: MP4 H.264 + AAC, ~6 Mbps (unos 45 MB por minuto). Un minuto tarda de 1 a 3 minutos en procesarse.
- Para revisar, sacar un fotograma del resultado (el generador usa ffmpeg; `ffmpeg -ss 3 -i salida.mp4 -frames:v 1 f.png`) y mirarlo con los mismos criterios de la sección 5.

## 3c. Láminas sin foto y fotos de terceros

- **Láminas sin foto:** ver "Diseño: Al Aire v2" (estilos `pais`, `citas` y `analisis`). Hay que mantener el texto corto: si algo se sale del cuadro, se recorta el texto, no la letra.
- **Fotos de otros:** solo con licencia libre (Wikimedia Commons: CC0, CC BY, CC BY-SA) o con permiso escrito del autor. Nunca fotos de agencias (AFP, Reuters, AP, EFE, Colprensa) ni capturas de otros medios, aunque se les ponga el crédito.
  - Hay que pedirle permiso a Martín antes de descargar, con el nombre del archivo, la fuente y el peso.
  - Hay que verificar el lugar y la fecha de cada foto (la descripción de Commons y su coherencia con lo que reportan los medios) y descartar las dudosas: PNG pequeños con aspecto de captura de pantalla, o fotos sin fecha.
  - El crédito en la lámina lleva autor, licencia, lugar y fecha: `Foto: Jorge Jaramillo · CC BY-SA 4.0 · París, 17 oct`. Si la foto es de otro día que el hecho del texto, el texto no puede dar a entender que la foto muestra ese hecho.
  - CC BY-SA obliga a compartir la lámina con la misma licencia: se dice en la descripción ("Las láminas 1 y 2 se comparten bajo CC BY-SA 4.0").
  - En el .md de la descripción va una tabla con lámina, autor, licencia, lugar, fecha y enlace de Commons.
  - Para buscar: API de Commons (`list=search`, `srnamespace=6`) y `prop=imageinfo&iiprop=url|size|extmetadata` para la licencia, el autor y la fecha. Se descarga a un ancho razonable con `Special:FilePath/<archivo>?width=2400`.

## 4. JSON de la noticia

```json
{
  "salida": "salida",
  "prefijo": "planton-museo",
  "sello": "Al aire",
  "meta": "BOGOTÁ · 17 OCT 2026",
  "credito": "Foto: Martín Perea / Dial Medio",
  "semilla": 17,
  "laminas": [
    {"tipo": "portada", "foto": "fuentes/foto-6.jpg", "foco": [0.43, 0.5],
     "titulo": "Con *danza y carteles*, cientos defendieron las obras retiradas del Museo Nacional",
     "bajada": "La Defensoría calificó el plantón de pacífico. Al anochecer, una tanqueta antidisturbios lo dispersó con agua."},
    {"foto": "fuentes/foto-5.jpg", "foco": [0.45, 0.5], "ancho": 0.42, "rotulo": "Arte en la calle",
     "texto": "Máscaras, disfraces y carteles impresos: la protesta se hizo con humor."},
    {"foto": "fuentes/foto-4.jpg", "foco": [0.5, 0.5], "posicion": "arriba", "rotulo": "Bajo la lluvia",
     "texto": "Aun con lluvia, el plantón siguió hasta el anochecer."}
  ]
}
```

Ejemplos aprobados: `ejemplo/2026-10-18-protestas-mundo.json` (carrusel completo v2, con los tres estilos sin foto) y `ejemplo/2026-10-17-planton-museo.json`.

Opciones por lámina:

- `foco`: ver la sección 3. Va en todas las láminas recortadas.
- `posicion`: `"arriba"` cuando abajo está lo que no se debe tapar.
- `ancho`: fracción del ancho para el bloque de texto (por defecto, todo el ancho en vertical). Bájalo (0.38 a 0.55) cuando lo importante esté a la derecha; el generador añade solo una sombra lateral para que la columna se lea.
- `escala`: tamaño del titular de la portada (por defecto 1.0). Con una columna angosta, usar 0.8 para que el titular no se parta en demasiadas líneas (máximo 6).
- `ajuste`: solo si una foto queda mal, `{"exposicion": 0.3, "calidez": -0.5, "contraste": 0.9, "saturacion": 1.05}`.
- `formato`: ver la sección 3 (normalmente no se pone).
- `persona`: rótulo de nombre y cargo para quien aparece en la foto y es noticia (una ministra, un vocero, un entrevistado), como los de La Silla Vacía. Formato: `{"nombre": "Iris Marín", "cargo": "Defensora del Pueblo", "x": 0.55, "y": 0.62}`. `x` e `y` son el punto (en fracciones) adonde apunta el piquito, justo debajo de la barbilla. El rótulo cuelga hacia abajo desde ahí, así que no debe chocar con el bloque de texto. Admite una lista para varias personas. Solo se usa con nombre y cargo verificados; a los manifestantes anónimos no se les pone.
- `credito`: cambia el crédito de esa lámina (p. ej., `"Foto: Sergio Ruiz / Dial Medio"`).

**Sin grano ni ruido:** la imagen va limpia (el grano se veía como baja calidad; lo decidió Martín el 18 oct 2026). Solo hay una viñeta muy suave. `semilla` se conserva por compatibilidad (el día del hecho).

## 5. Revisar (obligatorio)

Mirar cada JPG generado. Revisar:

1. El texto no tapa caras ni el texto de los carteles importantes. Si los tapa, usar `ancho`, cambiar el orden o elegir otra foto para esa lámina.
2. Nada se sale del cuadro y no quedan líneas de una sola palabra en el título.
3. El color se ve natural: ni lavado ni quemado. Si no, usar `ajuste`.
4. Se lee a tamaño de celular: imaginar la lámina a 390 px de ancho.

Corregir y regenerar solo esas láminas con `--solo=`.

## 6. Descripciones

**Instagram** (máximo 2.200 caracteres, sin enlaces):

1. Primer párrafo: gancho con el enfoque, más qué, dónde y cuándo.
2. Segundo párrafo: el contexto y el dato que explica el porqué.
3. `📍 La versión del Gobierno` (o de la contraparte): la cita verificada.
4. `📍 Cómo terminó` (o `📍 Qué sigue`): el desenlace, con los calificativos atribuidos.
5. `Fotos: Martín Perea / Dial Medio`
6. Máximo 5 hashtags, siempre con `#DialMedio` al final.

**TikTok** (de 400 a 700 caracteres): la misma historia en un solo párrafo con un emoji al principio, más 4 a 6 hashtags terminando en `#DialMedio`.

Guardar todo en `<prefijo>-descripcion.md` con una sección final **Fuentes (para Martín, no se publican)**: medio, fecha, qué dato sale de ahí y URL.

## 7. Entregar (en este orden y sin pedir confirmación)

1. Las láminas y los videos (y el `.zip`) para descargar, numerados en el orden de subida.
2. La descripción de Instagram en un bloque de código, para copiarla con un toque.
3. La descripción de TikTok en otro bloque de código.
4. Notas breves: dudas, discrepancias entre fuentes, qué se dejó por fuera y por qué.

Solo se pregunta antes de producir si falta un dato que impide publicar (p. ej., no se encuentra nada sobre el hecho). Si no, se decide con estas reglas y se avisa en las notas.

## Mantenimiento

Si se cambia el generador o este archivo en el PC de Martín, se hace commit y push a `dialmedio/dial-noticias` (main) para que el kit público quede igual.
