"""Materiales de impresión para todas las líneas (v3, 24 oct 2026).

Martín pidió que las piezas se vieran lo menos digitales posible: la textura de cianotipo de Nuevos mundos "estaba
buena pero se veía muy digital". Lo que delata a una textura generada es casi siempre lo mismo: ruido parejo en una
sola escala, bordes que tiemblan igual en todas partes, puntos perfectos y efectos que se notan más que la pieza.
Aquí cada material imita un proceso físico concreto, con sus defectos a la escala real y en dosis que se sienten
más de lo que se ven:

- papel(): la formación del papel (nubes de fibra en tres escalas), fibras sueltas, el diente que agarra la luz y,
  según la clase, las motas del papel reciclado o las manchas del papel de archivo.
- entintar(): una tinta sobre ese papel. La tinta es transparente (multiplica), carga desigual siguiendo la
  formación, deja sal (puntitos donde el papel no tomó) y su borde se abre un pixel donde la fibra la chupa.
- semitono(): trama de periódico de verdad: punto euclidiano girado a 45°, ganancia de punto, bordes comidos por la
  fibra y la tinta que carga distinto en cada zona. No son círculos dibujados uno por uno.
- rasgado(): el borde de un papel roto a mano, con la franja blanca de fibras que deja el desgarro.

Todo es numpy + Pillow (sin scipy), para que también corra en el sandbox del celular. Nada se aplica sobre las
fotos ni sobre el texto corrido: la textura vive en los campos de color y en los elementos gráficos.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


# ------------------------------------------------------------ ruidos

def ruido(w, h, escala, semilla=0, octavas=4, alargue=1.0, persistencia=0.5):
    """Ruido fractal suave entre 0 y 1. escala = tamaño de la mancha mayor en px; alargue > 1 lo estira en x."""
    rng = np.random.default_rng(semilla)
    total = np.zeros((h, w), np.float32)
    peso, amp = 0.0, 1.0
    for o in range(octavas):
        ex, ey = escala * alargue / 2 ** o, escala / 2 ** o
        gx, gy = max(2, int(w / max(ex, 1)) + 3), max(2, int(h / max(ey, 1)) + 3)
        rej = Image.fromarray((rng.random((gy, gx)) * 255).astype(np.uint8))
        total += amp * np.asarray(rej.resize((w, h), Image.BICUBIC), np.float32) / 255
        peso += amp
        amp *= persistencia
    total /= peso
    return np.clip((total - total.mean()) / (total.std() * 4 + 1e-6) + 0.5, 0, 1)


def fino(w, h, semilla, sigma=0.7):
    """Ruido de alta frecuencia (el diente del papel, la fibra que chupa tinta), media 0 y desviación 1."""
    rng = np.random.default_rng(semilla)
    im = Image.fromarray((rng.random((h, w)) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sigma))
    a = np.asarray(im, np.float32)
    return (a - a.mean()) / (a.std() + 1e-6)


def _blur(a, r):
    im = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), np.float32) / 255


# ------------------------------------------------------------ papel

CLASES = {
    # formación (nubes), fibras, diente, motas, manchas
    "prensa":    dict(form=0.030, fibras=0.9, diente=0.012, motas=0.0, manchas=0),
    "archivo":   dict(form=0.020, fibras=0.7, diente=0.010, motas=0.0, manchas=0),   # manchas: solo a pedido
    "reciclado": dict(form=0.030, fibras=1.0, diente=0.012, motas=1.0, manchas=0),
    "copia":     dict(form=0.012, fibras=0.25, diente=0.006, motas=0.0, manchas=0),   # papel bond, casi liso
    "negro":     dict(form=0.060, fibras=1.0, diente=0.020, motas=0.0, manchas=0),    # cartulina negra de álbum
    "tinta":     dict(form=0.030, fibras=0.35, diente=0.010, motas=0.0, manchas=0),   # un campo ya entintado
}


def _fibras(w, h, semilla, n, claro, largo=(10, 46)):
    """Fibras sueltas: trazos cortos y curvos, más claros u oscuros que el papel, casi invisibles uno por uno."""
    s = 2
    capa = Image.new("L", (w * s, h * s), 128)
    d = ImageDraw.Draw(capa)
    rng = np.random.default_rng(semilla)
    for _ in range(n):
        x, y = rng.random() * w * s, rng.random() * h * s
        ang = rng.random() * np.pi
        L = rng.uniform(*largo) * s
        curva = rng.normal(0, 0.6)
        pts = []
        for t in np.linspace(0, 1, 6):
            a = ang + curva * (t - 0.5)
            pts.append((x + np.cos(a) * L * t, y + np.sin(a) * L * t))
        v = 128 + (1 if rng.random() < claro else -1) * rng.uniform(10, 34)
        d.line(pts, fill=int(v), width=max(1, int(rng.uniform(0.8, 1.8) * s)))
    capa = capa.resize((w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.35))
    return (np.asarray(capa, np.float32) - 128) / 128


def papel(w, h, color, semilla=1, clase="prensa", fuerza=1.0):
    """Un pliego de papel del color dado (RGB float 0-255, forma (h, w, 3)).

    La formación es lo que más se nota: las nubes de fibra que se ven al mirar un papel contra la luz. Va en tres
    escalas para que no parezca ruido de pantalla."""
    p = CLASES[clase]
    c = np.array(color, np.float32)[None, None, :]
    nubes = 0.55 * ruido(w, h, 220, semilla, 3) + 0.30 * ruido(w, h, 60, semilla + 1, 3) + 0.15 * ruido(w, h, 16, semilla + 2, 2)
    lum = 1 + (nubes - 0.5) * 2 * p["form"] * fuerza
    if p["fibras"]:
        n = int(w * h / 700 * p["fibras"])
        lum += _fibras(w, h, semilla + 3, n, 0.55) * 0.05 * fuerza
    if p["diente"]:  # el diente: relieve fino iluminado desde arriba a la izquierda
        t = fino(w, h, semilla + 4, 0.8)
        relieve = t - np.roll(np.roll(t, 1, 0), 1, 1)
        lum += relieve * p["diente"] * 0.5 * fuerza
    rgb = c * lum[..., None]
    if clase == "negro":  # en la cartulina negra la fibra clara se ve más que la oscura
        rgb += np.clip(_fibras(w, h, semilla + 5, int(w * h / 900), 1.0, (14, 60)), 0, None)[..., None] * 16 * fuerza
    if p["motas"]:
        rgb = _motas(rgb, semilla + 6, p["motas"] * fuerza)
    for k in range(p["manchas"]):
        rgb = _mancha(rgb, semilla + 20 + k)
    return np.clip(rgb, 0, 255)


def _motas(rgb, semilla, fuerza):
    """Papel reciclado: motas de fibra de otro color (gris, pardo, algún azul) de medio a tres pixeles."""
    h, w = rgb.shape[:2]
    rng = np.random.default_rng(semilla)
    s = 3
    capa = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    tonos = [(70, 64, 58), (96, 82, 66), (120, 112, 100), (64, 74, 96), (140, 120, 96)]
    for _ in range(int(w * h / 4200 * fuerza)):
        x, y = rng.random() * w * s, rng.random() * h * s
        r = rng.gamma(1.6, 0.7) * s
        tono = tonos[rng.integers(len(tonos))]
        alfa = int(rng.uniform(30, 120))
        if rng.random() < 0.25:  # una fibra de color, alargada
            a = rng.random() * np.pi
            L = rng.uniform(4, 14) * s
            d.line([(x, y), (x + np.cos(a) * L, y + np.sin(a) * L)], fill=tono + (alfa,), width=max(1, int(r * 0.7)))
        else:
            pts = [(x + np.cos(t) * r * rng.uniform(0.5, 1.2), y + np.sin(t) * r * rng.uniform(0.5, 1.2)) for t in np.linspace(0, 2 * np.pi, 7)[:-1]]
            d.polygon(pts, fill=tono + (alfa,))
    capa = capa.resize((w, h), Image.LANCZOS)
    a = np.asarray(capa, np.float32)
    al = a[..., 3:4] / 255
    return rgb * (1 - al) + a[..., :3] * al


def _mancha(rgb, semilla):
    """Papel de archivo: una mancha de óxido muy tenue (foxing), irregular, casi en el borde."""
    h, w = rgb.shape[:2]
    rng = np.random.default_rng(semilla)
    cx = rng.choice([rng.uniform(0.02, 0.18), rng.uniform(0.82, 0.98)]) * w
    cy = rng.uniform(0.1, 0.9) * h
    r = rng.uniform(10, 34)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    borde = ruido(w, h, r * 0.8, semilla, 3)
    m = np.clip(1.2 - d - (borde - 0.5) * 0.9, 0, 1) ** 1.5 * 0.10
    oxido = np.array((176, 128, 84), np.float32)[None, None, :]
    return rgb * (1 - m[..., None]) + oxido * m[..., None]


def imagen(rgb):
    return Image.fromarray(np.clip(rgb + 0.5, 0, 255).astype(np.uint8)).convert("RGBA")


# ------------------------------------------------------------ tinta sobre papel

def carga(w, h, semilla, fuerza=1.0):
    """Cuánta tinta tomó cada punto (0.9-1.0): zonas que apretaron menos y la sal de la fibra."""
    zonas = 0.7 * ruido(w, h, 300, semilla, 3) + 0.3 * ruido(w, h, 40, semilla + 1, 2)
    c = 1 - (1 - zonas) * 0.09 * fuerza
    sal = np.clip((fino(w, h, semilla + 2, 0.6) - 2.9) * 1.2, 0, 1)  # pocos puntitos donde la tinta no agarró
    return np.clip(c - sal * 0.5 * fuerza, 0, 1)


def mordido(mascara, semilla, px=1.0):
    """El borde de una mancha de tinta impresa: se abre un pixel aquí y allá donde la fibra la chupa (no tiembla)."""
    m = np.asarray(mascara, np.float32) / 255 if not isinstance(mascara, np.ndarray) else mascara
    h, w = m.shape
    s = _blur(m, 0.9)
    n = 0.65 * fino(w, h, semilla, 0.7) + 0.35 * fino(w, h, semilla + 1, 2.2)
    return np.clip((s - 0.5 + n * 0.06 * px) * 7 + 0.5, 0, 1)


def entintar(base, mascara, color, semilla=1, opacidad=1.0, multiplicar=True, borde=1.0, fuerza=1.0):
    """Pone una tinta sobre `base` (RGB float) donde dice `mascara` (L o array 0-1).

    multiplicar=True: tinta transparente, como el offset y la riso (el papel se ve a través y dos tintas se suman).
    False: tinta cubriente (un papel claro sobre un fondo oscuro, la tinta blanca de serigrafía)."""
    h, w = base.shape[:2]
    m = mascara if isinstance(mascara, np.ndarray) else np.asarray(mascara, np.float32) / 255
    a = (mordido(m, semilla, borde) if borde else m) * carga(w, h, semilla + 7, fuerza) * opacidad
    c = np.array(color, np.float32)[None, None, :]
    if multiplicar:
        tinta = base * (c / 255)
        return base * (1 - a[..., None]) + tinta * a[..., None]
    return base * (1 - a[..., None]) + c * a[..., None]


def campo(w, h, color, semilla=1, clase="tinta", fuerza=1.0):
    """Un campo de color impreso: el papel con su formación, entintado parejo pero no perfecto."""
    return papel(w, h, color, semilla, clase, fuerza)


def franja(img, rects, color, semilla=1, fuerza=1.0):
    """Franjas de resaltador o cajas de rótulo con tinta impresa (sobre una imagen RGBA, en su sitio).

    El canto se abre un pixel donde la fibra chupa, la tinta carga más en el centro del trazo del rodillo y las
    esquinas no son perfectas. Antes cada línea tenía la suya; ahora todas usan esta."""
    if not rects:
        return
    x0 = int(max(0, min(r[0] for r in rects) - 8))
    y0 = int(max(0, min(r[1] for r in rects) - 8))
    x1 = int(min(img.width, max(r[2] for r in rects) + 8))
    y1 = int(min(img.height, max(r[3] for r in rects) + 8))
    w, h = x1 - x0, y1 - y0
    if w < 4 or h < 4:
        return
    m = Image.new("L", (w * 2, h * 2), 0)
    dm = ImageDraw.Draw(m)
    rng = np.random.default_rng(semilla)
    for r in rects:  # cada esquina se corre un poco: ninguna franja es un rectángulo exacto
        j = lambda: rng.uniform(-1.2, 1.2) * 2  # noqa: E731
        pts = [(2 * (r[0] - x0) + j(), 2 * (r[1] - y0) + j()), (2 * (r[2] - x0) + j(), 2 * (r[1] - y0) + j()),
               (2 * (r[2] - x0) + j(), 2 * (r[3] - y0) + j()), (2 * (r[0] - x0) + j(), 2 * (r[3] - y0) + j())]
        dm.polygon(pts, fill=255)
    m = np.asarray(m.resize((w, h), Image.LANCZOS), np.float32) / 255
    a = mordido(m, semilla, 1.0) * (0.94 + 0.06 * ruido(w, h, 120, semilla + 3, 3, alargue=4)) * carga(w, h, semilla + 5, 0.8 * fuerza)
    capa = np.zeros((h, w, 4), np.uint8)
    capa[..., :3] = color
    capa[..., 3] = np.clip(a * 255, 0, 255).astype(np.uint8)
    img.alpha_composite(Image.fromarray(capa, "RGBA"), (x0, y0))


# ------------------------------------------------------------ trama de semitono

def semitono(gris, celda=8.0, angulo=45.0, ganancia=0.08, semilla=1, rugosidad=1.0):
    """Trama de periódico sobre una imagen en gris (L o array 0-1, 1 = blanco). Devuelve la cobertura de tinta 0-1.

    Punto euclidiano (redondo en las luces, cuadros que se tocan en el 50 %, huecos redondos en las sombras),
    calculado como umbral y no dibujando círculos, al doble de resolución. La ganancia de punto engorda un poco
    los medios tonos, y el borde de cada punto lo come la fibra del papel."""
    g = gris if isinstance(gris, np.ndarray) else np.asarray(gris, np.float32) / 255
    h, w = g.shape
    s = 2
    G = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((w * s, h * s), Image.BICUBIC), np.float32) / 255
    yy, xx = np.mgrid[0:h * s, 0:w * s].astype(np.float32)
    a = np.radians(angulo)
    u = (xx * np.cos(a) + yy * np.sin(a)) / (celda * s)
    v = (-xx * np.sin(a) + yy * np.cos(a)) / (celda * s)
    spot = (np.cos(2 * np.pi * u) + np.cos(2 * np.pi * v)) / 4 + 0.5  # 1 en el centro del punto, 0 en el hueco
    oscuro = 1 - G
    oscuro = oscuro + ganancia * 4 * oscuro * (1 - oscuro)  # ganancia de punto: más en los medios tonos
    n = fino(w * s, h * s, semilla, 0.9) * 0.05 * rugosidad + (ruido(w * s, h * s, 90 * s, semilla + 1, 2) - 0.5) * 0.05 * rugosidad
    tinta = np.clip((oscuro - (1 - spot) + n) * 9 + 0.5, 0, 1)
    tinta = np.asarray(Image.fromarray((tinta * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS), np.float32) / 255
    return tinta


# ------------------------------------------------------------ papel rasgado

def rasgado(w, h, y_medio, semilla=1, amplitud=26, color_fibra=(236, 228, 214)):
    """El borde de un papel roto a mano a lo ancho de la lámina.

    Devuelve (mascara_arriba, franja_fibra): la parte que queda arriba (0-1) y la franja clara de fibras que deja el
    desgarro (0-1), que es lo que hace creíble un rasgado. El borde ondula en dos escalas (la mano y la fibra)."""
    rng = np.random.default_rng(semilla)
    x = np.arange(w, dtype=np.float32)

    def onda(escala, n):
        pts = rng.normal(0, 1, int(w / escala) + 4)
        return np.interp(x / escala, np.arange(len(pts)), pts)
    linea = y_medio + amplitud * (0.7 * onda(220, 1) + 0.3 * onda(55, 2)) + 1.6 * onda(14, 3) + 0.5 * onda(3, 6)
    # la franja de fibra: ancha donde el papel se desgarró en bisel, casi nada donde se cortó limpio
    ancho_fibra = np.clip(2 + 7 * np.clip(0.5 + 0.6 * onda(90, 4), 0, 1) ** 1.5 + 1.2 * onda(10, 5), 0.5, 14)
    yy = np.arange(h, dtype=np.float32)[:, None]
    arriba = np.clip(linea[None, :] - yy + 0.5, 0, 1)
    fin = linea[None, :] + ancho_fibra[None, :]
    # el canto exterior de la fibra es blando y peludo, el interior (donde empieza la tinta) es nítido
    pel = fino(w, h, semilla + 7, 0.7)
    fibra = np.clip((fin - yy) / 2.2 + 0.35 * pel, 0, 1) * (yy >= linea[None, :] - 0.5)
    fibra = np.clip(fibra - arriba, 0, 1)
    return arriba, fibra
