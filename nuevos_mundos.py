"""Estilo visual de Termómetro (antes Nuevos Mundos Posibles; v2, 22 oct 2026), la línea de clima y ambiente de Al Aire.

Martín pidió que no fuera predecible ni cuadriculada: más suave, elegante y sutil, coherente con Dial,
con el verde y el naranja juntos. Referentes: The Guardian (titulares en serif, mucho aire, fotos
grandes, datos limpios), La Linterna (impresión) y Mutante (riso de dos tintas).

- Titulares en Instrument Serif, con el acento en cursiva (brasa sobre foto u oscuro, terracota sobre papel).
- Eucalipto (verde suave) + brasa: el par de la línea. Papel y hueso de Dial como campos claros.
- Fotos de las láminas sin foto en riso de dos tintas (eucalipto y brasa), sin grano.
- Rótulos sin caja: una hoja y el texto en mono, como los antetítulos del Guardian.
- La misma estructura de Al Aire: cabecera, logo, crédito abajo, lámina final de pregunta.

v3 (29 oct 2026): más fotográfica y artística. Foto de fondo en todas las láminas con textura de
película (pelicula()), la lámina `reflexion` (pregunta y prosa sobre la foto, sin listas), el aro de
Dial en lugar de la hoja y más aire entre titular y texto.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dial_noticias as dn  # noqa: E402
import al_aire as aa  # noqa: E402

CARBON, PAPEL, HUESO = dn.CARBON, dn.PAPEL, (233, 223, 207)
TERRACOTA, BRASA = dn.TERRACOTA, (229, 138, 58)
EUCALIPTO = (86, 112, 94)          # el verde de la línea: suave, apagado, hacia el gris
EUCALIPTO_HONDO = (44, 62, 50)     # el mismo verde, oscuro: fondo del cierre y tinta del riso
SALVIA = (200, 211, 190)           # verde muy claro, para barras y filetes
GRIS = (95, 85, 76)
SELLO = "TERMÓMETRO"


def g(nombre):  # medidas vivas de al_aire (cambian con el formato)
    return getattr(aa, nombre)


# ------------------------------------------------------------ tipografía

def serif(tam):
    return dn.fuente("InstrumentSerif-Regular.ttf", tam)


def cursiva(tam):
    return dn.fuente("InstrumentSerif-Italic.ttf", tam)


# Letras del cuerpo (29 oct 2026: Martín pidió algo más alternativo, análogo, "aesthetic" e indie).
# "cuerpo" en el JSON elige; todas son OFL y están en fuentes/. r = regular, b = negrilla, i = cursiva.
CUERPOS = {
    "fraunces": {"r": "Fraunces-VF.ttf", "b": "Fraunces-VF.ttf", "i": "Fraunces-Italic-VF.ttf", "peso": 400, "negrita": 720,
                 "ejes": lambda tam, peso: {b"Optical Size": max(9, min(144, tam * 0.42)), b"Weight": peso, b"Softness": 100, b"Wonky": 0},
                 "escala": 1.0},
    "cormorant": {"r": "CormorantGaramond-VF.ttf", "b": "CormorantGaramond-VF.ttf", "i": "CormorantGaramond-Italic-VF.ttf",
                  "peso": 560, "negrita": 700, "ejes": lambda tam, peso: {b"Weight": peso}, "escala": 1.2},
    "bricolage": {"r": "BricolageGrotesque-VF.ttf", "b": "BricolageGrotesque-VF.ttf", "i": "BricolageGrotesque-VF.ttf",
                  "peso": 360, "negrita": 680, "escala": 0.96,
                  "ejes": lambda tam, peso: {b"Optical size": max(12, min(96, tam * 0.4)), b"Weight": peso, b"Width": 92}},
    "spectral": {"r": "Spectral-Light.ttf", "b": "Spectral-SemiBold.ttf", "i": "Spectral-LightItalic.ttf", "escala": 1.0},
}
FRANJA_CUERPO = (46, 44, 41)  # negro grisáceo de la franja de los resaltados del cuerpo
CUERPO = "bricolage"  # lo fija lamina() con cfg["cuerpo"]; Martín eligió Bricolage el 29 oct 2026


def cuerpo(tam, estilo="r"):
    """La letra del texto corrido, según CUERPO. estilo: "r", "b" (negrilla) o "i" (cursiva)."""
    c = CUERPOS[CUERPO]
    tam = tam * c.get("escala", 1.0)
    f = ImageFont.truetype(str(dn.FUENTES / c[estilo]), int(round(tam)))
    if c.get("ejes"):
        ejes = c["ejes"](tam, c["negrita"] if estilo == "b" else c["peso"])
        f.set_variation_by_axes([ejes.get(a["name"], a["default"]) for a in f.get_variation_axes()])
    return f


def _ancho_linea(r, l):
    return sum(r._w(tok) for tok in l) + sum(r._esp(tok[0][1]) for tok in l[1:])


def texto(img, x, y, contenido, tam, ancho, color, inter=1.42, centrar=False):
    """Texto corrido. *así* resalta en negrilla con textura de tinta (29 oct 2026: "si quieres resaltar
    un texto dentro del cuerpo, ponle negrilla y textura"). centrar: cada línea centrada en el ancho."""
    r = dn.Rico(contenido, tam, color=color, acento=color, interlineado=inter)
    r.f, r.fa = cuerpo(tam), cuerpo(tam, "b")
    d = ImageDraw.Draw(img)
    asc, desc = r.f.getmetrics()
    marcas, normales, rects = [], [], []
    for l in r.equilibradas(ancho):
        cx = x + ((ancho - _ancho_linea(r, l)) / 2 if centrar else 0)
        base = y + asc
        tramo = None  # una franja por cada tramo resaltado de la línea
        for i, tok in enumerate(l):
            if i:
                cx += r._esp(tok[0][1])
            for w, ac in tok:
                f = r.fa if ac else r.f
                (marcas if ac else normales).append((cx, base, w))
                if ac:
                    tramo = [tramo[0] if tramo else cx, cx + f.getlength(w), base]
                elif tramo:
                    rects.append(tramo)
                    tramo = None
                cx += f.getlength(w)
        if tramo:
            rects.append(tramo)
        y += r.alto_linea
    if rects:  # 29 oct 2026: lo resaltado va sobre una franja negra grisácea con textura, como tinta impresa
        franja_impresa(img, [[a - tam * 0.18, b - asc * 0.86, c + tam * 0.18, b + desc * 0.55] for a, c, b in rects],
                       FRANJA_CUERPO, int(sum(r_[0] for r_ in rects)) % 997)
    for cx, base, w in normales:
        d.text((cx, base), w, font=r.f, fill=color, anchor="ls")
    if marcas:
        negrilla_textura(img, marcas, r.fa, color)
    return y


def negrilla_textura(img, marcas, f, color):
    """Negrilla con textura de tinta: la letra no carga pareja y deja poros, como impresa con tipos."""
    asc, desc = f.getmetrics()
    x0 = int(min(m[0] for m in marcas)) - 4
    x1 = int(max(m[0] + f.getlength(m[2]) for m in marcas)) + 4
    y0 = int(min(m[1] for m in marcas) - asc) - 4
    y1 = int(max(m[1] for m in marcas) + desc) + 4
    w, h = x1 - x0, y1 - y0
    m = Image.new("L", (w, h), 0)
    dm = ImageDraw.Draw(m)
    for cx, base, palabra in marcas:
        dm.text((cx - x0, base - y0), palabra, font=f, fill=255, anchor="ls")
    a = np.asarray(m, np.float32) / 255
    rng = np.random.default_rng(abs(x0 * 7 + y0) % 9973)
    poros = (rng.random((h, w)) > 0.07).astype(np.float32)
    carga = np.clip(0.9 + 0.1 * aa.ruido_suave(w, h, abs(x0 + y0) % 997, 5, 5, 1.0), 0.7, 1)
    a = a * np.clip(0.6 + 0.4 * poros, 0, 1) * carga
    alfa = 255  # la negrilla va a tinta plena: tiene que resaltar sobre el resto del texto
    capa = Image.new("RGBA", (w, h), tuple(color[:3]) + (0,))
    capa.putalpha(Image.fromarray((np.clip(a, 0, 1) * alfa).astype(np.uint8)))
    img.alpha_composite(capa, (x0, y0))


def alto_cuerpo(contenido, tam, ancho, inter=1.42):
    r = dn.Rico(contenido, tam, interlineado=inter)
    r.f, r.fa = cuerpo(tam), cuerpo(tam, "b")
    return r.alto(r.equilibradas(ancho))


def rico_serif(contenido, tam, color, inter=1.0):
    r = dn.Rico(contenido, tam, color=color, acento=CARBON, interlineado=inter)
    r.f, r.fa = serif(tam), cursiva(tam)
    return r


def dibujar_franja(img, r, x, y, lineas, franja, centrar=None):
    """Como Rico.dibujar, pero el acento (*así*) va en cursiva carbón sobre una franja (22 oct 2026:
    la cursiva naranja sola no siempre se leía). Primero se pintan todas las franjas y después todo
    el texto, para que las letras que bajan de la línea de arriba no queden tapadas."""
    d = ImageDraw.Draw(img)
    asc = r.f.getmetrics()[0]
    tam = r.tam
    posiciones = []  # (x, base, palabra, acento)
    yy = y
    for l in lineas:
        cx, base = x + ((centrar - _ancho_linea(r, l)) / 2 if centrar else 0), yy + asc
        for i, tok in enumerate(l):
            if i:
                cx += r._esp(tok[0][1])
            for w, ac in tok:
                f = r.fa if ac else r.f
                posiciones.append((cx, base, w, ac, f.getlength(w)))
                cx += f.getlength(w)
        yy += r.alto_linea
    tramo, rects = None, []  # una franja continua por cada tramo de palabras con acento en la misma línea
    for cx, base, w, ac, ancho in posiciones + [(0, -1, "", False, 0)]:
        if ac and tramo and tramo[2] == base:
            tramo[1] = cx + ancho
        else:
            if tramo:
                rects.append([tramo[0] - tam * 0.08, tramo[2] - tam * 0.72, tramo[1] + tam * 0.1, tramo[2] + tam * 0.2])
            tramo = [cx, cx + ancho, base] if ac else None
    semilla = sum(map(ord, "".join(p[2] for p in posiciones))) % 997
    if franja == "tiza":  # 29 oct 2026: el acento en cursiva del mismo color, con una raya de tiza debajo
        for cx, base, w, ac, _ in posiciones:
            d.text((cx, base), w, font=r.fa if ac else r.f, fill=r.color, anchor="ls")
        for k, rc in enumerate(rects):
            tiza(img, rc[0] + tam * 0.04, rc[2] - tam * 0.02, rc[3] - tam * 0.03, max(7, tam * 0.11), semilla + k)
        return yy
    if rects:
        franja_impresa(img, rects, franja, semilla)
    for cx, base, w, ac, _ in posiciones:
        d.text((cx, base), w, font=r.fa if ac else r.f, fill=CARBON if ac else r.color, anchor="ls")
    return yy


def tiza(img, x0, x1, y, grosor, semilla, color=PAPEL):
    """Una raya de tiza blanca bajo el acento (Martín, 29 oct 2026, en lugar de la franja): trazo a mano,
    apenas curvo y en leve diagonal, más delgado en las puntas, con poros por donde se ve el fondo y
    vetas a lo largo, como la tiza que arrastra sobre un tablero."""
    rng = np.random.default_rng(semilla)
    pad = int(grosor * 3)
    w, h = int(x1 - x0) + 2 * pad, int(grosor * 7)
    s = 3
    m = Image.new("L", (w * s, h * s), 0)
    dm = ImageDraw.Draw(m)
    n = 48
    xs = np.linspace(pad, w - pad, n)
    curva = (h / 2 + np.sin(np.linspace(0, np.pi, n)) * grosor * 0.5 * rng.choice([-1, 1])
             + np.linspace(1, -1, n) * grosor * rng.uniform(0.2, 0.7) + np.cumsum(rng.normal(0, grosor * 0.03, n)))
    for i in range(n - 1):
        t = i / (n - 1)
        gi = grosor * (0.45 + 0.55 * np.sin(np.pi * min(1, 0.08 + t * 0.9)))
        dm.line([(xs[i] * s, curva[i] * s), (xs[i + 1] * s, curva[i + 1] * s)], fill=255, width=max(1, int(gi * s)))
    a = np.asarray(m.resize((w, h), Image.LANCZOS), np.float32) / 255
    poros = (rng.random((h, w)) > 0.3).astype(np.float32)
    vetas = np.asarray(Image.fromarray((rng.random((h, max(2, w // 7))) * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR), np.float32) / 255
    a = a * np.clip(0.35 + 0.65 * poros, 0, 1) * (0.55 + 0.45 * vetas)
    capa = Image.new("RGBA", (w, h), tuple(color[:3]) + (0,))
    capa.putalpha(Image.fromarray((np.clip(a, 0, 1) * 240).astype(np.uint8)))
    img.alpha_composite(capa, (max(0, int(x0 - pad)), max(0, int(y - h / 2))))


def franja_impresa(img, rects, color, semilla):
    """Franjas con tinta de impresión: el borde muerde un poco, la tinta carga desigual y no hay
    esquinas perfectas. Es lo que separa una franja impresa de un rectángulo de pantalla."""
    x0 = int(max(0, min(r[0] for r in rects) - 12))
    y0 = int(max(0, min(r[1] for r in rects) - 12))
    x1 = int(min(img.width, max(r[2] for r in rects) + 12))
    y1 = int(min(img.height, max(r[3] for r in rects) + 12))
    w, h = x1 - x0, y1 - y0
    if w < 4 or h < 4:
        return
    m = Image.new("L", (w, h), 0)
    dm = ImageDraw.Draw(m)
    for r in rects:
        dm.rectangle([r[0] - x0, r[1] - y0, r[2] - x0, r[3] - y0], fill=255)
    a = np.asarray(m.filter(ImageFilter.GaussianBlur(2.2)), np.float32) / 255
    borde = 0.6 * aa.ruido_suave(w, h, semilla, 5, 5, 1.0) + 0.4 * aa.ruido_suave(w, h, semilla + 1, 30, 4, 1.0)
    a = np.clip((a - 0.5 + borde * 0.09) * 9 + 0.5, 0, 1)
    carga = 0.86 + 0.14 * np.clip(aa.ruido_suave(w, h, semilla + 2, 90, 14, 1.4) * 0.5 + 0.5, 0, 1)
    capa = Image.new("RGBA", (w, h), color + (0,))
    capa.putalpha(Image.fromarray((a * carga * 255).astype(np.uint8)))
    img.alpha_composite(capa, (x0, y0))


def alto_titular(contenido, tam, ancho, inter=1.0):
    r = rico_serif(contenido, tam, PAPEL, inter)
    return r.alto(r.equilibradas(ancho))


def titular(img, x, y, contenido, tam, ancho, color=PAPEL, franja="tiza", inter=1.0, centrar=False):
    """Titular en serif. Sobre fotos el acento va en cursiva con una raya de tiza debajo (29 oct 2026);
    sobre papel, en una franja (salvia)."""
    r = rico_serif(contenido, tam, color, inter)
    return dibujar_franja(img, r, x, y, r.equilibradas(ancho), franja, ancho if centrar else None)


def espaciado(d, x, y, texto, f, fill, tracking=0.14, sombra=False):
    """Texto en versalitas con espacio entre letras (PIL no lo trae). Devuelve el x final.
    sombra: una sombra carbón de 2 px, para letra pequeña clara sobre fotos con zonas claras."""
    if sombra:
        espaciado(d, x + 1.5, y + 1.5, texto, f, CARBON + (170,), tracking)
    for ch in texto:
        d.text((x, y), ch, font=f, fill=fill, anchor="ls")
        x += f.getlength(ch) + f.size * tracking
    return x


def aro(img, cx, cy, d, color, punto=BRASA, angulo=90):
    """El símbolo de Dial (marca v4, el aro con punto) en la estación de Termómetro: el punto a 90°,
    a la derecha. Reemplaza a la hoja desde el 29 oct 2026 (lo pidió Martín). Medidas de
    dial-web/src/lib/aro.mjs, en una caja de 200: R 84, trazo 22,4, punto 24,9, aire 9,4.
    d = lado de la caja en px; (cx, cy) = su centro."""
    s = 4
    tam = round(d * s)
    k = tam / 200
    c = tam / 2
    rc, trazo, rp, aire = (84 - 11.2) * k, 22.4 * k, 24.9 * k, 9.4 * k
    a = np.radians(angulo - 90)
    px, py = c + rc * np.cos(a), c + rc * np.sin(a)
    anillo = Image.new("L", (tam, tam), 0)
    da = ImageDraw.Draw(anillo)
    da.ellipse([c - rc - trazo / 2, c - rc - trazo / 2, c + rc + trazo / 2, c + rc + trazo / 2], fill=255)
    da.ellipse([c - rc + trazo / 2, c - rc + trazo / 2, c + rc - trazo / 2, c + rc - trazo / 2], fill=0)
    da.ellipse([px - rp - aire, py - rp - aire, px + rp + aire, py + rp + aire], fill=0)
    bola = Image.new("L", (tam, tam), 0)
    ImageDraw.Draw(bola).ellipse([px - rp, py - rp, px + rp, py + rp], fill=255)
    capa = Image.new("RGBA", (tam, tam), tuple(color[:3]) + (0,))
    capa.putalpha(anillo)
    p = Image.new("RGBA", (tam, tam), tuple(punto[:3]) + (0,))
    p.putalpha(bola)
    capa.alpha_composite(p)
    capa = capa.resize((round(d), round(d)), Image.LANCZOS)
    img.alpha_composite(capa, (round(cx - d / 2), round(cy - d / 2)))


def antetitulo(img, x, y, texto, color, hoja=None, sombra=False):
    """Antetítulo como en prensa: el aro de Dial y el texto en sans espaciada, sin caja. y = línea base.
    Sobre fotos y verdes, el texto va en papel y el aro también, con el punto en brasa."""
    aro(img, x + 10, y - 8, 22, color, hoja or BRASA)
    espaciado(ImageDraw.Draw(img), x + 30, y, texto.upper(), dn.sans(21, 650, 100), color, sombra=sombra)


def cabecera(img, meta, fondo="foto"):
    """Cabecera de sección, como la de un periódico (22 oct 2026: las cajas se veían "muy digitales"):
    el aro de Dial y "Termómetro" en serif cursiva, el logo a la derecha, un filete fino
    a todo el ancho y debajo la fecha en versalitas. fondo: "foto", "claro" (papel) u "oscuro" (verdes)."""
    W, H, M, T, R = g("W"), g("H"), g("M"), g("T"), g("R")
    if fondo == "foto":
        img.alpha_composite(dn.degradado_superior(W, H, hasta=(T + 230) / H, fuerza=0.8))
    tinta = CARBON if fondo == "claro" else PAPEL
    d = ImageDraw.Draw(img)
    aro(img, M + 16, T + 19, 36, tinta)
    d.text((M + 42, T + 33), "Termómetro", font=cursiva(40), fill=tinta, anchor="ls")
    lg = dn.logo(36)
    if fondo == "claro":
        a = np.asarray(lg).copy()
        claro = a[..., 0] > 200
        a[claro, :3] = CARBON
        a[~claro & (a[..., 3] > 0), :3] = TERRACOTA
        lg = Image.fromarray(a)
    img.alpha_composite(lg, (W - M - R - lg.width, T + 2))
    filete = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(filete).line([(M, T + 54), (W - M - R, T + 54)], fill=tinta + (150,), width=2)
    img.alpha_composite(filete)
    espaciado(d, M, T + 88, meta.upper(), dn.sans(19, 600, 100), tinta + (235,), sombra=fondo == "foto")


def pie(img, contenido, color, n=None, cfg=None):
    """Desde el 29 oct 2026 (Martín, estructural) las láminas no llevan créditos ni número de lámina:
    los créditos van en la descripción, como siempre. "pie": true en el JSON los vuelve a poner."""
    if not (cfg and cfg.get("pie")):
        return
    W, H, M, B, R = g("W"), g("H"), g("M"), g("B"), g("R")
    d = ImageDraw.Draw(img)
    d.text((M, H - B + 58), contenido.upper(), font=dn.mono(15), fill=color, anchor="ls")
    total = len(cfg.get("laminas", [])) if cfg else 0
    if n and total:
        d.text((W - M - R, H - B + 58), f"{n:02d} / {total:02d}", font=dn.mono(17, True), fill=color, anchor="rs")


# ------------------------------------------------------------ riso de dos tintas

def riso(foto, tam, foco=(0.5, 0.5), fondo=PAPEL, tinta1=EUCALIPTO, tinta2=BRASA, contraste=1.7, desfase=(5, 4)):
    """Foto impresa en riso con dos tintas: el verde lleva las sombras y la brasa los medios tonos,
    con el registro apenas corrido. Sin grano: la imagen queda limpia y suave."""
    gris = dn.recortar(foto.convert("L"), f"{tam[0]}:{tam[1]}", foco).resize(tam, Image.LANCZOS)
    a = np.asarray(gris, np.float32) / 255
    a = np.clip((a - 0.5) * contraste + 0.52, 0, 1)
    d1 = np.clip(1 - a, 0, 1) ** 1.15 * 0.92
    d2 = np.clip(1 - np.abs(a - 0.6) / 0.34, 0, 1) ** 1.3 * 0.5
    d2 = np.roll(np.roll(d2, desfase[0], axis=1), desfase[1], axis=0)
    base = np.array(fondo, np.float32)[None, None, :] / 255
    t1 = np.array(tinta1, np.float32)[None, None, :] / 255
    t2 = np.array(tinta2, np.float32)[None, None, :] / 255
    out = base * (1 - d1[..., None] * (1 - t1)) * (1 - d2[..., None] * (1 - t2))
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).convert("RGBA")


def banda(cfg, lam, tam):
    """La foto de la banda de arriba (fichas y lugares): a color, con la misma colorización de las fotos,
    o en riso de dos tintas si la lámina dice "riso": true. Martín, 22 oct: la Amazonía en riso "parecía
    una mancha"; la banda tiene que leerse a primera vista."""
    ruta = cfg["_base"] / lam["semitono"]
    foco = tuple(lam.get("foco_semitono", (0.5, 0.5)))
    if lam.get("riso"):
        return riso(Image.open(ruta).convert("RGB"), tam, foco)
    foto = dn.preparar_foto(ruta, lam.get("ajuste"), f"{tam[0]}:{tam[1]}", foco)
    return pelicula(foto.resize(tam, Image.LANCZOS).convert("RGBA"), sum(tam), cfg)


# ------------------------------------------------------------ película (29 oct 2026)

def pelicula(img, semilla, cfg=None, fuerza=1.0):
    """Textura de foto análoga. Martín, 29 oct 2026: foto de fondo en todas las láminas, "con una textura
    de foto análoga", más fotográfico que de infografía. El 18 oct el ruido digital se había visto de baja
    calidad, así que esto imita la película y no el sensor: negros levantados, sombras un poco cálidas,
    un halo rojizo alrededor de las luces (halación) y un grano fino que se agrupa, más visible en los
    medios tonos y casi sin color. Va sobre la foto y antes del texto, que queda nítido.
    "pelicula": false en el JSON la apaga."""
    if cfg is not None and cfg.get("pelicula") is False:
        return img
    a = np.asarray(img.convert("RGB"), np.float32) / 255
    h, w = a.shape[:2]
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    luz = np.clip((lum - 0.7) / 0.3, 0, 1)
    halo = Image.fromarray((luz * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(max(4, w * 0.011)))
    a = a + (np.asarray(halo, np.float32) / 255)[..., None] * np.array([0.22, 0.075, 0.02], np.float32) * fuerza
    a = 0.04 + a * 0.92  # negros levantados y luces que no queman, como en el papel
    a = a + ((1 - lum) ** 2)[..., None] * np.array([0.02, 0.008, -0.014], np.float32) * fuerza
    rng = np.random.default_rng(semilla)
    # grano fino (29 oct 2026, 2.ª ronda: el primero se veía grueso): casi del tamaño del píxel y más leve
    gw, gh = max(2, round(w / 1.12)), max(2, round(h / 1.12))
    grano = np.asarray(Image.fromarray(rng.normal(0, 1, (gh, gw)).astype(np.float32), "F").resize((w, h), Image.BICUBIC))
    color = np.stack([np.asarray(Image.fromarray(rng.normal(0, 1, (gh // 2, gw // 2)).astype(np.float32), "F")
                                 .resize((w, h), Image.BICUBIC)) for _ in range(3)], -1)
    peso = (0.4 + 2.4 * lum * (1 - lum)) * 0.026 * fuerza
    a = a + grano[..., None] * peso[..., None] + color * 0.004 * fuerza
    # fuga de luz: un resplandor cálido que entra por un borde, distinto en cada lámina (pantalla)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    borde = rng.integers(4)
    dist = [xx / w, 1 - xx / w, yy / h, 1 - yy / h][borde]
    centro = rng.uniform(0.15, 0.85)
    eje = [yy / h, yy / h, xx / w, xx / w][borde]
    fuga = np.exp(-(dist / 0.16) ** 2) * np.exp(-((eje - centro) / 0.35) ** 2) * rng.uniform(0.10, 0.2) * fuerza
    tono = np.array([1.0, 0.48, 0.2], np.float32)
    a = 1 - (1 - a) * (1 - fuga[..., None] * tono)
    # viñeta suave, como la de un lente viejo
    r = np.sqrt(((xx / w - 0.5) / 0.5) ** 2 + ((yy / h - 0.5) / 0.5) ** 2) / np.sqrt(2)
    a = a * (1 - 0.18 * np.clip(r - 0.45, 0, 1) ** 1.4 / 0.55 ** 1.4)[..., None]
    out = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    # polvo y algún pelo en el negativo: pocos y pequeños, claros (en la copia, el polvo sale blanco)
    polvo = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dp = ImageDraw.Draw(polvo)
    for _ in range(int(rng.integers(14, 26))):
        px, py, rr = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(0.6, 2.2)
        dp.ellipse([px - rr, py - rr * rng.uniform(0.6, 1.4), px + rr, py + rr], fill=(250, 246, 236, int(rng.integers(60, 140))))
    for _ in range(int(rng.integers(0, 3))):
        x0, y0 = rng.uniform(0, w), rng.uniform(0, h)
        puntos = [(x0 + k * rng.uniform(4, 9), y0 + np.sin(k / 3 + rng.uniform(0, 3)) * 6 + k * rng.uniform(-3, 3)) for k in range(int(rng.integers(6, 14)))]
        dp.line(puntos, fill=(250, 246, 236, 70), width=1)
    out.alpha_composite(polvo.filter(ImageFilter.GaussianBlur(0.5)))
    if img.mode == "RGBA":
        out.putalpha(img.getchannel("A"))
    return out


def foto_fondo(cfg, lam, n):
    """La foto de la lámina, a sangre y con película (en video va sin, porque la capa es transparente)."""
    img = aa.foto_base(cfg, lam)
    return img if lam.get("_video") else pelicula(img, 300 + n, cfg)


def parrafo_serif(img, x, y, contenido, tam, ancho, color, cursiva_=True, inter=1.18):
    """Texto corrido en Instrument Serif (cursiva por defecto). Devuelve la y final."""
    f = cursiva(tam) if cursiva_ else serif(tam)
    d = ImageDraw.Draw(img)
    for linea in aa.partir(contenido, f, ancho):
        d.text((x, y + tam * 0.86), linea, font=f, fill=color, anchor="ls")
        y += tam * inter
    return y


# ------------------------------------------------------------ láminas

def l_portada(cfg, lam, n):
    W, H, M, B, R = g("W"), g("H"), g("M"), g("B"), g("R")
    img = foto_fondo(cfg, lam, n)
    ancho = W * lam["ancho"] - M if lam.get("ancho") else (W - 2 * M - R)
    tam = 116 * lam.get("escala", 1.0)
    baj = lam.get("bajada", "")
    alto = alto_titular(lam["titulo"], tam, ancho, 0.98) + (44 + alto_cuerpo(baj, 40, ancho - 40) if baj else 0)
    if lam.get("posicion") == "arriba":  # la portada va abajo; el resto, arriba o centrado (Martín, 29 oct 2026)
        y = g("T") + 200
        if lam.get("oscuro"):
            img.alpha_composite(Image.new("RGBA", (W, H), CARBON + (round(255 * lam["oscuro"]),)))
        img.alpha_composite(dn.degradado_superior(W, H, hasta=min(0.95, (y + alto + 260) / H), fuerza=0.95))
    else:
        y = H - B - alto
        img.alpha_composite(dn.degradado_inferior(W, H, desde=max(0.05, (y - 480) / H), fuerza=0.85))  # velo largo
        aa.degradado_bajo(img, max(0.12, (y - 150) / H), 0.97)
    cabecera(img, lam.get("meta", cfg["meta"]))
    if lam.get("rotulo"):
        antetitulo(img, M, y - 30, lam["rotulo"], PAPEL, BRASA, sombra=True)
    y = titular(img, M, y, lam["titulo"], tam, ancho, inter=0.98)
    if baj:  # 29 oct 2026: más aire entre el titular y el texto
        texto(img, M, y + 44, baj, 40, ancho - 40, PAPEL + (238,))
    pie(img, aa.credito(lam), PAPEL + (190,), n, cfg)
    return img


def l_foto(cfg, lam, n):
    W, H, M, T, B, R = g("W"), g("H"), g("M"), g("T"), g("B"), g("R")
    img = foto_fondo(cfg, lam, n)
    arriba = lam.get("posicion") == "arriba"
    if arriba:
        img.alpha_composite(dn.degradado_superior(W, H, hasta=0.58, fuerza=0.86))
    ancho = W * lam["ancho"] - M if lam.get("ancho") else (W - 2 * M - R)
    tx, tt = lam.get("texto", ""), lam.get("titulo", "")
    alto = (alto_titular(tt, 92, ancho) + 34 if tt else 0) + alto_cuerpo(tx, 40, ancho)
    y = H - B - alto if not arriba else T + 200
    if not arriba:
        aa.degradado_bajo(img, max(0.2, (y - 170) / H), 0.92)
    cabecera(img, lam.get("meta", cfg["meta"]))
    if lam.get("rotulo"):
        antetitulo(img, M, y - 28, lam["rotulo"], PAPEL, BRASA, sombra=True)
    if tt:
        y = titular(img, M, y, tt, 92, ancho) + 34
    texto(img, M, y, tx, 40, ancho, PAPEL + (240,))
    personas = lam.get("persona") or []
    for p in ([personas] if isinstance(personas, dict) else personas):
        aa.rotulo_persona(img, p)
    pie(img, aa.credito(lam), PAPEL + (190,), n, cfg)
    return img


def l_ficha(cfg, lam, n):
    """Papel con el dato grande en serif. Opcional: banda de foto en riso arriba (semitono, foco_semitono),
    antetítulo (rotulo), dato, dato_pie, destacado (la frase clave sobre franja brasa), titulo, texto,
    campos [[etiqueta, valor]] en lista con filetes,
    items numerados y cierre. También hace de lámina de análisis en esta línea."""
    W, H, M, T, B, R = g("W"), g("H"), g("M"), g("T"), g("B"), g("R")
    img = aa.campo(PAPEL, 50 + n, 0.025)
    ancho = W - 2 * M - R
    capa = Image.new("RGBA", (W, H * 2), (0, 0, 0, 0))  # el contenido va en su capa para poder centrarlo
    y = T + 150
    con_foto = bool(lam.get("semitono"))
    if con_foto:
        alto_foto = round(H * lam.get("alto_foto", 0.4))
        img.alpha_composite(banda(cfg, lam, (W, alto_foto)), (0, 0))
        y = alto_foto + 56
        if lam.get("pie_foto"):
            ImageDraw.Draw(img).text((M, alto_foto + 34), lam["pie_foto"].upper(), font=dn.mono(18), fill=GRIS, anchor="ls")
            y += 18
    d = ImageDraw.Draw(capa)
    if lam.get("rotulo"):
        antetitulo(capa, M, y + 24, lam["rotulo"], EUCALIPTO)
        y += 50
    if lam.get("dato"):
        tam = 260
        while serif(tam).getlength(lam["dato"]) > ancho and tam > 120:
            tam -= 10
        d.text((M - tam * 0.02, y + tam * 0.78), lam["dato"], font=serif(tam), fill=EUCALIPTO, anchor="ls")
        y += tam * 0.86
        if lam.get("dato_pie"):
            y = aa.texto(capa, M, y + 4, lam["dato_pie"], 38, ancho, CARBON, peso=600) + 10
        y += 22
    if lam.get("destacado"):  # la idea que explica la lámina, en cursiva sobre franja brasa
        y = titular(capa, M + 6, y + 4, "*" + lam["destacado"].strip("*") + "*", 66, ancho - 12, color=CARBON, franja=BRASA) + 30
    if lam.get("titulo"):
        y = titular(capa, M, y, lam["titulo"], 84 * lam.get("escala", 1.0), ancho, color=CARBON, franja=SALVIA) + 36
    if lam.get("texto"):
        y = aa.texto(capa, M, y, lam["texto"], 38, ancho, CARBON) + 22
    if lam.get("campos"):
        fe, fv = dn.sans(18, 650, 100), serif(40)
        col = 260
        for etq, valor in lam["campos"]:
            lineas = aa.partir(valor, fv, ancho - col)
            d.line([(M, y), (M + ancho, y)], fill=SALVIA, width=2)
            espaciado(d, M, y + 44, etq.upper(), fe, EUCALIPTO)
            for k, linea in enumerate(lineas):
                d.text((M + col, y + 46 + k * 44), linea, font=fv, fill=CARBON, anchor="ls")
            y += 66 + 44 * (len(lineas) - 1)
    fi = dn.sans(40, 600, 90)
    for i, it in enumerate(lam.get("items", []), 1):  # lista numerada en cursiva terracota
        lineas = aa.partir(it, fi, ancho - 64)
        d.text((M, y + 46), str(i), font=cursiva(58), fill=TERRACOTA, anchor="ls")
        for k, linea in enumerate(lineas):
            d.text((M + 64, y + 42 + k * 48), linea, font=fi, fill=CARBON, anchor="ls")
        y += 62 + 48 * (len(lineas) - 1)
    if lam.get("cierre"):  # remate con filete brasa
        y += 22
        h = aa.alto_texto(lam["cierre"], 38, ancho - 30)
        d.rectangle([M, y + 4, M + 5, y + h - 8], fill=BRASA)
        y = aa.texto(capa, M + 26, y, lam["cierre"], 38, ancho - 30, CARBON) + 10
    libre = (H - B - 20) - y
    baja = 0 if con_foto else max(0, round(libre * 0.45))
    img.alpha_composite(capa.crop((0, -baja, W, H - baja)))
    if y > H - B - 10:
        print(f"  ojo: la lámina {n} se pasa de alto; acorta el texto o los campos")
    cabecera(img, lam.get("meta", cfg["meta"]), "foto" if con_foto else "claro")
    pie(img, lam.get("credito", ""), GRIS)
    return img


def l_serie(cfg, lam, n):
    """Una serie en barras horizontales: "serie": [["2021", 13038], ...]; la última barra va en brasa.
    Con rotulo, dato (el cambio, p. ej. "−74 %") y dato_pie arriba. Para comparar periodos (gobiernos),
    cada fila lleva un tercer valor con su grupo y "grupos" da los nombres en orden: el primero va en
    hueso oscuro y el segundo en salvia, con una leyenda debajo."""
    W, H, M, T, B, R = g("W"), g("H"), g("M"), g("T"), g("B"), g("R")
    img = aa.campo(PAPEL, 55 + n, 0.025)
    cabecera(img, lam.get("meta", cfg["meta"]), "claro")
    d = ImageDraw.Draw(img)
    ancho = W - 2 * M - R
    y = T + 170
    if lam.get("rotulo"):
        antetitulo(img, M, y, lam["rotulo"], EUCALIPTO)
        y += 26
    if lam.get("dato"):
        tam = 250
        d.text((M - 5, y + tam * 0.8), lam["dato"], font=serif(tam), fill=EUCALIPTO, anchor="ls")
        y += tam * 0.88
    if lam.get("dato_pie"):
        y = aa.texto(img, M, y, lam["dato_pie"], 38, ancho, CARBON, peso=600) + 40
    serie = lam["serie"]
    tope = max(fila[1] for fila in serie)
    grupos = lam.get("grupos", [])
    tonos = [(204, 194, 180), SALVIA]
    fe, fv = dn.mono(24, True), dn.sans(32, 600, 88)
    col, alto_barra, paso = 110, 46, (70 if len(serie) <= 6 else 62)
    largo = ancho - col - 150
    for k, fila in enumerate(serie):
        etq, v = fila[0], fila[1]
        ultima = k == len(serie) - 1
        tono = tonos[grupos.index(fila[2]) % 2] if len(fila) > 2 and fila[2] in grupos else SALVIA
        w = max(6, largo * v / tope)
        cy = y + k * paso
        d.text((M, cy + alto_barra * 0.72), str(etq), font=fe, fill=GRIS, anchor="ls")
        d.rectangle([M + col, cy, M + col + w, cy + alto_barra], fill=BRASA if ultima else tono)
        d.text((M + col + w + 16, cy + alto_barra * 0.74), f"{v:,}".replace(",", "."), font=fv,
               fill=CARBON if ultima else GRIS, anchor="ls")
    y += paso * len(serie)
    if grupos:
        x = M + col
        for k, nombre in enumerate(grupos):
            d.rectangle([x, y + 4, x + 22, y + 26], fill=tonos[k % 2])
            x = espaciado(d, x + 32, y + 24, nombre.upper(), dn.sans(18, 650, 100), CARBON) + 30
        y += 40
    if lam.get("unidad"):
        for k, linea in enumerate(aa.partir(lam["unidad"], dn.sans(22, 500, 96), ancho - col)):
            d.text((M + col, y + 22 + k * 30), linea, font=dn.sans(22, 500, 96), fill=GRIS, anchor="ls")
    pie(img, lam.get("credito", ""), GRIS)
    return img


def l_citas(cfg, lam, n):
    """Hueso: las voces, en serif, con comillas grandes en brasa."""
    W, H, M, T, B, R = g("W"), g("H"), g("M"), g("T"), g("B"), g("R")
    img = aa.campo(HUESO, 20 + n, 0.025)
    cabecera(img, (lam.get("rotulo") or lam.get("meta", cfg["meta"])).upper(), "claro")
    d = ImageDraw.Draw(img)
    ancho = W - 2 * M - R - 90
    fa = dn.sans(23, 600, 96)
    bloques = []
    for c in lam["citas"]:
        r = rico_serif(c["texto"], 60, CARBON, 1.08)
        bloques.append((r, r.lineas(ancho), aa.partir(c["autor"], fa, ancho)))
    total = sum(r.alto(l) + 30 + 30 * len(a) for r, l, a in bloques) + 90 * (len(bloques) - 1)
    y = T + 120 + (H - T - 120 - B - total) / 2
    for k, (r, l, autor) in enumerate(bloques):
        d.text((M - 6, y + 150), "“", font=serif(230), fill=BRASA, anchor="ls")
        y = dibujar_franja(img, r, M + 90, y, l, SALVIA) + 30
        for linea in autor:
            d.text((M + 90, y + 10), linea, font=fa, fill=EUCALIPTO, anchor="ls")
            y += 30
        if k < len(bloques) - 1:
            y += 45
            d.line([(M + 90, y), (M + 90 + 120, y)], fill=BRASA, width=3)
            y += 45
    pie(img, lam.get("credito", ""), GRIS)
    return img


def l_lugar(cfg, lam, n):
    """Campo eucalipto con el lugar en serif cursiva grande, texto e items numerados en cursiva brasa.
    Opcional: una banda de foto en riso arriba (semitono)."""
    W, H, M, T, B, R = g("W"), g("H"), g("M"), g("T"), g("B"), g("R")
    img = aa.campo(EUCALIPTO, 10 + n, 0.03)
    ancho = W - 2 * M - R
    y = T + 150 if lam.get("semitono") else T + 280  # sin foto, el bloque baja hacia el centro
    if lam.get("semitono"):
        alto_foto = round(H * 0.27)
        img.alpha_composite(banda(cfg, lam, (W, alto_foto)), (0, 0))
        y = alto_foto + 30
    cabecera(img, lam.get("meta", cfg["meta"]), "foto" if lam.get("semitono") else "oscuro")
    d = ImageDraw.Draw(img)
    tam = 230
    while cursiva(tam).getlength(lam["titulo"]) > ancho and tam > 100:
        tam -= 10
    d.text((M - 6, y + tam * 0.8), lam["titulo"], font=cursiva(tam), fill=PAPEL, anchor="ls")
    y += tam * 0.95
    if lam.get("rotulo"):
        antetitulo(img, M, y + 10, lam["rotulo"], PAPEL, BRASA)
        y += 46
    if lam.get("texto"):
        y = aa.texto(img, M, y, lam["texto"], 42, ancho, PAPEL) + 26
    fi = dn.sans(42, 500, 92)
    for i, it in enumerate(lam.get("items", []), 1):
        lineas = aa.partir(it, fi, ancho - 70)
        d.text((M, y + 46), str(i), font=cursiva(60), fill=BRASA, anchor="ls")
        for k, linea in enumerate(lineas):
            d.text((M + 70, y + 44 + k * 50), linea, font=fi, fill=PAPEL, anchor="ls")
        y += 66 + 50 * (len(lineas) - 1)
    if y > H - B - 10:
        print(f"  ojo: la lámina {n} se pasa de alto; acorta el texto o los items")
    pie(img, lam.get("credito", ""), PAPEL + (200,))
    return img


def l_paises(cfg, lam, n):
    """Varios lugares, uno debajo del otro (p. ej. "No es solo Brasil"): campo eucalipto, titular con
    franja y, por cada lugar, su nombre en serif cursiva, un dato grande opcional en brasa y un texto que
    se entiende solo. "lugares": [{"nombre", "dato" (opcional), "texto"}]."""
    W, H, M, T, B, R = g("W"), g("H"), g("M"), g("T"), g("B"), g("R")
    img = aa.campo(EUCALIPTO, 70 + n, 0.03)
    cabecera(img, lam.get("meta", cfg["meta"]), "oscuro")
    d = ImageDraw.Draw(img)
    ancho = W - 2 * M - R
    capa = Image.new("RGBA", (W, H * 2), (0, 0, 0, 0))
    dc = ImageDraw.Draw(capa)
    y = 0
    if lam.get("rotulo"):
        antetitulo(capa, M, y + 24, lam["rotulo"], PAPEL, BRASA)
        y += 54
    if lam.get("titulo"):
        y = titular(capa, M, y, lam["titulo"], 88, ancho) + 30
    for k, lugar in enumerate(lam["lugares"]):
        dc.line([(M, y), (M + ancho, y)], fill=PAPEL + (110,), width=2)
        y += 22
        fn = cursiva(64)
        dc.text((M, y + 54), lugar["nombre"], font=fn, fill=PAPEL, anchor="ls")
        if lugar.get("dato"):
            dc.text((M + ancho, y + 58), lugar["dato"], font=serif(76), fill=BRASA, anchor="rs")
        y += 78
        y = aa.texto(capa, M, y, lugar["texto"], 36, ancho, PAPEL + (235,)) + 26
    # el bloque se centra entre la cabecera y el pie
    arriba, abajo = T + 120, H - B - 20
    y0 = arriba + max(0, (abajo - arriba - y) * 0.45)
    img.alpha_composite(capa.crop((0, -round(y0), W, H - round(y0))))
    if y0 + y > abajo + 10:
        print(f"  ojo: la lámina {n} se pasa de alto; acorta los textos")
    pie(img, lam.get("credito", ""), PAPEL + (200,))
    return img


def l_dos(cfg, lam, n):
    """Dos personas con el mismo trato (p. ej. los candidatos de una elección): dos retratos del mismo
    tamaño lado a lado, nombre y cargo en cada uno, y abajo una banda eucalipto con titulo y texto.
    "personas": [{"foto", "foco", "nombre", "cargo", "credito"}, {...}]"""
    W, H, M, B, R = g("W"), g("H"), g("M"), g("B"), g("R")
    img = aa.campo(EUCALIPTO, 60 + n, 0.03)
    arriba = g("T") + 112  # franja de la cabecera: las fotos empiezan debajo, para no tapar caras
    alto = round(H * lam.get("alto_fotos", 0.52))
    medio = 6
    an = (W - medio) // 2
    fn, fc = serif(50), dn.sans(17, 650, 100)
    for k, p in enumerate(lam["personas"]):
        foto = dn.preparar_foto(cfg["_base"] / p["foto"], p.get("ajuste"), f"{an}:{alto}", p.get("foco")).convert("RGBA")
        foto = pelicula(foto.resize((an, alto), Image.LANCZOS), 500 + n + k, cfg)
        foto.alpha_composite(dn.degradado_inferior(an, alto, desde=0.55, fuerza=0.85))
        dd = ImageDraw.Draw(foto)
        dd.text((M * 0.6, alto - 64), p["nombre"], font=fn, fill=PAPEL, anchor="ls")
        espaciado(dd, M * 0.6, alto - 30, p.get("cargo", "").upper(), fc, PAPEL + (225,))
        img.alpha_composite(foto, (k * (an + medio), arriba))
    cabecera(img, lam.get("meta", cfg["meta"]), "oscuro")
    ancho = W - 2 * M - R
    y = arriba + alto + 44
    if lam.get("rotulo"):
        antetitulo(img, M, y + 4, lam["rotulo"], PAPEL, BRASA)
        y += 40
    if lam.get("titulo"):
        y = titular(img, M, y, lam["titulo"], 84, ancho) + 14
    if lam.get("texto"):
        y = aa.texto(img, M, y, lam["texto"], 34, ancho, PAPEL + (235,))
    if y > H - B - 10:
        print(f"  ojo: la lámina {n} se pasa de alto; acorta el texto o baja alto_fotos")
    creditos = " · ".join(p.get("credito", "") for p in lam["personas"] if p.get("credito"))
    pie(img, lam.get("credito", creditos), PAPEL + (190,))
    return img


def l_reflexion(cfg, lam, n):
    """Foto a sangre con película y una pregunta que se explora en prosa. Martín, 29 oct 2026: foto de
    fondo en todas las láminas, un diseño más artístico y fotográfico que de infografía, y textos que se
    lean como reflexión y no como lista; más aire entre el titular y el texto.
    rotulo, titulo (la pregunta, con *acento*), texto (párrafos separados por una línea en blanco),
    citas [{texto, autor}], pregunta (remate en serif cursiva con filete brasa).
    "posicion": "arriba", "centro" o "abajo" (por defecto); "oscuro" (0 a 1, 0.52 por defecto) apaga la foto.
    2.ª ronda (29 oct 2026): sin cabecera (solo la llevan la primera y la última lámina; "cabecera": true
    la pone), "alinear": "centro" centra titular y texto, y la foto va más oscura para que el texto resalte."""
    W, H, M, T, B, R = g("W"), g("H"), g("M"), g("T"), g("B"), g("R")
    img = foto_fondo(cfg, lam, n)
    img.alpha_composite(Image.new("RGBA", (W, H), CARBON + (round(255 * lam.get("oscuro", 0.52)),)))
    centrar = lam.get("alinear") == "centro"
    ancho = W - 2 * M - R if not centrar else W - 2 * M - 40
    x = M if not centrar else (W - ancho) / 2
    capa = Image.new("RGBA", (W, H * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    y = 0
    if lam.get("rotulo"):
        antetitulo(capa, M, y + 24, lam["rotulo"], PAPEL, BRASA, sombra=True)
        y += 64
    if lam.get("titulo"):
        y = titular(capa, x, y, lam["titulo"], 92 * lam.get("escala", 1.0), ancho, centrar=centrar) + 48
    for k, par in enumerate(p for p in lam.get("texto", "").split("\n\n") if p.strip()):
        y = texto(capa, x, y + (28 if k else 0), par.strip(), 41, ancho, PAPEL + (246,), centrar=centrar)
    fa = dn.sans(23, 600, 96)
    for k, c in enumerate(lam.get("citas", [])):
        y += 46 if (k or lam.get("texto")) else 0
        d.text((M - 4, y + 118), "“", font=serif(180), fill=BRASA, anchor="ls")
        r = rico_serif(c["texto"], 56, PAPEL, 1.08)
        y = dibujar_franja(capa, r, M + 74, y, r.lineas(ancho - 74), "tiza") + 22
        for linea in aa.partir(c["autor"], fa, ancho - 74):
            espaciado(d, M + 74, y + 8, linea.upper(), dn.sans(19, 650, 100), PAPEL + (215,), 0.08)
            y += 30
    if lam.get("pregunta"):
        y += 52
        h = parrafo_serif(Image.new("RGBA", (W, H)), M + 30, 0, lam["pregunta"], 56, ancho - 30, PAPEL)
        d.rectangle([M, y + 8, M + 5, y + h - 4], fill=BRASA)
        y = parrafo_serif(capa, M + 30, y, lam["pregunta"], 56, ancho - 30, PAPEL)
    con_cabecera = lam.get("cabecera", False)
    arriba, abajo = (T + 140 if con_cabecera else T + 30), H - B - 24
    pos = "arriba" if lam.get("posicion") == "arriba" else "centro"  # 29 oct 2026: arriba o centrado, nunca abajo
    y0 = arriba if pos == "arriba" else arriba + (abajo - arriba - y) * 0.5
    if pos == "arriba":
        img.alpha_composite(dn.degradado_superior(W, H, hasta=min(0.95, (y0 + y + 180) / H), fuerza=0.85))
    elif pos == "centro":  # un velo más hondo detrás del bloque, que se apaga hacia arriba y hacia abajo
        yy = np.linspace(0, 1, H)[:, None]
        c0, c1 = (y0 - 140) / H, (y0 + y + 140) / H
        t = np.clip(np.minimum((yy - c0) / 0.12, (c1 - yy) / 0.12), 0, 1)
        velo = Image.new("RGBA", (W, H), CARBON + (0,))
        velo.putalpha(Image.fromarray(np.repeat((t * 0.45 * 255).astype(np.uint8), W, 1)))
        img.alpha_composite(velo)
    else:
        aa.degradado_bajo(img, max(0.08, (y0 - 240) / H), 0.93)
    if con_cabecera:
        cabecera(img, lam.get("meta", cfg["meta"]))
    img.alpha_composite(capa.crop((0, -round(y0), W, H - round(y0))))
    if y0 < arriba - 10:
        print(f"  ojo: la lámina {n} se pasa de alto; acorta el texto")
    pie(img, aa.credito(lam), PAPEL + (190,), n, cfg)
    return img


def l_cta(cfg, lam, n):
    """Cierre: la pregunta para comentar, en serif sobre eucalipto hondo, con el signo en cursiva brasa.
    Con "foto", el fondo es esa foto con película bajo un velo eucalipto hondo (29 oct 2026)."""
    W, H, M, T, B, R = g("W"), g("H"), g("M"), g("T"), g("B"), g("R")
    arriba = lam.get("posicion", "arriba") == "arriba"  # 29 oct 2026: la pregunta va arriba por defecto
    if lam.get("foto"):
        img = foto_fondo(cfg, lam, n)
        img.alpha_composite(Image.new("RGBA", (W, H), EUCALIPTO_HONDO + (round(255 * lam.get("oscuro", 0.72)),)))
        if arriba:
            img.alpha_composite(dn.degradado_superior(W, H, hasta=0.5, fuerza=0.75))
        else:  # el bloque de la pregunta va sobre una zona más honda, para que no se pierda
            aa.degradado_bajo(img, 0.38, 0.9)
        aa.degradado_bajo(img, 0.72, 0.85)
    else:
        img = aa.campo(EUCALIPTO_HONDO, 40 + n, 0.04)
    cabecera(img, (lam.get("rotulo") or "Conversemos").upper(), "oscuro")
    d = ImageDraw.Draw(img)
    ancho = W - 2 * M - R
    if not lam.get("foto"):  # sobre una foto, el signo grande tapaba la cara
        d.text((W - M - R + 10, T + 560), "?", font=cursiva(640), fill=BRASA, anchor="rs")
    pregunta, texto_ = lam["pregunta"], lam.get("texto", "")
    tam = 100 * lam.get("escala", 1.0)
    alto = alto_titular(pregunta, tam, ancho) + (40 + alto_cuerpo(texto_, 40, ancho) if texto_ else 0)
    y_pie = H - B - 150
    y = T + 190 if arriba else max(T + 320, y_pie - 70 - alto)
    antetitulo(img, M, y - 30, "Tu opinión", PAPEL, BRASA)
    y = titular(img, M, y, pregunta, tam, ancho)
    if texto_:
        texto(img, M, y + 40, texto_, 40, ancho, PAPEL + (232,))
    fa = dn.sans(24, 650, 100)
    aro(img, M + 11, y_pie + 22, 24, PAPEL)
    x = M + 32
    for k, palabra in enumerate(["COMENTA", "GUARDA", "COMPARTE"]):
        if k:
            x = espaciado(d, x + 4, y_pie + 32, "·", fa, PAPEL + (160,)) + 6
        x = espaciado(d, x, y_pie + 32, palabra, fa, BRASA if k == 0 else PAPEL)
    lg = dn.logo(64)
    img.alpha_composite(lg, (M, round(y_pie + 84)))
    d = ImageDraw.Draw(img)
    d.text((W - M - R, y_pie + 84 + 46), lam.get("cuenta", "@dialmedio"), font=dn.mono(28, True), fill=PAPEL, anchor="rs")
    d.text((M + lg.width + 24, y_pie + 84 + 46), "Sintonizar es conversar.", font=dn.serif(34), fill=BRASA, anchor="ls")
    pie(img, aa.credito(lam) if lam.get("foto") else "", PAPEL + (170,), n, cfg)
    return img


ESTILOS = {"portada": l_portada, "foto": l_foto, "ficha": l_ficha, "serie": l_serie, "citas": l_citas,
           "pais": l_lugar, "lugar": l_lugar, "paises": l_paises, "dos": l_dos, "cta": l_cta,
           "reflexion": l_reflexion}


def estilo_de(lam):
    if lam.get("estilo"):
        return lam["estilo"]
    if lam.get("personas"):
        return "dos"
    if lam.get("lugares"):
        return "paises"
    if lam.get("serie"):
        return "serie"
    if lam.get("tipo") == "texto" and (lam.get("dato") or lam.get("campos")):
        return "ficha"
    return aa.estilo_de(lam)


def lamina(cfg, lam, n):
    global CUERPO
    CUERPO = cfg.get("cuerpo", "bricolage")
    estilo = estilo_de(lam)
    if estilo == "analisis":  # en esta línea, el análisis es una ficha (papel, sin carbón)
        estilo = "ficha"
    return ESTILOS[estilo](cfg, lam, n)


def capa_video(cfg, lam):
    lam = dict(lam, _video=True)
    return (l_portada if estilo_de(lam) == "portada" else l_foto)(cfg, lam, 0)
