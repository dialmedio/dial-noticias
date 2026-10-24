# Sistema de noticias del día · Dial Medio

Martín manda foto(s), contexto y enfoque. Claude investiga, verifica, arma el carrusel con `dial_noticias.py` y entrega las imágenes más las descripciones listas para subir. **Este archivo es la fuente de verdad: no rediseñar, no cambiar tamaños ni colores. Solo se escriben el JSON y los textos.**

## 0. Preparar

- **Kit público:** https://github.com/dialmedio/dial-noticias. En un sandbox: `git clone --depth 1 https://github.com/dialmedio/dial-noticias` (o bajar `https://github.com/dialmedio/dial-noticias/archive/refs/heads/main.zip`). Si no hay internet en el sandbox, pedirle a Martín que adjunte el zip del kit.
- **En el PC de Martín (Claude Code):** el kit está en `D:\Claude Code\dial-noticias\`. Las fotos van a `D:\AA Dialmedio\Noticias\Al Aire\<AAAA-MM-DD> <Tema>\fuentes\` y el JSON a `noticias/<AAAA-MM-DD>-<tema>.json`, con `salida` = la carpeta de la noticia.
- **En el sandbox:** ejecutar `pip install pillow numpy fonttools` si falta algo (fontTools da el kerning; sin él todo funciona, con las letras menos ajustadas) y trabajar con rutas relativas: el JSON va junto a las fotos (o con rutas relativas a ellas), y la salida por defecto es `salida/` junto al JSON. Los videos usan ffmpeg: si no está instalado, el generador instala `imageio-ffmpeg` por su cuenta.
- Uso: `python dial_noticias.py <noticia>.json [--solo=2,4]`. Genera `<prefijo>-NN.jpg` (o `.mp4` si la lámina es un video). Con `--zip` agrega `<prefijo>.zip` con todo: solo en el flujo del celular, para bajar el carrusel de una vez; en el PC no se usa (Martín, 25 oct 2026: ocupa espacio sin necesidad).

## Sistema común v3: una familia, seis voces (24 oct 2026)

Martín pidió revisar todas las líneas juntas, como se ven en el feed, para que queden al mismo nivel, elegantes y coherentes, y sobre todo que se vean lo menos "Claude", robóticas y digitales posible. Lo común lo hacen tres módulos que usan todas las líneas; cada línea conserva su voz (color, letra y material).

**Lo que delataba lo digital, y ya no se usa:** la mono en mayúsculas para rótulos, créditos y numeración; las cajas perfectas tipo botón; el "01, 02" de las listas; las texturas de ruido en una sola escala (el cianotipo con puntos como estrellas y bordes barridos, el ruido SVG del papel); las ondas concéntricas; la foto en tarjeta redondeada; el negro puro de pantalla con un acento neón; las letras sin kerning.

- **Kerning real** (`oficio.py`): Pillow sin libraqm no leía el kerning de las fuentes y pares como "Lo", "Te" o "r," quedaban abiertos. Ahora `dn.fuente()` devuelve una fuente que mide y dibuja con el kerning de la instancia exacta (ancho y peso), leído con fontTools. Si fontTools no está, todo sigue funcionando sin kerning.
- **Materiales** (`materia.py`): cada línea se "imprime" con un proceso físico distinto. Al Aire, periódico y tipo de madera (trama de semitono de verdad, franjas y cajas con tinta impresa, papel rasgado con su fibra); Termómetro, papel reciclado con motas; Arte y memoria, cartulina negra de álbum; Nuevos mundos, cianotipo a brocha sobre papel de archivo (`cianotipo.py`); Tecnología, negro de imprenta. La textura vive en los campos de color y en los elementos gráficos, nunca sobre las fotos ni sobre el texto corrido (las fotos siguen sin grano, como pidió Martín).
- **Símbolo común:** el aro de Dial (marca v4) con el punto en la estación de cada línea, delante del nombre: Al Aire 0° (arriba, como el foco de una cabina de radio), Tecnología 45°, Termómetro 90°, Arte −90° y Nuevos mundos −45°. El punto siempre va en la mitad de arriba (abajo a la derecha el aro parece una Q).
- **Rueda de color:** brasa (Al Aire), eucalipto (Termómetro), violeta de sello (Tecnología), azul cianotipo (Nuevos mundos) y ámbar (Arte); carbón, papel y terracota son de todas. Cada línea tiene un color dominante y uno de acento, planos, nunca en degradado.
- **Créditos y fuentes:** en letra de texto pequeña y en caja normal, como el pie de foto de un diario (ya no en mono y mayúsculas), en el mismo lugar en todas las líneas. Si el crédito es largo, la letra baja un punto en vez de cortarse.
- **Antetítulos y etiquetas:** versales con interletra en la letra de la línea, nunca mono. El antetítulo va en el color de la línea (en papel sobre las fotos), sin símbolo delante. La letra pequeña sobre fotos lleva un halo blando, no una sombra corrida.
- **Listas:** con las cifras de la letra de la línea (condensada en Al Aire, cursiva serif en Termómetro y Nuevos mundos, Archivo fina en Tecnología), sin el cero delante.
- **Cierre:** la pregunta, una sola línea "Comenta · Guarda · Comparte" sin cajas (la primera palabra en el color de la línea) y la firma; la cuenta en letra de texto.
- **El acento no va en todas las láminas.** Resaltar una palabra en cada título es lo que más hace ver un carrusel como plantilla. En la portada va siempre; adentro, solo en las láminas que llevan la idea central (dos más, como mucho, por carrusel). Los demás títulos se sostienen con tamaño y peso.
- **Fotos:** la misma colorización de Dial en todas las líneas (también en Nuevos mundos y Tecnología, que antes no la tenían). Encima, cada línea pone su tratamiento: revelado hondo en Arte, blanco y negro de mezcla de canales en Tecnología, cianotipo a pedido en Nuevos mundos.
- **Pruebas:** `python dial_noticias.py <noticia>.json --salida=<carpeta>` genera en otra carpeta sin pisar la de la noticia.

## Diseño: Al Aire v2 (vigente desde el 18 oct 2026; ajustes v3 del 24 oct)

Lo aprobó Martín con el carrusel "Protestas en el mundo". Referentes: Mutante (campos planos, titulares condensados, collage en semitono, etiquetas en caja) y La Linterna de Cali (tipos de madera, tinta de prensa). Lo dibuja `al_aire.py`; `dial_noticias.py` lo usa por defecto (`"estilo": "v1"` vuelve al diseño anterior).

- **Cabecera fija** en todas las láminas: caja brasa impresa con el aro de Dial (punto arriba, "en el aire") y `AL AIRE` en versales condensadas; luego `meta` (lugar · fecha) en versales con halo, sin caja (v3: la caja carbón con mono se veía de interfaz); el logo arriba a la derecha.
- **Color:** la brasa `#E58A3A` es el color de Al Aire (el manual ya la reserva para lo "en vivo"). Terracota, carbón y papel, como siempre. No se agregan colores.
- **Titulares:** Instrument Sans 700 al 75 % de ancho (condensada), caja mixta. El acento (`*así*`) va en carbón sobre una franja brasa. Las líneas se equilibran solas.
- **Rótulos:** versales condensadas dentro de una caja impresa (papel sobre fotos, carbón sobre terracota): la caja de Mutante, con el canto y la tinta de una impresión. Créditos y fuentes abajo, en letra de texto pequeña (v3: ya no en mono).
- **Láminas sin foto** (`"tipo": "texto"`), según `estilo` (si no se pone, se deduce):
  - `pais`: campo terracota con el `titulo` en tipo de madera (papel, con la pasada corrida en carbón), `rotulo`, `texto`, `items` numerados y `citas` en serif. Para países o lugares sin foto libre.
  - `citas`: papel limpio, sin textura en las letras. Comillas grandes en terracota, la cita en Sans 600 y el autor en versales condensadas. Es la lámina de "la versión del Gobierno".
  - `analisis`: carbón con una foto en semitono brasa (`"semitono": "fuentes/x.jpg"`, `"foco_semitono": [x, y]`) con borde de papel rasgado (con la franja de fibra que deja el desgarro), el `titulo` con franja, `items` numerados con cifras de titular y `cierre` con filete. Para la lámina de análisis o cierre. Sin `semitono`, el título sube.
  - `cta`: **siempre la última lámina** (desde el 19 oct 2026). Carbón con un signo de pregunta grande en tipo de madera terracota, rótulo `TU OPINIÓN`, la `pregunta` en titular de impacto (con *acento*), un `texto` opcional que la aterriza, la línea `COMENTA · GUARDA · COMPARTE` en versales (sin cajas desde la v3) y la firma (logotipo, "Sintonizar es conversar." y @dialmedio). La pregunta es abierta, sobre el tema de la pieza y **sin tomar partido** (p. ej. "¿*Negociar o someter*? ¿Cuál crees que es el camino hacia la paz?"). La misma pregunta va al final de las dos descripciones, antes de los créditos.
- **Rótulo de persona (v2):** un punto brasa sobre la persona y una guía horizontal hacia dos cajas planas, como la cabecera: el nombre (papel, titular condensado) y el cargo (carbón, versales condensadas). `"persona": {"nombre", "cargo", "x", "y", "lado"}`: `x`, `y` es el punto, **sobre el hombro o el pecho, nunca sobre la cara**; `lado` (`"izq"` o `"der"`) es hacia dónde sale el rótulo. Hay que elegir el lado con espacio libre, sin tapar otras caras. El rótulo queda centrado a la altura del punto.
- **Franja del acento:** se pintan todas las franjas antes que el texto, para que las letras que bajan (g, j, p, q, y) de la línea de arriba no queden cortadas. La puntuación pegada al acento (¿ ? , :) entra en la franja.
- **Trama de semitono (v3, 24 oct):** punto euclidiano a 45°, con ganancia de punto y el borde comido por la fibra, sobre carbón entintado (`materia.semitono`); antes eran círculos perfectos dibujados uno por uno.
- **Texturas:** solo de impresión y evidentes. Tipo de madera (v3, 19 oct 2026): borde nítido y mordido, veta horizontal larga, huecos de canto nítido y poros sueltos; la segunda pasada, corrida y en otra tinta, solo asoma por fuera de la letra. Moteado amplio en los campos planos. Nunca grano sobre las fotos ni en el texto corrido.

## Línea Termómetro, antes Nuevos Mundos Posibles (v2, 22 oct 2026)

Desde el 23 oct 2026 es la línea de clima y ambiente de Al Aire (denuncias, crisis climática, soluciones y ciencia) y se llama **Termómetro**. La clave interna sigue siendo `"seccion": "nuevos-mundos"`.

Buenas noticias: conservación, ciencia y biología, clima, comunidades y economías propias, ciudades que cambian. Es una línea propia de Al Aire, con corrida de propuestas los lunes y los jueves. Se activa con `"seccion": "nuevos-mundos"` arriba en el JSON (sin `"seccion"` todo sale como Al Aire, idéntico). La dibuja `nuevos_mundos.py`, con la misma estructura de Al Aire (cabecera, logo, crédito abajo, lámina final de pregunta) y un estilo propio.

La v1 (verde brote, cuadrícula de libreta, grabado de línea) la descartó Martín el 22 oct: "muy predecible y los cuadros no funcionan". Pidió suavidad, elegancia, un toque de sutileza, coherente con Dial y con **el verde y el naranja juntos**. Referentes: The Guardian, La Linterna y Mutante.

- **Titulares en Instrument Serif** (la serif de Dial). El acento (`*así*`) va en cursiva **sobre una franja**: sobre fotos, franja eucalipto con la cursiva en papel (v3, 24 oct: con la franja brasa, en la rejilla del perfil una portada de Termómetro no se distinguía de una de Al Aire); brasa con cursiva carbón sobre los campos verdes y en el `destacado`; salvia sobre papel (22 oct: la cursiva naranja sola no siempre se leía). Las franjas se pintan antes que el texto, para no tapar las letras de la línea de arriba. Lo mismo en las citas.
- **Color:** eucalipto `#56705E` (verde suave, hacia el gris) y brasa `#E58A3A`; eucalipto hondo `#2C3E32` en el cierre; papel reciclado (con sus motas de fibra, `materia.papel("reciclado")`) en las láminas de datos y de citas; salvia `#C8D3BE` para barras y filetes. Nada de cuadrícula ni de tablas con bordes.
- **Sin cajas (22 oct, pasada final):** Martín sintió las cajas tipo botón y la mono en frases "muy digitales, muy genéricas". La cabecera es de periódico: el aro de Dial con el punto brasa a las tres (v3; antes, la hoja) y *Termómetro* en serif cursiva, el logo, un filete fino a todo el ancho y la fecha en versalitas debajo. Sobre fotos, un velo más fuerte arriba y una sombra mínima en la letra pequeña.
- **Antetítulos, etiquetas, autores, cargos y acciones del cierre** en Instrument Sans espaciada (versalitas), sin la hoja delante. Desde la v3 no queda mono: los años de la serie van en cursiva serif, los créditos y la cuenta en letra de texto y el pie de foto de la banda en cursiva.
- **Franja impresa:** el borde muerde un poco y la tinta carga desigual, como un resaltador sobre papel; no es un rectángulo de pantalla.
- **Fotos en las láminas de datos:** banda arriba **a color**, que se entienda a primera vista (la Amazonía en riso "parecía una mancha"). El riso de dos tintas queda como opción con `"riso": true`.
- **Fotos:** que sean fuertes y profesionales (Martín, 22 oct): selva, árboles, tala o fuego que impacten, aunque no sean exactamente del lugar de la noticia (el crédito dice dónde y cuándo). Si la noticia toca una elección o a personas públicas, van sus fotos.
- **Estilos** (`"estilo"`; si no se pone, se deduce):
  - `portada` y fotos interiores: como en Al Aire, con el titular en serif y `rotulo` como antetítulo.
  - `ficha` (`"tipo": "texto"`): papel con, en orden y todo opcional, la banda en riso (`semitono`, `foco_semitono`, `pie_foto`), `rotulo`, el **dato** grande en serif eucalipto, `dato_pie`, `destacado` (la frase que explica la lámina, p. ej. "41,8 % menos que un año antes", en cursiva sobre franja brasa: Martín pidió resaltar así el dato clave), `titulo`, `texto`, `campos` `[[etiqueta, valor]]` en lista con filetes, `items` numerados en cursiva y `cierre` con filete brasa. Sin foto, el contenido se centra (sirve de portada cuando no hay fotos). `"alto_foto"` cambia el alto de la banda (0.4 por defecto). También hace las veces de `analisis`.
  - `serie`: el cambio grande (`dato`, p. ej. "−74 %"), `dato_pie` y barras horizontales: `"serie": [["2021", 13038], …]`, `"unidad"`. La última barra va en brasa. Para comparar periodos (p. ej. gobiernos), cada fila lleva un tercer valor con su grupo y `"grupos"` da los dos nombres en orden (hueso oscuro y salvia, con leyenda).
  - `lugar` (o `pais`): campo eucalipto con el nombre en serif cursiva grande, `rotulo`, `texto` e `items`; opcional, banda en riso arriba.
  - `citas`: hueso, comillas grandes en brasa, la cita en serif (el acento con `*…*`) y el autor en versalitas eucalipto.
  - `paises`: varios lugares uno debajo del otro (p. ej. "No es solo Brasil"): `rotulo`, `titulo` y `"lugares": [{"nombre", "dato" (opcional, en brasa a la derecha), "texto"}]`. Cada texto se entiende solo (qué es el lugar, qué pasó, según quién).
  - `dos`: dos personas con el mismo trato (p. ej. los candidatos de una elección): retratos del mismo tamaño lado a lado, nombre y cargo en cada uno, y abajo la banda eucalipto con `rotulo`, `titulo` y `texto`. `"personas": [{"foto", "foco", "nombre", "cargo"}, …]`; La cabecera va en su propia franja verde y las fotos empiezan debajo, para no tapar caras; `"alto_fotos"` (0.5 por defecto) si el texto es largo. Fotos de los dos en acción y parecidas entre sí (p. ej. ambos hablando ante un micrófono), no un retrato oficial contra una foto de campaña. Orden neutral (alfabético por apellido) y la misma medida en las dos descripciones.
  - `cta`: eucalipto hondo, el signo en cursiva brasa, la pregunta en serif y la firma.
- **Criterio de las denuncias:** pruebas verificables (datos oficiales o independientes, fallos, investigaciones), la versión de la empresa o autoridad señalada y cuidado de las fuentes amenazadas; en la descripción, `📍 Qué responden` en lugar de `📍 Lo que falta`.
- **Criterio de las buenas noticias:** que esté probado, no solo anunciado; los límites van en la pieza (una lámina de "lo que falta"); sin maquillaje verde (nunca solo el comunicado de una empresa o un gobierno sobre sus logros). Ciencia: nombre común y científico, y "especie nueva" solo si está descrita formalmente.
- **Noticias con elecciones (Martín, 22 oct):** la elección puede ser el eje de la pieza. Se cuenta con datos por gobierno (oficiales y atribuidos), los planes de los dos candidatos con la misma medida, sus frases textuales y las advertencias atribuidas a quien las hace; si sirve, el contexto de la región. Dial no pone el calificativo: lo sostienen los datos.
- **Mensajes de Martín:** si pide una dedicatoria o un mensaje, se escribe con palabras propias de Dial a partir de su idea, no copiando literal su nota (22 oct).
- **Fotos de especies:** también de iNaturalist, solo CC0, CC BY o CC BY-SA (nunca NC ni ND), con las mismas reglas de 3c.
- **Descripción:** `📍 Cómo funciona` cuando no hay versión del Gobierno, y siempre `📍 Lo que falta`. Hashtags con `#TermometroDial` y `#DialMedio` al final.
- Ejemplos: `ejemplo/nuevos-mundos-muestra.json` (muestra de diseño, sin noticia real).

## Línea Arte y memoria (v1, 22 oct 2026; nombre provisional)

El arte como parte de un proceso histórico, político o simbólico: fotografía, música, pintura, grabado, escultura, patrimonio y artes híbridas. Línea propia de Al Aire, con corrida de propuestas los martes (mesa y criterio en `D:/Claude Code/dial-arte/`). Se activa con `"seccion": "arte"`; la dibuja `arte.py`, con la misma estructura de Al Aire (cabecera, logo, crédito abajo, lámina final de pregunta). El nombre ("Arte y memoria") lo decide Martín: se cambia en la constante `NOMBRE`.

Martín pidió un diseño "más inspirado para mostrar fotografía", con un tinte más oscuro y *aesthetic*, nada robótico, digital ni predecible. La idea es el cuarto oscuro y el álbum de fotos:

- **Fondo:** negro cálido `#130F0D`, impreso como cartulina negra de álbum (`materia.papel("negro")`: formación honda y fibras claras sueltas). Texto en papel de copia `#EFE6D8`; el acento en **ámbar** `#E8B48A` (la luz de seguridad del cuarto oscuro); la terracota clara de Dial para el esquinero y las comillas.
- **Titulares en Instrument Serif**, el acento (`*así*`) en cursiva ámbar **sin franja** (sobre el negro se lee solo). Antetítulos en sans espaciada ámbar y cartelas en sans espaciada; créditos en letra de texto (v3: sin mono).
- **Símbolo:** el aro de Dial con el punto ámbar a las nueve (v3). El esquinero de álbum queda para sujetar las obras y las copias, no delante de cada antetítulo.
- **Cabecera:** aro + *Arte y memoria* en serif cursiva, el logo y, debajo, el **lugar y la época de la historia** en versalitas (`meta`: `CIUDAD DE MÉXICO · 1912`), no la fecha de hoy.
- **Fotos a sangre** (`portada`, `foto`): reveladas más hondo (algo menos de color, sombras cálidas, viñeta de copia) y un velo largo hacia el negro. `"revelado": 0.5` lo suaviza.
- **Las obras se respetan:** una pintura, un grabado o una foto de archivo no se recortan ni se colorizan.
- **Estilos:**
  - `portada` y `foto`: como en Al Aire, con el titular en serif y `rotulo` como antetítulo.
  - `obra`: la obra entera (`"obra": "fuentes/x.jpg"`) como copia con borde de papel, sombra y esquineros de álbum, y debajo la **cartela de museo**: `"cartela": {"titulo", "autor", "fecha", "tecnica", "lugar"}`, más `rotulo` y `texto`. `"borde": 0` quita el borde (pinturas, objetos); `"esquineros": false` los quita; `"giro"` la inclina.
  - `copias`: dos o tres fotos como copias sueltas sobre la mesa, un poco giradas (`"copias": [{"foto", "giro"}]`), sin recorte; debajo `rotulo`, `titulo` y `texto`.
  - `epoca`: un año o dato enorme en cursiva ámbar (`dato`), `rotulo`, `titulo`, `texto` y, si se quiere, `"tiempo": [["1890", "texto"], …]` (línea de tiempo). Con `"foto"`, una copia de archivo arriba.
  - `citas`: la voz del artista, en serif con comillas terracota y el autor en versalitas ámbar.
  - `cta`: la pregunta en serif, el signo en cursiva terracota, `TU MIRADA` y la firma.
- **Créditos:** obra, autor, año y licencia (`José Guadalupe Posada, Calavera maderista, ca. 1910 · National Gallery of Art · CC0`). Derechos de las obras: ver el perfil de la línea.
- **Descripción:** `📍 La obra` (ficha) en lugar de la versión del Gobierno y `📍 Hoy`; hashtags con `#ArteYMemoria` y `#DialMedio` al final.
- Ejemplo: `ejemplo/arte-muestra.json` (muestra de diseño, sin historia real).

## Línea Tecnología y poder (v3, 24 oct 2026; pendiente del visto bueno de Martín)

La política de la tecnología (hackeos, vigilancia, regulación, plataformas, minerales críticos), sobre todo internacional. Sale los miércoles desde la mesa de Al Aire (tema `tecnologia`). Se activa con `"seccion": "tecnologia"`; la compone `tecnologia.py` en **HTML/CSS y la renderiza Chrome** (como el Expediente): necesita Chrome instalado (en el PC de Martín está; en un sandbox sin Chrome, usar el diseño de Al Aire). Martín pidió algo minimalista inspirado en X, con tipografía elegante e impactante; cada sección con su plantilla para que el perfil no se sienta repetido.

La v2 (Geist, negro de pantalla, verde señal, mono, cursor y foto en tarjeta redondeada) era la línea más digital de todas; en la revisión de conjunto Martín pidió otro color ("el verde de tecnología no me mata"). La v3 es la misma página negra y minimalista, pero impresa:

- **Color: violeta de sello** (`#9A8CD6` sobre negro; la tinta plena es `#5B3FC4`): el de los sellos oficiales de notarías, registradurías y juzgados, la marca con la que el poder certifica. Plano, nunca en degradado, y solo en el acento (`*así*`), los antetítulos, las cifras de las listas y el punto del aro.
- **Tipografía:** Archivo (Omnibus-Type, Buenos Aires, OFL), grotesca con eje de ancho. Titulares en semibold, un poco condensados y apretados, con líneas equilibradas; cifras grandes en Thin expandida; antetítulos en versales semiexpandidas. Sin mono. Nunca menos de 17 px.
- **Fondo:** negro de imprenta cálido con la formación de la tinta (`materia.py`), no el negro puro de una pantalla. Sin franjas ni cajas.
- **Fotos como planchas:** a todo el ancho y con esquinas rectas, en blanco y negro de mezcla de canales después de la colorización de Dial (`"color": true` las deja a color).
- **Símbolo:** el aro de Dial con el punto violeta a 45°.
- **Láminas:** `portada` (titular y bajada arriba; la foto a todo el ancho hasta abajo, desde la mitad, o desde `"corte"`), `foto` (la foto arriba a todo el ancho y el texto debajo; `"posicion": "arriba"` invierte; `"alto_foto"` cambia el alto), `post` (lámina de texto: `rotulo`, `titulo`, `texto` y, para "cómo funciona", `items` numerados), `dato` (`dato`, `unidad`, `texto`), `citas` (cita con comillas colgadas en violeta; nunca como si fuera un post de X de alguien real) y `cta`. Numeración 1/7 abajo, como un hilo.
- `"meta"`: `PAÍS · DD MES` (o `MUNDO · DD MES`). Muestra de referencia: `noticias/2026-10-25-tec-muestra-urna-brasil.json`.

## Línea Nuevos mundos posibles (v1, 24 oct 2026; pendiente del visto bueno de Martín)

Salidas al modelo: economías alternativas, otras formas de organizar lo público, investigaciones y experiencias reales (perfil en `dial-al-aire/perfil-nuevos-mundos-posibles.md`). Sale los viernes desde la mesa de Al Aire (tema `nuevos-mundos`). Se activa con `"seccion": "mundos"` (**no** `"nuevos-mundos"`, que es Termómetro); la compone `mundos.py` en HTML/CSS con Chrome, como Tecnología y poder. Martín pidió un diálogo entre el archivo, el solarpunk, lo minimalista y lo elegante de un medio internacional.

- **Idea:** el cianotipo, la impresión al sol con la que se hicieron los primeros libros con fotografías (Anna Atkins, 1843): archivo, sol y naturaleza en una sola técnica.
- **Color:** papel de archivo, azul cianotipo como tinta (acento `*así*` en cursiva azul; en oro sobre fondo cian) y oro de sol. Ninguna otra línea usa azul.
- **Tipografía:** Newsreader (Production Type, OFL) con tamaño óptico, fina en titulares y cómoda en texto; Instrument Sans espaciada para rótulos y créditos; números de lámina en cursiva Newsreader. La mono (IBM Plex Mono) queda solo para la signatura de la tarjeta de catálogo, que era escrita a máquina.
- **Archivo:** cada pieza es una ficha numerada (`"ficha": "01"` en el JSON, sube de a uno por pieza), las fotos llevan pie de lámina ("Lám. 05") y crédito vertical al canto. **Símbolo:** el aro de Dial (marca v4) en la estación de la línea: aro azul (o papel sobre azul) con el punto de oro a las 10:30 (−45°). Los puntos de las estaciones van siempre en la mitad de arriba: abajo a la derecha el aro se lee como una Q.
- **Texturas (v3, 24 oct; generadas, sin descargar nada):** Martín vio la v2 "buena pero muy digital" (bordes barridos como desenfoque, puntos como estrellas). Ahora `cianotipo.py` imita la técnica: la emulsión va en pasadas de brocha horizontales que se montan (donde se montan, el azul es apenas más hondo), con vetas de cerdas por tramos, la brocha que se descarga a lo largo de la pasada, dedos de pincel seco en los extremos, el diente del papel y el azul que sangra al lavar. El papel de las láminas claras es papel de archivo (`materia.papel("archivo")`), no un ruido SVG. El sol de la cifra va impreso en oro y el aro del cierre es un fotograma (la forma que tapó el sol y dejó el papel en blanco). Sin líneas de onda: se veían como un radar de pantalla.
- **Láminas:** `portada` (foto a sangre arriba, titular en papel; el tamaño se ajusta al largo), `foto` (placa + pie; `"tratamiento": "cianotipo"` para fotos de archivo o vestigios), `post` (`rotulo`, `titulo`, `texto`, `items`), `dato` (cifra fina sobre un sol: `dato`, `unidad`, `texto`), `ficha` (tarjeta de catálogo de la investigación: `campos` = lista de [etiqueta, valor], `signatura` arriba a la derecha, `tipo_ficha`), `balance` (`columnas` = [["Lo que muestra", [...]], ["Lo que falta", [...]]]: el criterio de la línea hecho lámina), `citas` y `cta`. `"fondo": "cian"` invierte cualquier lámina de texto para dar ritmo (una por pieza basta). `"fuentes"` en una lámina pone sus fuentes en el pie.
- `"meta"`: `TEMA · LUGAR` (p. ej. `Economía · Brasil`). Muestra: `ejemplo/mundos-muestra.json`.

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

- **La portada (regla de Martín, 24 oct 2026): una sola foto profesional e impactante, un título y una bajada sencillos, y nada más.** Tiene que contar el titular por sí sola, sin leer lo de adentro. Nada de collage, recortes ni varias personas pegadas (el generador los quita de la portada): la portada de Lula y Flávio Bolsonaro del 24 oct, con dos recortes sobre una foto de fondo que no decía nada, le fue mal. Cómo elegir la foto: el momento o la acción que ES la noticia (alguien votando en una elección, la marcha en una protesta, la persona en el gesto que la define), nítida, con fuerza y con resolución (al menos 1.350 px de alto en el recorte, para que no se vea blanda). Si son dos partes, la foto no puede favorecer a una (en una elección, el votante o la urna, no un candidato). Título corto (ideal 2 a 6 palabras, nunca más de 60 caracteres) y bajada de una sola frase sencilla (hasta 90). Si no hay foto así, mejor una lámina sin foto (`pais`) que una foto débil o que no tenga relación.
- Una lámina por foto, en el orden que cuente mejor la historia. **Portada** = la foto más fuerte y representativa (ver la regla anterior). Después, el desarrollo y el contexto (qué se retiró, quién, por qué). Luego, la versión oficial en su propia lámina. **Cierre** = el desenlace o lo que sigue. Y siempre, al final, la lámina `cta` con la pregunta para comentar.
- Si Martín manda una sola foto, se hace solo la portada.
- **Formato: todo en vertical 4:5 (1080 × 1350) y todas las láminas iguales.** Lo decidió Martín el 18 oct 2026: en horizontal se veían muy pequeñas en el celular, y 4:5 es lo más grande que Instagram muestra en el feed. El generador lo aplica solo si el JSON no trae `formato`. Si la pieza es **un solo video**, el defecto es 9:16 (reel / TikTok). Solo se usa otro formato si Martín lo pide (`"formato": "9:16"`, `"1:1"` o `"original"`).
- **Recorte (lo más importante de cada lámina):** de una foto horizontal, 4:5 se queda con el 45 % del ancho. Por cada foto se decide qué es lo esencial (la persona, el cartel, el gesto, el contraste entre dos grupos) y se pone `"foco": [x, 0.5]`, con `x` = el centro horizontal de eso en fracciones de la foto original (p. ej. `0.57`). Hay que comprobar que el recorte no corte el texto de un cartel ni una cara.
- **Cuando el texto taparía lo esencial:** si el cartel o la persona están abajo, `"posicion": "arriba"` sube el bloque de texto bajo el logo (con degradado arriba). Si están a la derecha, `"ancho": 0.42` deja el texto en una columna a la izquierda.
- **Cifras que no se parten:** entre el número y su unidad va un espacio duro (U+00A0): `5,2 %`, `24.648 kilómetros`. El generador no corta ahí.
- **La letra no tiene ² ni ³:** se escribe "kilómetros cuadrados" (o se pone la unidad en el texto de apoyo), nunca "km²".
- Límites de texto (en caracteres, con espacios):
  - Título: hasta 60 en la portada (ideal 2 a 6 palabras). Lleva 1 a 3 palabras de acento entre asteriscos (`*danza y carteles*`), que salen sobre la franja brasa. El acento es la idea central del enfoque, no un adorno. **Adentro no va en todos los títulos** (v3): solo en las láminas con la idea central, dos como mucho por carrusel; los demás títulos van sin asteriscos.
  - Titular interior (opcional, `"titulo"` en láminas con foto): de 2 a 5 palabras ("550.000 en la calle", "Agua a presión"). Le da a cada lámina su propia idea; el `texto` la desarrolla.
  - Bajada (solo portada): hasta 90, una sola frase sencilla (antes eran 120 y dos frases).
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
- `degradado`: `[desde, fuerza]` (p. ej. `[0.3, 0.97]`) en láminas de foto y portada, cuando la foto es clara y la letra no se lee.
- `alto_semitono`: alto de la franja en semitono de la lámina `analisis` (por defecto 0.444; con 4 ítems y cierre, 0.34).
- `recorte`: collage sobre cualquier lámina (desde el 23 oct 2026): una foto pegada con borde de papel, canto rasgado, giro y sombra, que se sale de su franja. `{"foto", "x", "y", "ancho", "alto", "foco", "giro", "pie"}`; `pie` es el nombre en caja brasa. Sirve para poner a una persona sobre el semitono (p. ej. quien denuncia, sobre la foto del denunciado). Desde el 24 oct 2026 admite una lista de recortes (dos personas del mismo tamaño, en orden alfabético por apellido), pero **solo en láminas interiores**: en la portada no van (ver sección 3).
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

1. Las láminas y los videos para descargar, numerados en el orden de subida (y el `.zip`, solo en el celular).
2. La descripción de Instagram en un bloque de código, para copiarla con un toque.
3. La descripción de TikTok en otro bloque de código.
4. Notas breves: dudas, discrepancias entre fuentes, qué se dejó por fuera y por qué.

Solo se pregunta antes de producir si falta un dato que impide publicar (p. ej., no se encuentra nada sobre el hecho). Si no, se decide con estas reglas y se avisa en las notas.

## Mantenimiento

Si se cambia el generador o este archivo en el PC de Martín, se hace commit y push a `dialmedio/dial-noticias` (main) para que el kit público quede igual.
