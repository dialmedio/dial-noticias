# Sistema de noticias del día · Dial Medio

Martín manda foto(s), contexto y enfoque. Claude investiga, verifica, arma el carrusel con `dial_noticias.py` y entrega las imágenes más las descripciones listas para subir. **Este archivo es la fuente de verdad: no rediseñar, no cambiar tamaños ni colores. Solo se escriben el JSON y los textos.**

## 0. Preparar

- **Kit público:** https://github.com/dialmedio/dial-noticias. En un sandbox: `git clone --depth 1 https://github.com/dialmedio/dial-noticias` (o bajar `https://github.com/dialmedio/dial-noticias/archive/refs/heads/main.zip`). Si no hay internet en el sandbox, pedirle a Martín que adjunte el zip del kit.
- **En el PC de Martín (Claude Code):** el kit está en `D:\Claude Code\dial-noticias\`. Las fotos van a `D:\AA Dialmedio\AudiovisualDial\Noticias\<AAAA-MM-DD> <Tema>\fuentes\` y el JSON a `noticias/<AAAA-MM-DD>-<tema>.json`, con `salida` = la carpeta de la noticia.
- **En el sandbox:** ejecutar `pip install pillow numpy` si falta algo y trabajar con rutas relativas: el JSON va junto a las fotos (o con rutas relativas a ellas), y la salida por defecto es `salida/` junto al JSON. Los videos usan ffmpeg: si no está instalado, el generador instala `imageio-ffmpeg` por su cuenta.
- Uso: `python dial_noticias.py <noticia>.json [--solo=2,4]`. Genera `<prefijo>-NN.jpg` (o `.mp4` si la lámina es un video) y `<prefijo>.zip` con todo.

## 1. Investigar y verificar (antes de escribir una sola lámina)

1. Fijar la fecha real del hecho. "Ayer" u "hoy" se calculan con la fecha actual. Si las fotos pueden ser de días distintos, decirlo en las notas.
2. Buscar el hecho en medios confiables (El Tiempo, El Espectador, La Silla Vacía, Cambio, Infobae, Semana, Blu, Caracol, RCN, agencias) y en fuentes primarias (comunicados, Defensoría, Policía, ministerios, Alcaldía).
3. Cada cifra, cita y nombre debe salir de una fuente primaria o de al menos un medio que lo reporte; si se puede, de dos. Lo que no se encuentre se deja por fuera. Las discrepancias entre medios (horas, cifras) se resuelven con una formulación que no tome partido ("al anochecer", "al menos 500, según la Defensoría") y se anotan para Martín.
4. Nombres institucionales precisos y vigentes. Ejemplo: los antidisturbios son la **Unidad Nacional Antidisturbios (Unadi)** desde la Resolución 03226 del 13 oct 2026, que reemplazó a la UNDMO y reincorporó al Esmad. En las láminas se escribe "Unadi (antes Esmad)".
5. Redactar con palabras propias. No copiar frases de otros medios.

## 2. Criterio editorial

- **Periodístico, balance y no ataque.** Siempre va la versión oficial o de la contraparte, con cita textual verificada. El enfoque de Martín (p. ej., "fue pacífico") se sostiene con hechos y con calificativos **atribuidos** a una fuente ("pacífico, según la Defensoría").
- Lo que dicen los carteles lo muestra la foto. Dial no repite insultos ni acusaciones en su propio texto.
- No evitar a ninguna persona de las fotos. No inventar nombres ni cargos.
- **Créditos.** Por defecto todo es de Martín: `Foto: Martín Perea / Dial Medio`. En los videos el generador cambia solo "Foto:" por "Video:". En la descripción: `Fotos: Martín Perea / Dial Medio`, o `Fotos y video: …` si hay video. Si Martín dice que algo es de otra persona (p. ej., Sergio Ruiz), se pone `"credito"` en esa lámina y se ajusta la descripción. Cualquier otro rol que haga falta nombrar (texto, edición) es de Martín, salvo que él diga otra cosa.

## 3. Estructura del carrusel

- Una lámina por foto, en el orden que cuente mejor la historia. **Portada** = la foto más fuerte y representativa. Después, el desarrollo y el contexto (qué se retiró, quién, por qué). Luego, la versión oficial en su propia lámina. **Cierre** = el desenlace o lo que sigue.
- Si Martín manda una sola foto, se hace solo la portada.
- **Formato:** por defecto, la proporción original de cada foto (lado corto 1080 px). Si Martín pide "4:5" (o "9:16", "1:1"), se pone `"formato": "4:5"` arriba en el JSON y, si hace falta, `"foco": [x, y]` por lámina (en fracciones de 0 a 1, p. ej. `[0.6, 0.5]`) para que el recorte no corte al protagonista.
- Límites de texto (en caracteres, con espacios):
  - Título: hasta 90. Lleva 1 a 3 palabras de acento entre asteriscos (`*danza y carteles*`), que salen en serif cursiva terracota. El acento es la idea central del enfoque, no un adorno.
  - Bajada (solo portada): hasta 120. Dos frases: el hecho clave y el desenlace.
  - Rótulo (interiores): de 1 a 4 palabras, sin punto ("Frente al museo", "La versión del Gobierno", "Al anochecer").
  - Texto interior: hasta 110. Con `"ancho"` reducido, hasta 80.
- `"sello"`: **"Al aire"**, siempre (es el "en vivo" de la radio y cabe en vertical). `"meta"`: `CIUDAD · DD MES AAAA` en mayúsculas.
- **Formato 9:16 (historias, reels, TikTok):** el generador ya deja libre la franja de abajo y el borde derecho, donde Instagram y TikTok ponen sus botones. En esos casos el texto debe ser todavía más corto: título de hasta 70 caracteres.

## 3b. Videos

- Si Martín manda un video, la lámina lleva el video en `"foto"` (`"foto": "fuentes/clip.mp4"`; también sirven .mov, .m4v, .webm…). Sale el **video completo**, con su audio, con la misma colorización (convertida en LUT y medida sobre varios fotogramas para que no cambie a mitad del video), el mismo grano, la misma viñeta y el mismo diseño encima durante todo el video.
- Un video solo suele ir con `"tipo": "portada"` (titular + bajada). Si va dentro de un carrusel con fotos, se trata como cualquier otra lámina, en su lugar del orden. Instagram admite carruseles mixtos.
- Se respeta la proporción original del video (lado corto 1080). Si Martín pide otro formato, se usan `formato` y `foco`, igual que en las fotos.
- Salida: MP4 H.264 + AAC, ~6 Mbps (unos 45 MB por minuto). Un minuto tarda de 1 a 3 minutos en procesarse.
- Para revisar, sacar un fotograma del resultado (el generador usa ffmpeg; `ffmpeg -ss 3 -i salida.mp4 -frames:v 1 f.png`) y mirarlo con los mismos criterios de la sección 5.

## 4. JSON de la noticia

```json
{
  "salida": "salida",
  "prefijo": "planton-museo",
  "sello": "Al aire",
  "meta": "BOGOTÁ · 17 OCT 2026",
  "credito": "Foto: Martín Perea / Dial Medio",
  "semilla": 17,
  "formato": null,
  "laminas": [
    {"tipo": "portada", "foto": "fuentes/foto-6.jpg",
     "titulo": "Con *danza y carteles*, cientos defendieron las obras retiradas del Museo Nacional",
     "bajada": "La Defensoría calificó el plantón de pacífico. Al anochecer, una tanqueta antidisturbios lo dispersó con agua."},
    {"foto": "fuentes/foto-8.jpg", "rotulo": "Lo que se retiró", "ancho": 0.44,
     "texto": "Afiches de Pizarro y Jaramillo, candidatos asesinados en 1990, están entre las piezas retiradas."}
  ]
}
```

Opciones por lámina:

- `ancho`: fracción del ancho para el bloque de texto (por defecto 0.72 en horizontal y todo el ancho en vertical). Bájalo (0.38 a 0.45) cuando el texto tape un cartel o una cara en el centro.
- `ajuste`: solo si una foto queda mal, `{"exposicion": 0.3, "calidez": -0.5, "contraste": 0.9, "saturacion": 1.05}`.
- `formato` y `foco`: ver la sección 3.
- `persona`: rótulo de nombre y cargo para quien aparece en la foto y es noticia (una ministra, un vocero, un entrevistado), como los de La Silla Vacía. Formato: `{"nombre": "Iris Marín", "cargo": "Defensora del Pueblo", "x": 0.55, "y": 0.62}`. `x` e `y` son el punto (en fracciones) adonde apunta el piquito, justo debajo de la barbilla. El rótulo cuelga hacia abajo desde ahí, así que no debe chocar con el bloque de texto. Admite una lista para varias personas. Solo se usa con nombre y cargo verificados; a los manifestantes anónimos no se les pone.
- `credito`: cambia el crédito de esa lámina (p. ej., `"Foto: Sergio Ruiz / Dial Medio"`).

`semilla` = el día del hecho, para que el grano sea reproducible.

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
