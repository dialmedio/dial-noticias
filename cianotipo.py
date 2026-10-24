"""Texturas de cianotipo para Nuevos mundos posibles (24 oct 2026).

Martín pidió "un poco más de arte" con texturas, empezando por la del cianotipo. Un cianotipo real tiene tres rasgos
que se imitan aquí, sin descargar nada (todo se genera, así no hay licencias de por medio):
- La emulsión se aplica a pincel: el azul no llega parejo a los bordes, deja colas de pincel seco y el papel asoma.
- El azul de Prusia es moteado: zonas más hondas y más claras, vetas en la dirección del pincel.
- Puntos claros donde la emulsión no agarró, y la fibra del papel debajo.

campo(): un rectángulo de azul moteado. borde(): la máscara de un área pintada a pincel dentro de la lámina.
impresion(): las dos juntas, en RGBA, lista para poner encima del papel.
"""
import numpy as np
from PIL import Image, ImageFilter

HONDO, CLARO = np.array((13, 38, 76), np.float32), np.array((38, 84, 140), np.float32)  # azul de Prusia, sombra y luz


def ruido(w, h, escala_x, escala_y=None, semilla=0, octavas=4):
    """Ruido suave de valores (fbm) entre 0 y 1; escala_y distinta a escala_x lo estira en vetas."""
    escala_y = escala_y or escala_x
    rng = np.random.default_rng(semilla)
    total, peso, amp = np.zeros((h, w), np.float32), 0.0, 1.0
    for o in range(octavas):
        gx, gy = max(2, int(w / escala_x * 2 ** o) + 2), max(2, int(h / escala_y * 2 ** o) + 2)
        rejilla = Image.fromarray((rng.random((gy, gx)) * 255).astype(np.uint8))
        capa = np.asarray(rejilla.resize((w, h), Image.BICUBIC), np.float32) / 255
        total += capa * amp
        peso += amp
        amp *= 0.5
    total /= peso
    return (total - total.min()) / (np.ptp(total) + 1e-6)


def campo(w, h, semilla=1):
    """El azul del cianotipo: moteado, con vetas de pincel horizontales, grano de papel y puntos sin emulsión."""
    mote = ruido(w, h, 300, semilla=semilla)
    nubes = ruido(w, h, 90, semilla=semilla + 4, octavas=3)
    vetas = ruido(w, h, 800, 60, semilla=semilla + 1, octavas=3)
    grano = ruido(w, h, 2.5, semilla=semilla + 2, octavas=2)
    t = 0.36 + 0.36 * (mote - 0.5) + 0.10 * (nubes - 0.5) + 0.16 * (vetas - 0.5) + 0.06 * (grano - 0.5)
    rgb = HONDO + (CLARO - HONDO) * np.clip(t, 0, 1)[..., None]
    # puntos donde la emulsión no agarró: pocos, pequeños y blandos
    puntos = ruido(w, h, 9, semilla=semilla + 3, octavas=1)
    claros = np.clip((puntos - 0.994) / 0.006, 0, 1)
    claros = np.asarray(Image.fromarray((claros * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6)), np.float32) / 255
    rgb = rgb + (np.array((200, 212, 224), np.float32) - rgb) * (claros[..., None] * 0.45)
    return rgb


def borde(w, h, caja, semilla=1, cola=90):
    """Máscara (0–1) de un área pintada a pincel. caja = (x0, y0, x1, y1). Los bordes laterales dejan colas de pincel
    seco en la dirección del trazo (horizontal); arriba y abajo el borde es irregular pero más contenido."""
    x0, y0, x1, y1 = caja
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    irregular = (ruido(w, h, 120, semilla=semilla + 10, octavas=5) - 0.5) * 40
    trazos = ruido(w, h, 900, 26, semilla=semilla + 11, octavas=3)  # pasadas de pincel: anchas y de largo variable
    dx = np.minimum(xx - x0, x1 - xx) + irregular + (trazos - 0.5) * cola
    dy = np.minimum(yy - y0, y1 - yy) + irregular * 0.8
    d = np.minimum(dx, dy)
    alfa = np.clip(d / 3 + 0.5, 0, 1)
    # pincel seco cerca del borde: la emulsión se abre en hilos finos
    seco = ruido(w, h, 240, 2.2, semilla=semilla + 12, octavas=3)
    zona = np.clip(1 - d / 60, 0, 1) ** 1.5
    alfa *= 1 - zona * np.clip((seco - 0.5) * 2.6, 0, 1) * 0.85
    return np.clip(alfa, 0, 1)


def impresion(w, h, caja, semilla=1):
    """La impresión al sol: el azul moteado dentro de un área pintada a pincel, en RGBA."""
    rgb = campo(w, h, semilla)
    a = borde(w, h, caja, semilla)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8), "RGBA")


def foto(im, w, h, semilla=1, margen=26):
    """Una foto pasada a cianotipo con la emulsión de pincel en los bordes (RGBA, el papel asoma por fuera)."""
    from PIL import ImageOps
    im = ImageOps.fit(im.convert("RGB"), (w, h), Image.LANCZOS)
    g = np.asarray(ImageOps.autocontrast(im.convert("L"), cutoff=1), np.float32) / 255
    mote = ruido(w, h, 240, semilla=semilla)
    t = np.clip(g ** 0.92 * 0.9 + 0.08 * (mote - 0.5), 0, 1)
    sombra, luz = np.array((14, 38, 72), np.float32), np.array((236, 232, 220), np.float32)
    rgb = sombra + (luz - sombra) * t[..., None]
    a = borde(w, h, (margen, margen, w - margen, h - margen), semilla, cola=48)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8), "RGBA")


if __name__ == "__main__":
    import sys
    salida = sys.argv[1] if len(sys.argv) > 1 else "cianotipo-prueba.png"
    impresion(1080, 1350, (40, 40, 1040, 1310)).save(salida)
