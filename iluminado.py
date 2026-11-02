"""Grabado iluminado: técnicas aprendidas de referentes (2 nov 2026), convertidas en herramientas de Dial.

Nace de estudiar el carrusel «crisis de sensibilidad» de @ecologiasensible (collage de paisaje en blanco y negro
con el agua pintada a mano, mancha de resaltador tras una itálica, hoja rasgada sobre la foto, láminas oscuras con
palabras de color). No copia su ejecución: la traduce a procesos de imprenta y de taller. El manual de uso está en
REFERENTES.md; aquí solo las piezas.

  grabado(gris)                líneas de buril en vez de trama de puntos: la foto vuelve grabado de libro viejo
  aguada(img, mascara, color)  color puesto a mano con pincel: sangra, se acumula en el borde, se corre del dibujo
  pincelada(img, cajas, color) resaltador de pincel seco detrás de una frase (cerdas, puntas abiertas, leve giro)
  isolineas(w, h)              curvas de nivel finas, para nombrar el territorio sin mostrarlo
  hoja(img, caja)              hoja de papel rasgada a mano, girada, con su sombra, sobre la foto
  horizonte(foto)              alfa que quita el cielo: el paisaje sale del papel
  cielo_rayado(w, h)           el cielo de grabado: rayas finas que pesan arriba, huecos de nube
  subrayado(img, cajas, color) marcador rápido bajo palabras de una cita
  mascara_solida / contorno    figuras recortadas sin huecos (el filete existe, pero en personas no se usa)
  fotograbado(gris)            tono continuo con grano de aguatinta: la textura para personas
  color_de(foto)               máscara de una prenda por su color, para iluminarla con aguada
  silueta(foto, cache)         la persona o la planta sin fondo (rembg), para que rompa el marco
  continuo(ancho_total, ...)   un mismo paisaje que corre de una lámina a la siguiente

Composición (resuelta en la pieza de prueba, para todas las líneas):
  afirma / siente / cartel     las dos voces (Instrument Sans que afirma, Fraunces itálica que siente) y el rótulo
  cortar / renglones / mixto   renglones con pincelada detrás; renglón de tramos con voz y color (lista-poema)
  firma(img)                   @dialmedio con el aro; elige tinta clara u oscura según el fondo
  pliego(w, h, semilla, noche) papel hueso o cartulina
  paisaje_continuo(foto, n)    la panorámica en buril, día y noche, sin cielo, con el agua en aguada
  persona(foto, alto, papel)   una persona en fotograbado, sin delineado, la prenda iluminada (nunca la piel)
  figura_buril(foto, alto)     planta u objeto en buril (nunca personas)
  cifra(texto, tam)            la cifra del cartel de junta: grabada, en aguada, con filete

Todas trabajan en RGBA de PIL o en arrays float 0-1 y no tocan nada fuera de sí."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

import materia as mt

# paleta de la técnica: el papel y la tinta del grabado; el color de la aguada lo elige cada pieza
HUESO = (240, 233, 219)
SEPIA = (36, 29, 23)
CARTULINA = (24, 21, 19)
TINTA_CLARA = (226, 218, 200)
ANIL = (60, 96, 160)            # aguada de agua: añil
ANIL_CLARO = (150, 178, 222)    # el añil para letra sobre cartulina
SALVIA = (128, 156, 104)        # aguada de monte
OCRE = (196, 140, 58)           # aguada de tierra


def _gris(foto):
    return np.asarray(foto.convert("L"), np.float32) / 255 if isinstance(foto, Image.Image) else foto


def _escala(a, w, h, metodo=Image.BICUBIC):
    return np.asarray(Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8)).resize((w, h), metodo), np.float32) / 255


def _blur(a, r):
    if r <= 0:
        return a
    return np.asarray(Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)),
                      np.float32) / 255


# ------------------------------------------------------------ grabado de líneas

def grabado(gris, periodo=6.5, angulo=-12.0, onda=0.9, contraste=1.25, brillo=0.0, cruce=0.62, semilla=1, clara=False):
    """Cobertura de tinta 0-1 de un grabado de buril: líneas paralelas que engordan en la sombra y ondulan con la
    forma; en lo más oscuro entra un segundo rayado cruzado. clara=True para imprimir con tinta clara sobre negro
    (la tinta va donde la foto tiene luz)."""
    g = _gris(gris)
    g = np.clip((g - 0.5) * contraste + 0.5 + brillo, 0, 1)
    if clara:
        g = 1 - g
    h, w = g.shape
    s = 2
    G = _escala(g, w * s, h * s)
    yy, xx = np.mgrid[0:h * s, 0:w * s].astype(np.float32)
    a = np.radians(angulo)
    # la línea sigue un poco la luz de la foto (como el buril que rodea el volumen) y una ondulación lenta de la mano
    curva = _blur(G, 6 * s) * 1.6 + (mt.ruido(w * s, h * s, 420 * s, semilla, 2) - 0.5) * onda
    v = (-xx * np.sin(a) + yy * np.cos(a)) / (periodo * s) + curva
    tri = np.abs(2 * (v - np.floor(v)) - 1)            # 0 en el eje de la línea, 1 entre líneas
    oscuro = 1 - G
    tinta = np.clip((oscuro * 1.05 - tri) * 7 + 0.5, 0, 1)
    if cruce:
        b = a + np.radians(62)
        v2 = (-xx * np.sin(b) + yy * np.cos(b)) / (periodo * 1.15 * s) + curva * 0.5
        tri2 = np.abs(2 * (v2 - np.floor(v2)) - 1)
        tinta = np.maximum(tinta, np.clip(((oscuro - cruce) * 2.6 - tri2) * 7 + 0.5, 0, 1))
    # el borde de cada línea lo come la fibra
    tinta = np.clip(tinta + mt.fino(w * s, h * s, semilla + 3, 0.8) * 0.06, 0, 1)
    return _escala(tinta, w, h, Image.LANCZOS)


def entintar(cobertura, tinta, alfa=None):
    """RGBA con la tinta donde hay cobertura (y solo dentro de alfa, si se da)."""
    h, w = cobertura.shape
    a = cobertura if alfa is None else cobertura * alfa
    out = np.zeros((h, w, 4), np.uint8)
    out[..., :3] = tinta
    out[..., 3] = np.clip(a * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


# ------------------------------------------------------------ aguada a mano

def aguada(img, mascara, color, semilla=1, fuerza=0.9, sangrado=5, desfase=(6, 4), sobre_negro=False, x=0, y=0):
    """Pinta con agua de color sobre img (RGBA, en su sitio) donde dice la máscara (0-1, del tamaño de la zona).

    Como una acuarela puesta a mano encima de un grabado: no respeta del todo el dibujo (se corre unos px y
    sangra con un borde irregular), el pigmento se acumula en el canto y granula en el centro. Sobre papel
    multiplica (el grabado sigue viéndose debajo); sobre cartulina negra ilumina."""
    m = np.asarray(mascara, np.float32)
    if m.max() > 1.5:
        m = m / 255
    h, w = m.shape
    n = mt.ruido(w, h, 70, semilla, 3)
    mb = _blur(m, sangrado)
    a = np.clip((mb + (n - 0.5) * 0.45 - 0.32) * 3.2, 0, 1)
    borde = np.clip(a - _blur(a, 7), 0, 1) * 1.8
    gran = mt.ruido(w, h, 5, semilla + 1, 2)
    nubes = mt.ruido(w, h, 160, semilla + 2, 3)
    a = np.clip(a * (0.55 + 0.25 * gran + 0.25 * nubes) + borde * 0.4, 0, 1) * fuerza
    dx, dy = desfase  # se corre del dibujo sin dar la vuelta por el otro borde
    corrido = np.zeros_like(a)
    corrido[max(dy, 0):h + min(dy, 0), max(dx, 0):w + min(dx, 0)] = a[max(-dy, 0):h - max(dy, 0), max(-dx, 0):w - max(dx, 0)]
    a = corrido
    zona = np.asarray(img.crop((x, y, x + w, y + h)), np.float32)
    c = np.array(color, np.float32)
    if sobre_negro:
        zona[..., :3] = zona[..., :3] + (c - zona[..., :3]) * (a[..., None] * 0.55)
    else:
        zona[..., :3] = zona[..., :3] * (1 - a[..., None] * (1 - c / 255))
    img.paste(Image.fromarray(np.clip(zona, 0, 255).astype(np.uint8), "RGBA"), (x, y))


# ------------------------------------------------------------ pincelada

def pincelada(img, cajas, color, semilla=1, giro=-1.2):
    """Resaltador de pincel seco detrás de una o varias líneas de texto: cuerpo lleno, cerdas que se abren en el
    canto de arriba y de abajo, puntas desparejas, levemente torcido. cajas: [(x0, y0, x1, y1)] por renglón."""
    W, H = img.size
    m = np.zeros((H, W), np.float32)
    rng = np.random.default_rng(semilla)
    for k, (x0, y0, x1, y1) in enumerate(cajas):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        hh, ww = y1 - y0, x1 - x0
        if hh < 4 or ww < 4:
            continue
        pad = int(hh * 0.5)
        zw, zh = ww + 2 * pad, hh + 2 * pad
        yy, xx = np.mgrid[0:zh, 0:zw].astype(np.float32)
        cy = zh / 2 + (xx - zw / 2) * np.tan(np.radians(giro)) + rng.uniform(-2, 2)
        dist = np.abs(yy - cy) / (hh / 2)                       # 0 en el centro del trazo, 1 en el canto
        cerdas = mt.ruido(zw, zh, max(8, hh * 0.5), semilla + 10 + k, 3, alargue=14)
        cuerpo = np.clip((1.0 - dist) * 7 + (cerdas - 0.5) * 5 * np.clip(dist * 1.4, 0, 1), 0, 1)   # canto nítido
        # las puntas: cada fila empieza y termina en un sitio distinto, como el pincel que entra y sale
        fila = mt.ruido(1, zh, max(4, hh * 0.3), semilla + 20 + k, 2)[:, 0]
        ini = pad - hh * 0.25 + (fila - 0.5) * hh * 0.9
        fin = pad + ww + hh * 0.2 + (mt.ruido(1, zh, max(4, hh * 0.3), semilla + 30 + k, 2)[:, 0] - 0.5) * hh * 0.9
        puntas = np.clip((xx - ini[:, None]) / 2.5, 0, 1) * np.clip((fin[:, None] - xx) / 2.5, 0, 1)
        seca = 0.86 + 0.14 * mt.ruido(zw, zh, hh * 2, semilla + 40 + k, 2, alargue=6)
        a = cuerpo * puntas * seca
        X0, Y0 = x0 - pad, y0 - pad
        sx0, sy0 = max(0, -X0), max(0, -Y0)
        ex, ey = min(zw, W - X0), min(zh, H - Y0)
        m[Y0 + sy0:Y0 + ey, X0 + sx0:X0 + ex] = np.maximum(m[Y0 + sy0:Y0 + ey, X0 + sx0:X0 + ex], a[sy0:ey, sx0:ex])
    capa = np.zeros((H, W, 4), np.uint8)
    capa[..., :3] = color
    capa[..., 3] = (np.clip(m, 0, 1) * 255).astype(np.uint8)
    img.alpha_composite(Image.fromarray(capa, "RGBA"))


# ------------------------------------------------------------ isolíneas

def isolineas(w, h, semilla=1, n=16, grosor=1.1, escala=520, esquina=(0, 0)):
    """Máscara 0-1 de curvas de nivel finas de grosor parejo (sobre un relieve de ruido suave). Se desvanecen
    lejos de la esquina dada (en fracciones de w, h), para que no haya un borde de caja."""
    from scipy.ndimage import gaussian_filter
    f = gaussian_filter(mt.ruido(w, h, escala, semilla, 3).astype(np.float64), 6) * n   # sin escalones de 8 bits
    gy, gx = np.gradient(f)
    grad = np.sqrt(gx ** 2 + gy ** 2)
    d = np.abs((f - np.floor(f)) - 0.5)                     # 0.5 en la curva
    dist_px = (0.5 - d) / (grad + 1e-4)
    lineas = np.clip(grosor - dist_px + 0.5, 0, 1) * np.clip(grad * 60 - 0.2, 0, 1)   # sin manchas en las cimas planas
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.hypot((xx - esquina[0] * w) / w, (yy - esquina[1] * h) / h)
    return lineas * np.clip(1.15 - r * 1.1, 0, 1) ** 1.5



# ------------------------------------------------------------ subrayado de resaltador

def subrayado(img, cajas, color, semilla=1, alfa=0.85):
    """Trazo de marcador bajo palabras (la mitad baja del renglón), rápido y un poco torcido, como quien subraya
    una cita que le tocó. Más fino y más rápido que la pincelada. cajas: [(x0, y_base, x1, alto_letra)]."""
    W, H = img.size
    capa = Image.new("L", (W * 2, H * 2), 0)
    d = ImageDraw.Draw(capa)
    rng = np.random.default_rng(semilla)
    for x0, base, x1, alto in cajas:
        g = alto * 0.42
        y = base - alto * 0.12
        inc = rng.uniform(-0.012, 0.012)
        pts_arr, pts_ab = [], []
        for i in range(24):
            t = i / 23
            x = x0 - 6 + (x1 - x0 + 12) * t
            yc = y + (x - x0) * inc + rng.normal(0, 0.6)
            e = g / 2 * (0.82 + 0.18 * np.sin(t * np.pi))
            pts_arr.append((2 * x, 2 * (yc - e)))
            pts_ab.append((2 * x, 2 * (yc + e)))
        d.polygon(pts_arr + pts_ab[::-1], fill=255)
    m = np.asarray(capa.resize((W, H), Image.LANCZOS), np.float32) / 255
    m = m * (0.85 + 0.15 * mt.ruido(W, H, 30, semilla + 1, 2, alargue=8)) * alfa
    out = np.zeros((H, W, 4), np.uint8)
    out[..., :3] = color
    out[..., 3] = (np.clip(m, 0, 1) * 255).astype(np.uint8)
    img.alpha_composite(Image.fromarray(out, "RGBA"))


# ------------------------------------------------------------ cielo rayado

def cielo_rayado(w, h, periodo=7.0, grosor=(0.5, 1.6), semilla=1, nubes=0.35):
    """El cielo del grabado: rayas horizontales finas que se engruesan hacia arriba (el cielo de noche pesa
    arriba y se abre en el horizonte), con huecos donde pasan nubes. Cobertura 0-1."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    onda = (mt.ruido(w, h, 600, semilla, 2) - 0.5) * 1.2
    v = yy / periodo + onda
    tri = np.abs(2 * (v - np.floor(v)) - 1) * periodo / 2       # distancia al eje de la raya, en px
    t = 1 - yy / max(h - 1, 1)                                   # 1 arriba, 0 en el horizonte
    g = grosor[0] + (grosor[1] - grosor[0]) * t ** 1.3
    nub = np.clip((mt.ruido(w, h, 260, semilla + 1, 3, alargue=3) - (1 - nubes)) * 4, 0, 1)
    return np.clip(g / 2 - tri + 0.6, 0, 1) * (1 - nub)


# ------------------------------------------------------------ figuras: máscara sólida y contorno

def mascara_solida(m, umbral=110):
    """La máscara de rembg sin zonas a medias: umbral, huecos rellenos y canto suave de 1 px."""
    from scipy.ndimage import binary_fill_holes, binary_opening
    a = np.asarray(m, np.float32)
    b = binary_fill_holes(binary_opening(a > umbral, iterations=2))
    return Image.fromarray((b * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))


def contorno(m, grosor=3):
    """El filete de buril alrededor de una figura recortada (L 0-255): lo que define el borde en un grabado."""
    a = m.filter(ImageFilter.MaxFilter(grosor * 2 + 1))
    return ImageChops.subtract(a, m)


# ------------------------------------------------------------ fotograbado (para personas)

def fotograbado(gris, contraste=1.12, brillo=0.02, grano=0.5, lineas=0.10, periodo=3.4, semilla=1, clara=False):
    """Cobertura 0-1 de un fotograbado: tono continuo (la cara se lee como foto, no como billete) con el grano de
    resina de la aguatinta y un rayado finísimo casi invisible que lo emparenta con el grabado del paisaje.
    Es la textura para personas; el buril (grabado) queda para paisaje, plantas y objetos."""
    g = _gris(gris)
    g = np.clip((g - 0.5) * contraste + 0.5 + brillo, 0, 1)
    cob = g if clara else 1 - g
    cob = cob ** 1.08
    h, w = cob.shape
    resina = mt.fino(w, h, semilla, 0.55)                          # granos de resina: más en los medios tonos
    cob = cob + resina * grano * 0.08 * (0.25 + 4 * cob * (1 - cob))
    yy = np.arange(h, dtype=np.float32)[:, None]
    v = yy / periodo + (mt.ruido(w, h, 300, semilla + 1, 2) - 0.5) * 0.8
    raya = np.abs(2 * (v - np.floor(v)) - 1)
    cob = cob * (1 - lineas * (raya - 0.5) * 2 * np.clip(cob * 2, 0, 1))
    return np.clip(cob, 0, 1)


def color_de(foto, tono="rojo", umbral=0.18):
    """Máscara 0-1 de una prenda u objeto por su color en la foto (para iluminarlo con aguada): 'rojo' o 'vivo'
    (cualquier color saturado)."""
    a = np.asarray(foto.convert("RGB"), np.float32) / 255
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    sat = a.max(-1) - a.min(-1)
    if tono == "rojo":  # rojo de tela, no de piel: en la tela el verde y el azul son menos de la mitad del rojo,
        # en luz y en sombra; la piel al sol es roja pero conserva verde (proporción ~0.6)
        m = ((g / (r + 1e-3)) < 0.42) & ((b / (r + 1e-3)) < 0.42) & (r > 0.35)
    else:
        m = sat > umbral + 0.2
    m = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.GaussianBlur(1))
    return np.asarray(m, np.float32) / 255

# ------------------------------------------------------------ hoja rasgada

def hoja(img, caja, semilla=1, giro=-1.6, color=HUESO, sombra=0.42):
    """Una hoja de papel rasgada a mano en sus cuatro lados, girada, con su sombra, pegada sobre img (en su sitio).
    Devuelve la función que lleva coordenadas de la hoja recta a la lámina (para escribir encima girado) y el
    lienzo de la hoja (RGBA recto) para escribir antes de girarlo: se usa como
        lienzo, pegar = hoja(...); dibujar en lienzo; pegar()"""
    x0, y0, x1, y1 = caja
    w, h = int(x1 - x0), int(y1 - y0)
    rng = np.random.default_rng(semilla)

    def canto(p, q, n, amp):
        out = []
        ruido = np.cumsum(rng.normal(0, amp * 0.35, n))
        ruido -= np.linspace(ruido[0], ruido[-1], n)
        for i in range(n):
            t = i / (n - 1)
            px, py = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
            dx, dy = q[1] - p[1], -(q[0] - p[0])
            ln = np.hypot(dx, dy) or 1
            e = ruido[i] + rng.normal(0, amp * 0.25)
            out.append((px + dx / ln * e, py + dy / ln * e))
        return out
    m_pad = 40
    pts = (canto((m_pad, m_pad), (w + m_pad, m_pad), 160, 3.5) + canto((w + m_pad, m_pad), (w + m_pad, h + m_pad), 160, 2.2)
           + canto((w + m_pad, h + m_pad), (m_pad, h + m_pad), 160, 3.5) + canto((m_pad, h + m_pad), (m_pad, m_pad), 160, 2.2))
    W2, H2 = w + 2 * m_pad, h + 2 * m_pad
    mask = Image.new("L", (W2, H2), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    papel = mt.papel(W2, H2, color, semilla + 40, "prensa", 1.0)
    canto_m = np.asarray(ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(5))), np.float32) / 255
    papel = papel + canto_m[..., None] * 18
    lienzo = Image.fromarray(np.dstack([np.clip(papel, 0, 255), np.asarray(mask)]).astype(np.uint8), "RGBA")

    def pegar():
        lienzo.putalpha(ImageChops.multiply(lienzo.split()[3], mask))   # lo pintado encima no se sale de la hoja
        rot = lienzo.rotate(giro, resample=Image.BICUBIC, expand=False)
        som = rot.split()[3].filter(ImageFilter.GaussianBlur(16)).point(lambda v: v * sombra)
        capa_s = Image.new("RGBA", rot.size, (0, 0, 0, 0))
        capa_s.putalpha(som)
        img.alpha_composite(capa_s, (int(x0 - m_pad + 8), int(y0 - m_pad + 12)))
        img.alpha_composite(rot, (int(x0 - m_pad), int(y0 - m_pad)))
    return lienzo, m_pad, pegar


# ------------------------------------------------------------ horizonte y siluetas

def horizonte(foto, umbral_azul=0.08, apertura=81, alto_max=0.6, suavizado=12):
    """Alfa 0-1 que deja la tierra y quita el cielo (azul o nube). El filo se abre para que no queden agujas."""
    a = np.asarray(foto.convert("RGB"), np.float32) / 255
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    L = 0.3 * r + 0.59 * g + 0.11 * b
    sat = (a.max(-1) - a.min(-1)) / (a.max(-1) + 1e-4)
    h, w = L.shape
    cielo = ((b - r > umbral_azul) & (L > 0.42)) | ((L > 0.82) & (sat < 0.14))
    tierra = ~cielo
    cs = np.vstack([np.zeros((1, w)), np.cumsum(tierra, 0)])
    filo = np.argmax((cs[8:] - cs[:-8]) >= 8, axis=0).astype(np.float32)
    filo = np.minimum(filo, alto_max * h)
    from numpy.lib.stride_tricks import sliding_window_view as ventanas
    k = apertura  # la mediana quita agujas sin dejar mesetas; el promedio corrido suaviza el pulso
    filo = np.median(ventanas(np.pad(filo, k // 2, mode="edge"), k), 1)
    s = max(3, suavizado) | 1
    filo = ventanas(np.pad(filo, s // 2, mode="edge"), s).mean(1)
    yy = np.arange(h, dtype=np.float32)[:, None]
    return np.clip(yy - filo[None, :] + 0.5, 0, 1), filo


_SESIONES = {}


def silueta(foto, cache=None, modelo="u2net_human_seg"):
    """Máscara L de la figura sin fondo (rembg). Se guarda en cache para no recalcularla."""
    if cache and Path(cache).exists():
        m = Image.open(cache).convert("L")
        if m.size == foto.size:
            return m
    from rembg import new_session, remove
    if modelo not in _SESIONES:
        _SESIONES[modelo] = new_session(modelo)
    m = remove(foto.convert("RGB"), session=_SESIONES[modelo], only_mask=True).convert("L")
    if cache:
        m.save(cache)
    return m


# ------------------------------------------------------------ paisaje continuo

def continuo(capa, n, ancho=1080):
    """Corta una capa ancha (n láminas de ancho) en n pedazos: el paisaje sigue al pasar de una lámina a otra."""
    return [capa.crop((i * ancho, 0, (i + 1) * ancho, capa.height)) for i in range(n)]


# ============================================================ piezas de composición (resueltas en la pieza de prueba
# «¿Por qué ya nada nos conmueve?», 2 nov 2026, y aprobadas por Martín; para todas las líneas)

# ------------------------------------------------------------ las dos voces

def _fuente(nombre, tam, **ejes):
    import dial_noticias as dn
    import oficio
    f = oficio.Fuente(dn.FUENTES / nombre, tam, ejes or None)
    f.tam = tam
    return f


def afirma(tam, peso=700):
    """La voz que dice el hecho: Instrument Sans."""
    return _fuente("InstrumentSans-VF.ttf", tam, wdth=94, wght=peso)


def siente(tam, peso=800):
    """La voz que lo siente: Fraunces itálica suave."""
    return _fuente("Fraunces-Italic-VF.ttf", tam, opsz=144, wght=peso, SOFT=100, WONK=1)


def cartel(tam, peso=560):
    """Fraunces romana para rótulos de cartel (barrio · vereda · resguardo, la cinta)."""
    return _fuente("Fraunces-VF.ttf", tam, opsz=72, wght=peso, SOFT=50, WONK=0)


def cortar(texto, f, ancho):
    lineas, act = [], ""
    for w in texto.split():
        prueba = (act + " " + w).strip()
        if act and f.getlength(prueba) > ancho:
            lineas.append(act)
            act = w
        else:
            act = prueba
    return lineas + [act]


def renglones(img, lineas, y, f, color, paso, centro=True, x=80, pincel=None, semilla=1):
    """Renglones centrados o a la izquierda (y = línea de base del primero); pincel: color de una pincelada detrás."""
    W = img.width
    cajas, pos = [], []
    for i, t in enumerate(lineas):
        w = f.getlength(t)
        x0 = (W - w) / 2 if centro else x
        base = y + i * paso
        pos.append((x0, base, t))
        cajas.append((x0 - f.tam * 0.18, base - f.tam * 0.72, x0 + w + f.tam * 0.14, base + f.tam * 0.2))
    if pincel:
        pincelada(img, cajas, pincel, semilla)
    d = ImageDraw.Draw(img)
    for x0, base, t in pos:
        d.text((x0, base), t, font=f, fill=color, anchor="ls")
    return y + (len(lineas) - 1) * paso


def mixto(img, y, partes, centro=True, x=80):
    """Un renglón con tramos de distinta voz y color: [(texto, fuente, color)]. Es la lista-poema."""
    ancho = sum(f.getlength(t) for t, f, _ in partes)
    x0 = (img.width - ancho) / 2 if centro else x
    d = ImageDraw.Draw(img)
    for t, f, c in partes:
        d.text((x0, y), t, font=f, fill=c, anchor="ls")
        x0 += f.getlength(t)


def firma(img, color=None, izquierda=False, cuenta="@dialmedio", margen=80):
    """@dialmedio con el aro, abajo; si no se da color, lo elige según lo que haya debajo."""
    import al_aire as aa
    W, H = img.size
    f = afirma(24, 650)
    w = 30 + f.getlength(cuenta)
    x0 = margen if izquierda else (W - w) / 2
    if color is None:
        zona = np.asarray(img.crop((int(x0) - 6, H - 84, int(x0 + w) + 6, H - 44)).convert("L"), np.float32)
        color = SEPIA if zona.mean() > 140 else HUESO
    aa.aro(img, x0 + 11, H - 62, 26, color)
    ImageDraw.Draw(img).text((x0 + 30, H - 53), cuenta, font=f, fill=color, anchor="ls")


# ------------------------------------------------------------ pliegos y paisaje continuo

def pliego(w, h, semilla, noche=False):
    """Papel hueso (día) o cartulina (noche), RGBA opaco."""
    a = mt.papel(w, h, CARTULINA if noche else HUESO, semilla, "negro" if noche else "prensa", 1.0)
    return Image.fromarray(np.dstack([a, np.full((h, w), 255)]).astype(np.uint8), "RGBA")


def _agua_bajo_orilla(L, filo, fondo_max):
    """Máscara 0-1 del agua de una laguna o río horizontal: todo lo que queda bajo la orilla (el salto de luz entre
    el monte en sombra y el agua, columna por columna), aun los reflejos oscuros."""
    from numpy.lib.stride_tricks import sliding_window_view as ventanas
    from scipy.ndimage import binary_closing, binary_fill_holes
    h, w = L.shape
    Ls = np.asarray(Image.fromarray((L * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4)), np.float32) / 255
    salto = np.full_like(Ls, -1)
    salto[8:-8] = Ls[16:] - Ls[:-16]
    yy = np.arange(h)[:, None]
    salto[(yy < filo[None, :] + 30) | (yy > fondo_max)] = -1
    orilla = np.argmax(salto, 0).astype(np.float32)
    k = min(301, (w // 2) * 2 - 1)
    orilla = np.median(ventanas(np.pad(orilla, k // 2, mode="edge"), k), 1)
    borde = min(160, w // 10)
    orilla[:borde] = orilla[borde]           # el borde de la foto no deja escalón
    lago = (yy > orilla[None, :]).astype(np.uint8) * 255
    lago = np.asarray(Image.fromarray(lago).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(9)), np.float32) / 255
    lago = binary_fill_holes(binary_closing(lago > 0.5, np.ones((25, 61)))).astype(np.float32)
    return np.asarray(Image.fromarray((lago * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)), np.float32) / 255


def paisaje_continuo(foto, n, ancho=1080, alto=600, recorte=None, agua="orilla", cache=None, semilla=2,
                     color_agua=ANIL, cielo_umbral=0.08):
    """Un paisaje panorámico de n láminas de ancho, en grabado de buril, sin cielo y con el agua en aguada.
    Devuelve (día, noche): RGBA de (n*ancho, alto), papel hueso con tinta sepia y cartulina con tinta clara.
    Cada lámina i (desde 1) toma su tramo con .crop(((i-1)*ancho, 0, i*ancho, alto)) y lo pega abajo.

    agua: "orilla" (laguna o río: todo bajo la orilla), None (sin agua) o una máscara 0-1 propia.
    cache: carpeta donde guardar los dos PNG (el cálculo tarda)."""
    if cache:
        cd, cn = Path(cache) / "paisaje-dia.png", Path(cache) / "paisaje-noche.png"
        if cd.exists() and cn.exists():
            return Image.open(cd), Image.open(cn)
    TW, TH = n * ancho, alto
    im = foto.convert("RGB")
    if recorte:
        im = im.crop(recorte)
    im = im.resize((TW, TH), Image.LANCZOS)
    alfa, filo = horizonte(im, umbral_azul=cielo_umbral, alto_max=0.7, apertura=181, suavizado=31)
    a = np.asarray(im, np.float32) / 255
    L = 0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]
    if isinstance(agua, str):
        lago = _agua_bajo_orilla(L, filo, int(TH * 0.78))
    elif agua is None:
        lago = np.zeros_like(L)
    else:
        lago = np.asarray(agua, np.float32)
    local = np.asarray(Image.fromarray((L * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(40)), np.float32) / 255
    G = np.clip(L + (L - local) * 1.4, 0, 1)                                 # contraste local: el monte se dibuja
    calma = np.asarray(Image.fromarray((G * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(9)), np.float32) / 255
    G = G * (1 - lago) + (0.40 + 0.5 * calma) * lago                         # el agua clara: manda la aguada
    a8 = Image.fromarray((alfa * 255).astype(np.uint8))
    dia = Image.new("RGBA", (TW, TH), (*HUESO, 255))
    dia.alpha_composite(entintar(grabado(G, 5.2, -4, 0.6, 1.5, 0.12, 0.7, semilla=semilla), SEPIA))
    if lago.any():
        aguada(dia, lago * alfa, color_agua, semilla=semilla + 2)
    dia.putalpha(a8)
    noche = Image.new("RGBA", (TW, TH), (*CARTULINA, 255))
    noche.alpha_composite(entintar(grabado(G, 5.2, -4, 0.6, 1.5, 0.05, 0.7, semilla=semilla, clara=True), TINTA_CLARA))
    if lago.any():  # de noche, a media fuerza: el agua no brilla más que el texto
        aguada(noche, lago * alfa, color_agua, semilla=semilla + 2, sobre_negro=True, fuerza=0.5)
    noche.putalpha(a8)
    if cache:
        dia.save(cd)
        noche.save(cn)
    return dia, noche


# ------------------------------------------------------------ figuras que salen del paisaje

def _una_figura(m):
    """Deja solo la mancha más grande de la máscara: fuera astillas del fondo."""
    from scipy.ndimage import label
    et, k = label(np.asarray(m) > 110)
    if k <= 1:
        return m
    tam = np.bincount(et.ravel())
    tam[0] = 0
    return Image.fromarray(np.where(et == tam.argmax(), np.asarray(m), 0).astype(np.uint8))


def _prenda(foto, tono, umbral):
    """La prenda de color como mancha limpia: la más grande, cerrada, con sus brillos rellenos, hasta el borde."""
    from scipy.ndimage import binary_closing, binary_fill_holes, label
    t = color_de(foto, tono, umbral)
    et, k = label(t > 0.5)
    if not k:
        return t
    tam = np.bincount(et.ravel())
    tam[0] = 0
    t = tam[et] > 0.01 * t.size
    t = binary_closing(np.pad(t, 12, mode="edge"), np.ones((21, 21)))[12:-12, 12:-12]
    return binary_fill_holes(t).astype(np.float32)


def persona(foto, alto, papel, cache=None, caja=None, hasta=None, quitar=(), claro=(), tinte="rojo", umbral=0.3,
            color=None, semilla=1):
    """Una persona para sacarla del paisaje, en fotograbado y sin delineado. Devuelve la capa RGBA (ancho, alto);
    se pega con el pie en el borde de abajo de la lámina. Aprobado por Martín el 2 nov 2026.

    papel(w, h) -> RGBA: el papel de la lámina en ese sitio (la figura se imprime en el mismo papel, sin canto).
    caja: encuadre en la foto. hasta: fila donde se corta la figura, después de la máscara (si se cambia el
      encuadre, rembg recalcula y puede pegar manchas del fondo).
    quitar: polígonos (coordenadas del encuadre) de otras personas pegadas; seguir la línea del hombro.
    claro: polígonos donde el fondo claro se coló entre mechones: ahí se quita lo claro y queda el pelo oscuro.
    tinte: la prenda de ese color se ilumina con aguada (color, por defecto la brasa); nunca la piel. None: sin color."""
    foto = foto.convert("RGB")
    if caja:
        foto = foto.crop(caja)
    m = silueta(foto, cache)
    if hasta:
        foto, m = foto.crop((0, 0, foto.width, hasta)), m.crop((0, 0, m.width, hasta))
    if quitar:
        fuera = Image.new("L", m.size, 0)
        for pol in quitar:
            ImageDraw.Draw(fuera).polygon(pol, fill=255)
        m = ImageChops.subtract(m, fuera.filter(ImageFilter.GaussianBlur(1.5)))
    if claro:
        zona = Image.new("L", m.size, 0)
        for pol in claro:
            ImageDraw.Draw(zona).polygon(pol, fill=255)
        L = np.asarray(foto.convert("L"), np.float32) / 255
        luz = np.clip((L - 0.32) * 6, 0, 1) * (np.asarray(zona, np.float32) / 255)
        m = Image.fromarray((np.asarray(m, np.float32) * (1 - luz)).astype(np.uint8))
    tela = Image.fromarray((_prenda(foto, tinte, umbral) * 255).astype(np.uint8)) if tinte else None
    m = _una_figura(m)
    bb = m.point(lambda v: 255 if v > 40 else 0).getbbox()
    foto, m = foto.crop(bb), m.crop(bb)
    k = alto / foto.height
    foto = foto.resize((round(foto.width * k), alto), Image.LANCZOS)
    m = mascara_solida(m.resize(foto.size, Image.LANCZOS)).filter(ImageFilter.MinFilter(3))  # sin halo de fondo
    m = m.filter(ImageFilter.GaussianBlur(0.7))
    capa = papel(foto.width, alto)
    capa.alpha_composite(entintar(fotograbado(foto, 1.22, 0.04, 0.4, semilla=semilla), SEPIA))
    if tela is not None:
        t = np.asarray(tela.crop(bb).resize(foto.size, Image.LANCZOS), np.float32) / 255
        if color is None:
            import al_aire as aa
            color = aa.BRASA
        aguada(capa, t * (np.asarray(m, np.float32) / 255), color, semilla=semilla, fuerza=0.8, sangrado=2,
               desfase=(2, 1))
    capa.putalpha(m)
    return capa


def figura_buril(foto, alto, cache=None, noche=False, modelo="u2net", periodo=4.4, brillo=0.0, contraste=1.35,
                 caja=None, semilla=1):
    """Una planta, animal u objeto recortado en grabado de buril (nunca personas: para ellas, persona()).
    Sin delineado. Devuelve RGBA."""
    foto = foto.convert("RGB")
    if caja:
        foto = foto.crop(caja)
    m = _una_figura(silueta(foto, cache, modelo))
    bb = m.point(lambda v: 255 if v > 40 else 0).getbbox()
    foto, m = foto.crop(bb), m.crop(bb)
    k = alto / foto.height
    foto = foto.resize((round(foto.width * k), alto), Image.LANCZOS)
    m = mascara_solida(m.resize(foto.size, Image.LANCZOS))
    cob = grabado(foto, periodo, -14, 0.5, contraste, brillo, 0.66, semilla=semilla, clara=noche)
    capa = Image.new("RGBA", foto.size, (*(CARTULINA if noche else HUESO), 255))
    capa.alpha_composite(entintar(cob, TINTA_CLARA if noche else SEPIA))
    capa.putalpha(m)
    return capa


# ------------------------------------------------------------ cifra de cartel

def cifra(texto, tam, semilla=9, color=ANIL):
    """La cifra grande del cartel de junta: Fraunces negra y suave, grabada por dentro, pintada a mano con aguada y
    con filete de tinta. Devuelve RGBA."""
    f = _fuente("Fraunces-VF.ttf", tam, opsz=144, wght=900, SOFT=100, WONK=1)
    w, h = int(f.getlength(texto)) + 40, int(tam * 1.15)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).text((20, tam * 0.95), texto, font=f, fill=255, anchor="ls")
    ma = np.asarray(m, np.float32) / 255
    capa = Image.new("RGBA", (w, h), (*HUESO, 255))
    gris = np.clip(0.78 - mt.ruido(w, h, 90, semilla, 3) * 0.35, 0, 1)
    capa.alpha_composite(entintar(grabado(gris, 4.2, -30, 0.3, 1.0, 0.0, 0, semilla=semilla), SEPIA))
    aguada(capa, ma, color, semilla=semilla + 1, fuerza=0.95, desfase=(5, 4))
    filete = np.asarray(m.filter(ImageFilter.MaxFilter(7)), np.float32) / 255
    rgb = np.asarray(capa, np.float32)[..., :3]
    rgb = rgb * ma[..., None] + np.array(SEPIA) * (1 - ma[..., None])
    return Image.fromarray(np.dstack([rgb, np.maximum(filete, ma) * 255]).astype(np.uint8), "RGBA")
