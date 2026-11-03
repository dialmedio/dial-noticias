"""Copia quemada y sello: técnicas aprendidas del carrusel «Ecología de las relaciones» de @aliana.luz (3 nov 2026),
ficha 4 de REFERENTES.md (aprobada el 3 nov). Pieza de ejemplo: «¿Dónde aprendimos la guerra que queremos dejar
atrás?», en Noticias/Al Aire/2026-11-03 Ecologia de las relaciones (calco)/calco.py.

El referente pone fotos de archivo en blanco y negro con mucho grano, la pregunta escrita a mano enorme encima y una
sola mancha azul plana sobre el objeto o la cara que carga el poder (el casete en la cabeza, la carpeta del
voceador, la maestra sin cara). Dial no copia la mano ni el azul: lo traduce a oficios de imprenta y de oficina.

  copia(foto, caja, quemar)      la foto de archivo a todo el ancho, en fotograbado sobre el hueso, con zonas
                                 «quemadas» como en el cuarto oscuro: donde va la letra, la copia se oscurece a mano;
                                 abajo= pone una foto apaisada solo abajo y quema el cielo hasta el negro
  tipos(img, renglones, ...)     la pregunta compuesta con tipos sueltos: cada letra con su giro, su tamaño y su
                                 altura, y el renglón que se dobla con la foto; tinta de imprenta con el canto comido
  tampon(img, mascara, color)    tinta de tampón de caucho sobre un objeto: plana, opaca, con la presión desigual y
                                 los poros del sello mal entintado. Marca el mecanismo, nunca la cara
  sello(texto, tam)              el sello de oficina con una palabra y marco doble, girado: la etiqueta que se le
                                 pone a una persona («desechable», «baja»), estampada sobre la foto. Va sobre fondo
                                 muy claro o muy oscuro: sobre gris medio la brasa se pierde
  mascara_oscura(foto, caja)     la mancha de un objeto oscuro sobre fondo claro (la bota colgada), para el tampón"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import iluminado as il
import materia as mt

W, H = 1080, 1350


def _blur(a, r):
    return np.asarray(Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)),
                      np.float32) / 255


# ------------------------------------------------------------ la copia de archivo, quemada donde va la letra

def copia(foto, caja=None, quemar=(), brillo=-0.04, contraste=1.18, grano=0.6, semilla=1, w=W, h=H, papel=None,
          abajo=None):
    """La foto a todo el ancho de la lámina, en fotograbado (tinta sepia sobre el papel hueso).

    caja: encuadre en la foto (x0, y0, x1, y1), con la proporción de la lámina; si no, el centro.
    quemar: [(x0, y0, x1, y1, fuerza)] en px de la lámina. Como el «quemado» del cuarto oscuro: esa zona recibe más
      luz y la copia sale más oscura, con el borde perdido (sin caja). Es lo que deja leer la letra clara encima.
    abajo: alto en px de la foto si va solo en la parte de abajo (una foto apaisada que no se puede recortar sin
      que la letra tape una cara). Arriba queda papel en gris medio que se quema con `quemar` hasta el negro: la
      foto sube y se pierde en la sombra, sin canto.
    Devuelve (lámina RGBA, gris de la copia 0-1 ya quemada, foto RGB encuadrada) para pintar encima; con abajo, la
    foto encuadrada tiene el alto de la lámina (arriba en gris)."""
    im = foto.convert("RGB")
    fh = abajo or h
    if caja:
        im = im.crop(caja)
    else:
        k = min(im.width / w, im.height / fh)
        cw, ch = w * k, fh * k
        x0, y0 = (im.width - cw) / 2, (im.height - ch) / 2
        im = im.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch)))
    im = im.resize((w, fh), Image.LANCZOS)
    if abajo:
        lienzo = Image.new("RGB", (w, h), (128, 128, 128))
        lienzo.paste(im, (0, h - abajo))
        im = lienzo
    g = np.asarray(im.convert("L"), np.float32) / 255
    if abajo:  # arriba, el tono de la orilla de la foto; la foto entra fundida en 140 px
        y0 = h - abajo
        tono = g[y0:y0 + 40].mean()
        t = np.clip((np.arange(h, dtype=np.float32) - y0) / 140, 0, 1)[:, None]
        g = g * t + tono * (1 - t)
    if quemar:
        z = np.zeros((h, w), np.float32)
        for x0, y0, x1, y1, f in quemar:
            q = np.zeros((h, w), np.float32)
            q[max(0, int(y0)):int(y1), max(0, int(x0)):int(x1)] = f
            z = np.maximum(z, _blur(q, 70))
        g = g * (1 - z)
    lam = papel.copy() if papel is not None else il.pliego(w, h, semilla)
    lam.alpha_composite(il.entintar(il.fotograbado(g, contraste, brillo, grano, semilla=semilla), il.SEPIA))
    return lam, g, im


# ------------------------------------------------------------ tipos sueltos

def _impresion(m, semilla):
    """La letra impresa con tipo de plomo: canto apenas comido, tinta que no carga pareja."""
    h, w = m.shape
    canto = mt.ruido(w, h, 3.5, semilla, 2)
    # solo el canto se come (4m(1-m) es 0 dentro del trazo): los perfiles finos no se cortan
    a = np.clip(m + (canto - 0.5) * 0.7 * (4 * m * (1 - m)), 0, 1)
    carga = 0.88 + 0.12 * mt.ruido(w, h, 40, semilla + 1, 2)
    poros = np.clip((mt.fino(w, h, semilla + 2, 0.6) - 0.6) * 3, 0, 1) * 0.18
    return np.clip(a * (carga - poros), 0, 1)


def tipos(img, renglones, x, y, f, color, paso, centro=False, ancho=None, semilla=1, baile=1.0, curva=(),
          tinta=None):
    """La pregunta compuesta con tipos sueltos, a mano, sobre img (en su sitio).

    Cada letra se pone sola: un poco girada (±3°), más grande o más chica (±7 %), arriba o abajo de la línea; así la
    pregunta se lee como algo hecho por alguien y no como un rótulo. renglones: los cortes van a mano, como en un
    cartel. curva: por renglón, cuánto se dobla (en fracciones del tamaño; + hacia abajo en el centro), para que el
    renglón siga una forma de la foto. ancho: si se da y centro=False, x es el borde izquierdo de esa caja.
    tinta: color de la tinta en cada renglón (lista) para partir la pregunta en dos tintas. Devuelve la base del
    último renglón."""
    rng = np.random.default_rng(semilla)
    tam = f.size
    capa = np.zeros((img.height, img.width), np.float32)
    colores = np.zeros((img.height, img.width, 3), np.float32)
    for k, t in enumerate(renglones):
        largo = f.getlength(t)
        x0 = (img.width - largo) / 2 if centro else x
        base = y + k * paso
        cv = curva[k] if k < len(curva) else 0
        col = (tinta[k] if tinta and k < len(tinta) else color)
        for i, c in enumerate(t):
            if c == " ":
                continue
            adelante = f.getlength(t[:i]) if i else 0
            av = f.getlength(c)
            u = (adelante + av / 2) / max(largo, 1)                     # 0-1 a lo largo del renglón
            dy_curva = cv * tam * 4 * u * (1 - u)
            giro_curva = -np.degrees(np.arctan(cv * tam * 4 * (1 - 2 * u) / max(largo, 1)))
            s = 1 + np.clip(rng.normal(0, 0.045), -0.08, 0.08) * baile
            gi = np.clip(rng.normal(0, 2.2), -4, 4) * baile + giro_curva
            dy = np.clip(rng.normal(0, tam * 0.028), -tam * 0.06, tam * 0.06) * baile + dy_curva
            pad = int(tam * 0.6)
            gw, gh = int(av * 1.4) + 2 * pad, int(tam * 1.4) + 2 * pad
            g = Image.new("L", (gw, gh), 0)
            ImageDraw.Draw(g).text((pad, pad + tam), c, font=f, fill=255, anchor="ls")
            g = g.resize((max(1, round(gw * s)), max(1, round(gh * s))), Image.LANCZOS)
            # gira sobre el pie de la letra
            g = g.rotate(gi, resample=Image.BICUBIC, center=((pad + av / 2) * s, (pad + tam) * s))
            px, py = round(x0 + adelante - pad * s), round(base + dy - (pad + tam) * s)
            ga = np.asarray(g, np.float32) / 255
            sx0, sy0 = max(0, -px), max(0, -py)
            ex, ey = min(ga.shape[1], img.width - px), min(ga.shape[0], img.height - py)
            if ex <= sx0 or ey <= sy0:
                continue
            zona = (slice(py + sy0, py + ey), slice(px + sx0, px + ex))
            trozo = ga[sy0:ey, sx0:ex]
            capa[zona] = np.maximum(capa[zona], trozo)
            colores[zona] = np.where(trozo[..., None] > 0.02, np.array(col, np.float32), colores[zona])
    a = _impresion(capa, semilla + 7)
    out = np.dstack([colores, a * 255]).astype(np.uint8)
    img.alpha_composite(Image.fromarray(out, "RGBA"))
    return y + (len(renglones) - 1) * paso


# ------------------------------------------------------------ tampón y sello

def _tinta_tampon(m, semilla):
    """Alfa de tinta de tampón: plana y opaca en el cuerpo, con el borde un poco más cargado (el caucho aplasta la
    tinta hacia el canto), presión desigual y poros donde el sello no tocó."""
    h, w = m.shape
    presion = np.clip(0.80 + 0.30 * (mt.ruido(w, h, 55, semilla, 3) - 0.5) * 2, 0, 1)
    poros = np.clip((mt.ruido(w, h, 4, semilla + 1, 2) - 0.70) * 5, 0, 1)
    raspado = np.clip((mt.ruido(w, h, 18, semilla + 2, 2, alargue=5) - 0.78) * 4, 0, 1)
    borde = np.clip(m - _blur(m, 2.2), 0, 1) * 0.5
    canto = mt.ruido(w, h, 2.5, semilla + 3, 2)
    mm = np.clip((_blur(m, 0.8) - 0.5 + (canto - 0.5) * 0.35) * 6 + 0.5, 0, 1)
    return np.clip(mm * (presion - poros * 0.55 - raspado * 0.45) + borde * mm, 0, 1)


def tampon(img, mascara, color, semilla=1, fuerza=0.94, x=0, y=0):
    """Tinta de tampón (color plano y opaco) sobre img donde dice la máscara (0-1, del tamaño de la zona que empieza
    en x, y). A diferencia de la aguada, tapa: el objeto queda convertido en una mancha de oficina."""
    m = np.asarray(mascara, np.float32)
    if m.max() > 1.5:
        m = m / 255
    a = _tinta_tampon(m, semilla) * fuerza
    capa = np.zeros((*m.shape, 4), np.uint8)
    capa[..., :3] = color
    capa[..., 3] = (a * 255).astype(np.uint8)
    img.alpha_composite(Image.fromarray(capa, "RGBA"), (int(x), int(y)))


def sello(texto, tam, color, semilla=1, giro=-4.0, marco=True, fuente=None, carga=1.0):
    """El sello de oficina: una palabra en versales de cartel, con marco doble, entintada como tampón y girada.
    carga: más de 1 entinta más (sobre papel o gris claro la brasa pierde contraste: 1.3). Devuelve RGBA recortado."""
    import afiche as af
    f = fuente or af.grotesca(tam)
    track = tam * 0.06
    largo = sum(f.getlength(c) for c in texto) + track * (len(texto) - 1)
    pad_x, pad_y = tam * 0.42, tam * 0.30
    gr = max(3, round(tam * 0.075))
    w = int(largo + 2 * pad_x + 4 * gr)
    h = int(tam * 0.78 + 2 * pad_y + 4 * gr)
    m = Image.new("L", (w + 40, h + 40), 0)
    d = ImageDraw.Draw(m)
    if marco:
        d.rectangle((20, 20, 20 + w, 20 + h), outline=255, width=gr)
        d.rectangle((20 + gr * 2, 20 + gr * 2, 20 + w - gr * 2, 20 + h - gr * 2), outline=255, width=max(2, gr // 2))
    xx = 20 + (w - largo) / 2
    for c in texto:
        d.text((xx, 20 + h / 2 + tam * 0.39), c, font=f, fill=255, anchor="ls")
        xx += f.getlength(c) + track
    m = m.rotate(giro, resample=Image.BICUBIC, expand=True)
    a = np.clip(_tinta_tampon(np.asarray(m, np.float32) / 255, semilla) * carga, 0, 1)
    out = np.zeros((m.height, m.width, 4), np.uint8)
    out[..., :3] = color
    out[..., 3] = (a * 255).astype(np.uint8)
    im = Image.fromarray(out, "RGBA")
    return im.crop(im.getbbox())


def mascara_oscura(gris, caja, umbral=0.42, cerrar=9):
    """Máscara 0-1 (tamaño de la lámina) de un objeto oscuro sobre fondo claro dentro de caja (px de la lámina):
    la bota colgada en la pared. Se queda con la mancha más grande, sin huecos."""
    from scipy.ndimage import binary_closing, binary_fill_holes, label
    x0, y0, x1, y1 = caja
    z = gris[y0:y1, x0:x1] < umbral
    z = binary_fill_holes(binary_closing(z, np.ones((cerrar, cerrar))))
    et, k = label(z)
    if k > 1:
        t = np.bincount(et.ravel())
        t[0] = 0
        z = et == t.argmax()
    m = np.zeros_like(gris)
    m[y0:y1, x0:x1] = z
    return _blur(m, 1.0)
