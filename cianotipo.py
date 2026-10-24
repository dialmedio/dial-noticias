"""Texturas de cianotipo para Nuevos mundos posibles (v3, 24 oct 2026).

Martín pidió "un poco más de arte" con texturas, empezando por la del cianotipo; en la revisión de conjunto dijo que
estaba buena "pero se ve muy digital". La v2 tenía tres defectos de máquina: bordes barridos en horizontal (parecían
desenfoque de movimiento), puntos claros redondos (parecían estrellas) y un moteado parejo en una sola escala.

Un cianotipo de verdad se hace así, y eso es lo que se imita, sin descargar nada:
- La emulsión se extiende con una brocha ancha en pasadas paralelas que se montan un poco. Cada pasada tiene su
  propio canto ondulado, y donde dos se montan el azul queda más hondo.
- Dentro de cada pasada se ven las cerdas: vetas finas en la dirección del trazo, más claras y más oscuras.
- Donde la brocha empieza o se levanta, la emulsión se abre en dedos de pincel seco, cada cerda llega hasta un
  punto distinto y la carga se acaba.
- El papel (de acuarela) tiene diente: en las crestas el azul es un poco más claro. Al lavar, el azul sangra apenas
  fuera del borde.

emulsion(): la cobertura y el espesor de la capa pintada. impresion(): el azul de Prusia sobre esa capa, en RGBA para
poner encima del papel. borde(): solo la máscara (para las fotos). foto(): una foto pasada a cianotipo.
"""
import numpy as np
from PIL import Image, ImageFilter, ImageOps

HONDO = np.array((12, 34, 70), np.float32)    # azul de Prusia donde la emulsión es gruesa
MEDIO = np.array((26, 64, 116), np.float32)   # el azul de una capa pareja
CLARO = np.array((88, 128, 172), np.float32)  # donde la capa es delgada (pincel seco)


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


def _linea(n, escala, rng, octavas=3):
    """Ruido de una dimensión (media 0, ~desviación 1) de largo n con detalle a partir de `escala` px."""
    x = np.arange(n, dtype=np.float32)
    total = np.zeros(n, np.float32)
    amp = 1.0
    for o in range(octavas):
        e = max(1.0, escala / 2 ** o)
        pts = rng.normal(0, 1, int(n / e) + 4)
        total += amp * np.interp(x / e, np.arange(len(pts)), pts)
        amp *= 0.5
    return total / 1.5


def _blur(a, r):
    im = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), np.float32) / 255


def emulsion(w, h, caja, semilla=1, pasadas=None, seco=1.0):
    """Cobertura (0-1) y espesor de la emulsión pintada a brocha dentro de `caja` = (x0, y0, x1, y1).

    Las pasadas van en horizontal, de borde a borde de la caja, montadas un 25 %. seco = cuánto se abren los extremos."""
    rng = np.random.default_rng(semilla)
    x0, y0, x1, y1 = caja
    alto = y1 - y0
    n = pasadas or max(3, round(alto / 250))
    paso = alto / n
    yy = np.arange(h, dtype=np.float32)[:, None]
    xx = np.arange(w, dtype=np.float32)[None, :]
    cobertura = np.zeros((h, w), np.float32)
    capas = []
    for k in range(n):
        yc = y0 + paso * (k + 0.5) + rng.normal(0, paso * 0.04)
        media = paso * 0.62  # media altura: se monta con la vecina
        # el canto de cada pasada ondula a dos escalas; la pasada se inclina y se arquea apenas
        inclin = rng.normal(0, 0.012)
        arco = rng.normal(0, 6)
        centro = yc + inclin * (xx - w / 2) + arco * ((xx - w / 2) / (w / 2)) ** 2
        sup = media + 9 * _linea(w, 160, rng)[None, :] + 2.5 * _linea(w, 18, rng, 2)[None, :]
        inf = media + 9 * _linea(w, 160, rng)[None, :] + 2.5 * _linea(w, 18, rng, 2)[None, :]
        d = np.where(yy < centro, sup - (centro - yy), inf - (yy - centro))  # >0 dentro de la pasada
        banda = np.clip(d / 1.6 + 0.5, 0, 1)
        # cerdas: vetas finas a lo largo del trazo, que se ven por tramos (donde la brocha apretó distinto)
        cerdas = np.tanh(_linea(h, 3.5, rng, 2))[:, None]
        tramos = ruido(w, h, 340, 60, semilla * 29 + k, 3)
        veta = ruido(w, h, 520, 4.0, semilla * 31 + k, 3)
        carga = 0.86 + (0.07 * cerdas + 0.08 * (veta - 0.5)) * (0.4 + tramos)
        # la brocha se descarga a lo largo de la pasada: empieza honda y termina más clara
        sentido = rng.choice([-1, 1])
        avance = np.clip((xx - x0) / max(1, x1 - x0), 0, 1)
        avance = avance if sentido > 0 else 1 - avance
        carga = carga * (1 - 0.16 * avance ** 0.9)
        # extremos: cada mechón de cerdas llega hasta un punto distinto (dedos de pincel seco) y se afina
        def extremo():
            return seco * (10 * np.abs(_linea(h, 6, rng, 2)) + 26 * _linea(h, 48, rng, 2) ** 2)[:, None]
        ini = x0 + rng.uniform(-6, 18) + extremo()
        fin = x1 - rng.uniform(-6, 18) - extremo()
        dx = np.minimum(xx - ini, fin - xx)
        punta = np.clip(dx / 1.4 + 0.5, 0, 1)
        agotada = np.clip(dx / (70 * seco + 1), 0, 1) ** 0.7  # cerca del extremo la brocha ya trae poca carga
        hueco = np.clip((ruido(w, h, 90, 9.0, semilla * 17 + k, 2) - 0.74) * 4, 0, 1) * (1 - agotada) ** 1.5  # saltos del pincel seco
        c = banda * punta * (1 - hueco)
        cobertura = np.maximum(cobertura, c)
        capas.append(c * carga * (0.5 + 0.5 * agotada))
    pila = np.stack(capas)
    tope = pila.max(0)
    espesor = tope + 0.22 * (pila.sum(0) - tope)  # donde dos pasadas se montan, el azul es apenas más hondo
    return _blur(cobertura, 0.5), espesor


def color(espesor, w, h, semilla=1):
    """Del espesor al azul: más capa, más hondo; el diente del papel aclara las crestas."""
    t = 1 - np.exp(-2.1 * espesor)  # se satura: dos pasadas montadas no son el doble de oscuras
    nubes = 0.7 * ruido(w, h, 300, semilla=semilla + 5, octavas=3) + 0.3 * ruido(w, h, 70, semilla=semilla + 8, octavas=2)
    t = t * (0.88 + 0.16 * nubes)  # la exposición y el lavado nunca son parejos
    rng = np.random.default_rng(semilla + 6)
    diente = Image.fromarray((rng.random((h, w)) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    diente = (np.asarray(diente, np.float32) / 255 - 0.5) * 2.4
    t = np.clip(t - np.clip(diente, 0, None) * 0.035, 0, 1)
    lo = np.clip(t / 0.62, 0, 1)[..., None]
    hi = np.clip((t - 0.62) / 0.38, 0, 1)[..., None]
    return CLARO + (MEDIO - CLARO) * lo + (HONDO - MEDIO) * hi


def impresion(w, h, caja, semilla=1, seco=0.55):
    """La impresión al sol: el azul de Prusia en la capa pintada, en RGBA (el papel asoma fuera y en los dedos).
    En una lámina entera los extremos se abren menos (seco=0.55) para que el pincel seco no muerda el texto."""
    cob, esp = emulsion(w, h, caja, semilla, seco=seco)
    rgb = color(esp, w, h, semilla)
    sangrado = np.clip(_blur(cob, 2.5) * 0.22 - 0.02, 0, 1)  # el azul que sangra al lavar, fuera del borde
    alfa = np.maximum(cob * 0.97, sangrado)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), alfa * 255]).astype(np.uint8), "RGBA")


def borde(w, h, caja, semilla=1, cola=90):
    """Máscara (0-1) de un área pintada a brocha (para enmarcar las fotos en cianotipo). cola: cuánto se abren
    los extremos, en la misma escala de la v2 (90 = la lámina entera, ~45 = una foto)."""
    cob, _ = emulsion(w, h, caja, semilla, seco=cola / 90)
    return cob


def foto(im, w, h, semilla=1, margen=26):
    """Una foto pasada a cianotipo con la emulsión de brocha en los bordes (RGBA, el papel asoma por fuera)."""
    im = ImageOps.fit(im.convert("RGB"), (w, h), Image.LANCZOS)
    g = np.asarray(ImageOps.autocontrast(im.convert("L"), cutoff=1), np.float32) / 255
    cob, esp = emulsion(w, h, (margen, margen, w - margen, h - margen), semilla, seco=0.6)
    densidad = (1 - g) ** 0.9 * np.clip(esp / (esp.max() + 1e-6) * 1.15, 0.7, 1)
    rgb = color(densidad * 1.6, w, h, semilla)
    papel = np.array((236, 232, 220), np.float32)
    luz = np.clip(1 - densidad * 1.25, 0, 1)[..., None] ** 1.6  # las luces quedan en papel
    rgb = rgb * (1 - luz) + papel * luz
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), cob * 255]).astype(np.uint8), "RGBA")


if __name__ == "__main__":
    import sys
    salida = sys.argv[1] if len(sys.argv) > 1 else "cianotipo-prueba.png"
    fondo = Image.new("RGBA", (1080, 1350), (241, 237, 227, 255))
    fondo.alpha_composite(impresion(1080, 1350, (40, 40, 1040, 1310)))
    fondo.convert("RGB").save(salida)
