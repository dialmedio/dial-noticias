"""Afiche militante: técnicas aprendidas del carrusel de contranarrativas (2 nov 2026), ficha 2 de REFERENTES.md.

El referente es un ensayo político de 11 láminas: portada de un solo color con una persona recortada, flores
grandes que se salen del marco y titular en cartel; adentro, texto largo y centrado con un resaltador bajo cada
renglón y una foto pegada abajo. Dial lo traduce a su materia (marca v5): la tinta brasa impresa, la o de pluma
del aro en vez de las flores, la letra de la marca llevada a cartel. Aquí solo las piezas; el uso, en la ficha.

  renglones(img, texto, y0, y1)   texto centrado con una franja de resaltador por renglón; *así* va en negrilla
                                  y cierra la lámina (el remate). Se achica hasta caber y reparte los renglones
                                  parejos, sin viudas
  banda(img, foto, desde)         la foto en blanco y negro como tira de copia pegada abajo, canto rasgado arriba
  retrato(foto, caja, ancho)      la persona en blanco y negro de tono continuo, borde limpio, sin la gente de atrás
  pluma(trazos)                   trazo de pluma de punta ancha al eje del aro: engruesa y adelgaza solo
  anillos(img, lista)             la o de pluma grande, cortada por los bordes, en varias tintas: el marco
  disco(img, c, color)            círculo de la misma tinta más oscura detrás de la persona
  grotesca / titular              Bricolage negra y estrecha a tamaño de cartel, interlineado apretado
  logo_tinta(alto)                la firma en carbón para fondos claros (el punto sigue rojo)

Láminas completas (estilos para un generador de pieza): l_portada, l_texto, l_cierre. ESTILOS las reúne.

Trabajan sobre el lienzo de al_aire (aa.W, aa.H y sus márgenes) en RGBA de PIL."""
import re

import numpy as np
from PIL import Image, ImageDraw

import al_aire as aa
import dial_noticias as dn
import materia as mt

CARBON, PAPEL, BRASA = aa.CARBON, aa.PAPEL, aa.BRASA
RESALTADOR = tuple(round(b * 0.62 + p * 0.38) for b, p in zip(BRASA, PAPEL))  # brasa de resaltador, no plena
BRASA_HONDA = tuple(round(c * 0.8) for c in BRASA)                             # la del disco: la misma tinta, más carga
MISION = ("Dial Medio es un medio independiente y riguroso: no responde a ningún partido y verifica cada dato antes "
          "de publicarlo. Para seguir así necesitamos que nos sigas y compartas esta pieza.")


# ------------------------------------------------------------ texto con franja por renglón

def tokens(texto):
    """[(palabra, negrilla)]; *así* va en negrilla. Parte solo en espacios normales: el espacio duro (U+00A0) une
    «51,7 %» o «47 a 45» para que no se separen."""
    out, neg = [], False
    for w in (w for w in re.split(r"[ \t\r\n]+", texto.replace("*", " * ")) if w):
        if w == "*":
            neg = not neg
        else:
            out.append((w, neg))
    # la puntuación que quedó suelta tras cerrar el asterisco se pega a la palabra anterior
    pegado = []
    for w, n in out:
        if pegado and not any(c.isalnum() for c in w):
            pegado[-1] = (pegado[-1][0] + w, pegado[-1][1])
        else:
            pegado.append((w, n))
    return pegado


def _cortar(toks, f, fb, ancho):
    esp = f.getlength(" ")
    lineas, act, x = [], [], 0
    for w, n in toks:
        ww = (fb if n else f).getlength(w)
        if act and x + esp + ww > ancho:
            lineas.append(act)
            act, x = [], 0
        x += (esp if act else 0) + ww
        act.append((w, n))
    if act:
        lineas.append(act)
    return lineas


def _parejas(toks, f, fb, ancho):
    """El mismo número de líneas, lo más parejas posible (sin viudas)."""
    n = len(_cortar(toks, f, fb, ancho))
    lo, hi = ancho * 0.5, ancho
    for _ in range(16):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if len(_cortar(toks, f, fb, mid)) > n else (lo, mid)
    return _cortar(toks, f, fb, hi)


def _bloque(texto, tam, ancho):
    f, fb = dn.cuerpo(tam, 520), dn.cuerpo(tam, 720)
    parrafos = [_parejas(tokens(p), f, fb, ancho) for p in texto.split("\n\n")]
    paso = tam * 1.3
    alto = sum(len(p) for p in parrafos) * paso + (len(parrafos) - 1) * tam * 0.9
    return f, fb, parrafos, paso, alto


def renglones(img, texto, y0, y1, tam_max=58, tam_min=36, ancho=None, centro=True, color=RESALTADOR, tinta=CARBON):
    """Texto centrado con su franja de resaltador bajo cada renglón. Se achica hasta caber entre y0 y y1 y queda
    centrado en ese alto (o arriba, con centro=False). Párrafos separados por línea en blanco. Devuelve el y final."""
    ancho = ancho or (aa.W - 2 * aa.M - 40)
    tam = tam_max
    while True:
        f, fb, parrafos, paso, alto = _bloque(texto, tam, ancho)
        if alto <= y1 - y0 or tam <= tam_min:
            break
        tam -= 1
    y = y0 + ((y1 - y0 - alto) / 2 if centro else 0)
    esp = f.getlength(" ")
    rects, piezas = [], []
    for p in parrafos:
        for l in p:
            w = sum((fb if n else f).getlength(t) for t, n in l) + esp * (len(l) - 1)
            x = (aa.W - w) / 2
            base = y + tam
            rects.append((x - tam * 0.28, base - tam * 0.86, x + w + tam * 0.28, base + tam * 0.3))
            for t, n in l:
                piezas.append((x, base, t, fb if n else f))
                x += (fb if n else f).getlength(t) + esp
            y += paso
        y += tam * 0.9
    mt.franja(img, rects, color, int(y0 + len(texto)) % 997)
    d = ImageDraw.Draw(img)
    for x, base, t, fu in piezas:
        d.text((x, base), t, font=fu, fill=tinta, anchor="ls")
    return y


# ------------------------------------------------------------ fotos

def banda(img, foto, desde=0.6, foco=(0.5, 0.5), zoom=1.0, semilla=1):
    """La foto en blanco y negro como una tira de copia pegada abajo, desde `desde` (fracción del alto), con el
    canto de arriba rasgado. foto: ruta o imagen. Devuelve el y donde empieza."""
    y_top = round(aa.H * desde)
    h = aa.H - y_top + 30
    foto = (foto if isinstance(foto, Image.Image) else Image.open(foto)).convert("RGB")
    fx, fy = foco
    s = max(aa.W / foto.width, h / foto.height) * zoom
    fw, fh = round(foto.width * s), round(foto.height * s)
    foto = foto.resize((fw, fh), Image.LANCZOS)
    cx = int(min(max(fx * fw - aa.W / 2, 0), fw - aa.W))
    cy = int(min(max(fy * fh - h / 2, 0), fh - h))
    foto = foto.crop((cx, cy, cx + aa.W, cy + h))
    foto = dn.pelicula(foto, 30 + semilla, grano=0.5).convert("L")
    g = np.asarray(foto, np.float32)
    lo, hi = np.percentile(g, 2), np.percentile(g, 98)
    g = np.clip((g - lo) / max(hi - lo, 1) * 255 * 0.92 + 14, 0, 255)  # negro de película, no negro puro
    rgb = np.stack([g * 0.99, g * 0.97, g * 0.93], -1)  # un tibio de copia en papel
    arriba, fibra = mt.rasgado(aa.W, h, 22, 70 + semilla, amplitud=10)
    alfa = np.clip(1 - arriba, 0, 1)
    rgb = rgb * (1 - fibra[..., None]) + np.array((250, 247, 240), np.float32) * fibra[..., None]
    capa = np.dstack([np.clip(rgb, 0, 255), alfa * 255]).astype(np.uint8)
    img.alpha_composite(Image.fromarray(capa, "RGBA"), (0, y_top - 22))
    return y_top


def retrato(ruta, caja, ancho, semilla=1):
    """La persona recortada en blanco y negro de tono continuo (no en trama ni en fotograbado), con el borde limpio:
    la máscara de rembg se aprieta, pierde el halo y se queda solo con la figura más grande (la gente de atrás
    sale). caja: (x0, y0, x1, y1) en fracciones de la foto. La máscara se guarda junto a la foto."""
    from pathlib import Path
    from scipy import ndimage
    ruta = Path(ruta)
    foto = Image.open(ruta).convert("RGB")
    x0, y0, x1, y1 = [round(v * s) for v, s in zip(caja, (foto.width, foto.height) * 2)]
    alta = foto.crop((x0, y0, x1, y1))
    m = aa.silueta(alta, ruta.with_name(f"{ruta.stem}-silueta-{x0}-{y0}-{x1}-{y1}.png"))
    m = np.asarray(m, np.float32) / 255
    etiq, k = ndimage.label(m > 0.5)
    if k > 1:
        tam = ndimage.sum(np.ones_like(m), etiq, range(1, k + 1))
        m = m * ndimage.binary_dilation(etiq == (1 + int(np.argmax(tam))), iterations=6)
    m = np.clip((m - 0.35) / 0.3, 0, 1)  # borde firme, sin el velo gris de la máscara
    m = ndimage.grey_erosion(m, size=(3, 3))
    tam_ = (ancho, round(alta.height * ancho / alta.width))
    alfa = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize(tam_, Image.LANCZOS), np.float32)
    g = np.asarray(dn.pelicula(alta.resize(tam_, Image.LANCZOS), 40 + semilla, grano=0.6).convert("L"), np.float32)
    dentro = g[alfa > 128]
    lo, hi = np.percentile(dentro, 1.5), np.percentile(dentro, 99)
    g = np.clip((g - lo) / max(hi - lo, 1), 0, 1) ** 1.05 * 236 + 16  # negro de película, blanco de papel
    rgb = np.stack([g * 1.0, g * 0.975, g * 0.935], -1)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), alfa]).astype(np.uint8), "RGBA")


# ------------------------------------------------------------ formas de la marca

def pluma(trazos, w=None, h=None):
    """Trazos de pluma de punta ancha (el aro de la v5 es una o de pluma): la punta va al ángulo fijo del aro, así
    el trazo engruesa y adelgaza solo según la dirección. trazos: [(puntos de control, media punta)]. Máscara L."""
    w, h = w or aa.W, h or aa.H
    m = Image.new("L", (w * 2, h * 2), 0)
    d = ImageDraw.Draw(m)
    a = np.radians(aa.PLUMA["eje"])
    for pts, punta in trazos:
        p = np.array(pts, np.float32) * 2
        p = np.vstack([p[0], p, p[-1]])  # Catmull-Rom por los puntos de control, bien denso
        cur = []
        for i in range(1, len(p) - 2):
            for t in np.linspace(0, 1, 40, endpoint=False):
                t2, t3 = t * t, t * t * t
                cur.append(0.5 * ((2 * p[i]) + (-p[i - 1] + p[i + 1]) * t + (2 * p[i - 1] - 5 * p[i] + 4 * p[i + 1] - p[i + 2]) * t2
                                  + (-p[i - 1] + 3 * p[i] - 3 * p[i + 1] + p[i + 2]) * t3))
        cur.append(p[-2])
        n_ = np.array([np.cos(a), np.sin(a)]) * punta * 2
        for q0, q1 in zip(cur[:-1], cur[1:]):
            d.polygon([tuple(q0 - n_), tuple(q0 + n_), tuple(q1 + n_), tuple(q1 - n_)], fill=255)
    return m.resize((w, h), Image.LANCZOS)


TINTAS = {"papel": PAPEL, "carbon": CARBON, "brasa": BRASA, "oscura": BRASA_HONDA}


def anillos(img, lista, semilla=1):
    """La o de pluma de la marca, grande y cortada por los bordes: hace lo que las flores del referente (marco,
    ritmo, dos tintas) con el gesto propio de Dial. lista: [{"c": [cx, cy, r], "punta": media punta, "tinta":
    papel|carbon|brasa|oscura o (r, g, b), "giro": radianes, "opacidad": 0-1}]. Tinta impresa pareja, sin veta;
    con opacidad baja queda detrás del texto como un sello tenue."""
    for k, a in enumerate(lista):
        cx, cy, r = a["c"]
        ang = np.linspace(0, 2 * np.pi, 13)[:-1] + a.get("giro", 0)
        pts = [(cx + r * np.cos(t), cy + r * 0.94 * np.sin(t)) for t in ang]
        m = pluma([(pts + pts[:3], a["punta"])])
        tinta = a["tinta"]
        aa.estampar(img, m, TINTAS.get(tinta, tinta) if isinstance(tinta, str) else tuple(tinta), 50 + semilla + 5 * k,
                    fuerza=0.45, opacidad=a.get("opacidad", 1.0))


def disco(img, c, color=BRASA_HONDA, semilla=1):
    """Círculo impreso de la misma tinta del campo, con más carga: detrás de la persona, le da peso y la separa."""
    m = Image.new("L", (aa.W, aa.H), 0)
    cx, cy, r = c
    ImageDraw.Draw(m).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    aa.estampar(img, m, color, 11 + semilla, fuerza=0.5)


def grotesca(tam):
    """Bricolage Grotesque negra y estrecha: la letra de texto de la marca, llevada a cartel."""
    return dn.fuente("BricolageGrotesque-VF.ttf", tam, opsz=96, wght=800, wdth=75)


def titular(img, x, y, lineas, tam, color=CARBON, inter=0.86):
    """Titular de cartel, renglones cortados a mano, interlineado apretado. Devuelve la base del último renglón."""
    f = grotesca(tam)
    d = ImageDraw.Draw(img)
    for k, l in enumerate(lineas):
        d.text((x - tam * 0.04, y + tam * 0.78 + k * tam * inter), l, font=f, fill=color, anchor="ls")
    return y + tam * 0.78 + (len(lineas) - 1) * tam * inter


def logo_tinta(alto):
    """La firma sobre fondo claro: letras en carbón y el punto en luz roja."""
    a = np.asarray(dn.logo(alto)).copy()
    a[a[..., 0] > 200, :3] = CARBON
    return Image.fromarray(a)


def firma_clara(img, x, y_pie, primera=PAPEL, cuenta="@dialmedio"):
    """COMENTA · GUARDA · COMPARTE (la primera resaltada) y la firma en carbón, para campos claros o de color."""
    fa_ = aa.etiqueta_f(27)
    xx = x
    for k, palabra in enumerate(["COMENTA", "GUARDA", "COMPARTE"]):
        if k:
            xx = aa.versal(img, xx + 14, y_pie, "·", fa_, CARBON, 0) + 14
        xx = aa.versal(img, xx, y_pie, palabra, fa_, primera if k == 0 else CARBON, 0.08)
    lg = logo_tinta(64)
    img.alpha_composite(lg, (x, round(y_pie + 40)))
    d = ImageDraw.Draw(img)
    d.text((x + lg.width + 24, y_pie + 86), "Sintonizar es conversar.", font=dn.serif(34), fill=CARBON, anchor="ls")
    d.text((aa.W - aa.M, y_pie + 86), cuenta, font=dn.sans(30, 560, 96), fill=CARBON, anchor="rs")


# ------------------------------------------------------------ láminas

def l_portada(cfg, lam, n):
    """Portada por capas (aprobada el 2 nov 2026): campo brasa plano, disco de la misma tinta más honda, anillos de
    pluma cortados por los bordes en dos tintas, titular de cartel que llena el ancho y la persona en blanco y
    negro ENCIMA del titular, tocando apenas el último renglón (profundidad). El antetítulo va chico, arriba.

    Campos: titulo (renglones con \\n), tam, y_titulo, bajada (antetítulo), disco [cx, cy, r], anillos,
    recorte [{"foto", "caja", "x", "ancho", "baja"}]."""
    img = aa.campo(BRASA, 3 + n)
    disco(img, lam["disco"], BRASA_HONDA, n)
    anillos(img, lam.get("anillos", []), n)
    y = aa.T + lam.get("y_titulo", 120)
    titular(img, aa.M, y, lam["titulo"].split("\n"), lam.get("tam", 170))
    for rc in lam.get("recorte", []):
        p = retrato(cfg["_base"] / rc["foto"], rc["caja"], rc["ancho"], n)
        img.alpha_composite(p, (rc["x"], aa.H - p.height + rc.get("baja", 0)))
    aa.cabecera(img, lam.get("meta", cfg["meta"]), oscuro=False, sobre_foto=False)
    if lam.get("bajada"):
        aa.versal(img, aa.M, y - 22, lam["bajada"].upper(), aa.etiqueta_f(28), CARBON, 0.08)
    return img


def l_texto(cfg, lam, n):
    """Lámina de argumento: papel, sin cabezote ni logo (Martín, 2 nov 2026: la marca va en portada y cierre),
    texto centrado con franja por renglón y, si hay foto, la tira de copia abajo. Campos: texto, tam, centro,
    foto, desde, foco, zoom, recorte (de al_aire), solape."""
    img = aa.campo(PAPEL, 20 + n, clase="prensa")
    y1 = aa.H - aa.B
    if lam.get("foto"):
        y1 = banda(img, cfg["_base"] / lam["foto"], lam.get("desde", 0.6), lam.get("foco", (0.5, 0.5)),
                   lam.get("zoom", 1.0), n) - 40
    rcs = lam.get("recorte", [])
    if rcs:
        y1 = min(y1, min(rc["y"] for rc in rcs) + lam.get("solape", 40))
    renglones(img, lam["texto"], 110, y1, lam.get("tam", 58), centro=lam.get("centro", True))
    for rc in rcs:
        aa.pegar_recorte(img, cfg, rc, n)
    return img


def l_cierre(cfg, lam, n):
    """Cierre como par de la portada (aprobado el 2 nov 2026): el mismo campo, disco y anillo, la pregunta en la
    letra del titular, un filete, la misión de Dial y la firma. Sin el signo de pregunta grande.

    Campos: pregunta (renglones con \\n), tam, mision (por defecto MISION), ancho_mision, disco, anillos, cuenta."""
    img = aa.campo(BRASA, 40 + n)
    disco(img, lam["disco"], BRASA_HONDA, n)
    anillos(img, lam.get("anillos", []), n)
    aa.cabecera(img, "CONVERSEMOS", oscuro=False, sobre_foto=False)
    x, y = aa.M, aa.T + 190
    aa.versal(img, x, y, "TU OPINIÓN", aa.etiqueta_f(28), CARBON, 0.1)
    base = titular(img, x, y + 24, lam["pregunta"].split("\n"), lam.get("tam", 118))
    d = ImageDraw.Draw(img)
    y = base + 56
    d.line([(x, y), (x + 140, y)], fill=CARBON, width=5)
    fm = dn.cuerpo(36, 540)
    for k, l in enumerate(aa.partir(lam.get("mision", MISION), fm, lam.get("ancho_mision", 720))):
        d.text((x, y + 70 + k * 50), l, font=fm, fill=CARBON, anchor="ls")
    firma_clara(img, x, aa.H - aa.B - 120, cuenta=lam.get("cuenta", "@dialmedio"))
    return img


ESTILOS = {"portada": l_portada, "texto": l_texto, "cierre": l_cierre}
