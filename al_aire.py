"""Estilo visual de Al Aire (v2, aprobado por Martín el 18 oct 2026).

Referentes: Mutante (campos planos, titulares condensados, collage en semitono,
etiquetas en caja) y La Linterna (tipos de madera, tinta con textura de prensa,
registro imperfecto). Todo dentro de la paleta Dial; la brasa pasa a ser el color
de Al Aire (el manual ya la reserva para los estados "en vivo").

La línea Termómetro, antes Nuevos Mundos Posibles ("seccion": "nuevos-mundos") la dibuja nuevos_mundos.py y la de Arte y memoria
("seccion": "arte") arte.py; las dos usan
las piezas de este archivo (cabecera, textos, fotos, hoja) con su propio estilo.
"""
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dial_noticias as dn  # noqa: E402
import materia as mt  # noqa: E402

CARBON, PAPEL, HUESO = dn.CARBON, dn.PAPEL, (233, 223, 207)
TERRACOTA, BRASA = dn.TERRACOTA, (229, 138, 58)
W, H = 1080, 1350
M = 72
T, B, R = 62, 110, 0   # cabecera, margen inferior y margen derecho extra (zona segura en 9:16)
FORMATO = "4:5"
SELLO = "AL AIRE"

# Tintas de la línea ("seccion" en el JSON). Una línea con otra estructura (Nuevos mundos) tiene su módulo.
#   acento: franja, sello y numeración · fondo: análisis y cierre · campo: lámina de lugar
#   tinta: signo del cierre · comillas: las de la lámina de citas, sobre papel · sombra: segunda pasada del tipo de madera
#   simbolo: lo que va en el sello ("punto" en vivo u "hoja")
SECCIONES = {
    # v5 (29 oct 2026): la luz roja de Dial es solo el punto; el campo, el signo y las comillas van en brasa
    "al-aire": dict(sello="Al aire", acento=BRASA, fondo=CARBON, campo=BRASA, tinta=BRASA,
                    comillas=BRASA, sombra=PAPEL, simbolo="punto"),
}
ACENTO, FONDO, CAMPO, TINTA, COMILLAS, SOMBRA = BRASA, CARBON, BRASA, BRASA, BRASA, PAPEL
SIMBOLO = "punto"


def seccion(cfg):
    """Aplica la tinta de la línea de la noticia (Al Aire por defecto)."""
    global SELLO, ACENTO, FONDO, CAMPO, TINTA, COMILLAS, SOMBRA, SIMBOLO
    s = SECCIONES.get(cfg.get("seccion"), SECCIONES["al-aire"])  # Nuevos mundos usa las medidas y tintas de base
    SELLO = cfg.get("sello", s["sello"]).upper()
    ACENTO, FONDO, CAMPO, TINTA = s["acento"], s["fondo"], s["campo"], s["tinta"]
    COMILLAS, SOMBRA = s["comillas"], s["sombra"]
    SIMBOLO = s["simbolo"]


def lienzo(w, h, formato=None):
    """Ajusta las medidas globales a la lámina (4:5 por defecto; 9:16 deja la zona segura de redes)."""
    global W, H, T, B, R, FORMATO
    W, H = w, h
    alto = h / w >= 1.6
    T, B, R = (150, 330, 110) if alto else (62, 110, 0)
    FORMATO = formato or ("9:16" if alto else "4:5")


# ------------------------------------------------------------ texturas de impresión

def ruido_fractal(w, h, semilla, escalas=(6, 24, 90), pesos=(0.5, 0.3, 0.2)):
    rng = np.random.default_rng(semilla)
    total = np.zeros((h, w), np.float32)
    for esc, p in zip(escalas, pesos):
        pw, ph = max(2, w // esc), max(2, h // esc)
        base = Image.fromarray((rng.random((ph, pw)) * 255).astype(np.uint8))
        total += p * np.asarray(base.resize((w, h), Image.BICUBIC), np.float32) / 255
    return total / sum(pesos)


def ruido_suave(w, h, semilla, kx, ky, desenfoque=1.4):
    """Ruido continuo sin cuadrícula: azar a baja resolución, desenfoque gaussiano y ampliación.
    kx, ky = tamaño de la mancha en px; si kx > ky salen vetas horizontales (como la madera)."""
    rng = np.random.default_rng(semilla)
    pw, ph = max(4, round(w / kx)), max(4, round(h / ky))
    base = Image.fromarray((rng.random((ph, pw)) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(desenfoque))
    a = np.asarray(base.resize((w, h), Image.BILINEAR), np.float32) / 255
    return (a - a.mean()) / (a.std() + 1e-6)  # media 0, desviación 1


def tinta(mascara, semilla, fuerza=1.0):
    """Máscara (L) -> alfa con aspecto de tipo de madera impreso a mano (v3, 19 oct 2026).

    - Borde nítido pero irregular: el tipo gastado muerde el contorno (sin halo borroso).
    - Veta de la madera: la tinta se carga en franjas horizontales largas, no en puntos.
    - Huecos alargados donde la veta no tomó tinta, más frecuentes en unas zonas que en otras.
    - El contorno siempre carga más tinta que el centro (el rodillo aprieta en los bordes).
    """
    w, h = mascara.size
    m = np.asarray(mascara, np.float32) / 255
    # borde: desplaza el umbral con ruido fino y suave, y corta nítido
    suave = np.asarray(mascara.filter(ImageFilter.GaussianBlur(2.2)), np.float32) / 255
    mordida = 0.6 * ruido_suave(w, h, semilla, 5, 5, 1.2) + 0.4 * ruido_suave(w, h, semilla + 1, 14, 14, 1.2)
    borde = np.clip((suave - 0.5 + mordida * 0.1 * fuerza) * 16 + 0.5, 0, 1)
    # interior: veta horizontal modulada por zonas de presión
    veta = 0.6 * ruido_suave(w, h, semilla + 2, 70, 3, 1.0) + 0.4 * ruido_suave(w, h, semilla + 3, 26, 2, 0.8)
    zona = ruido_suave(w, h, semilla + 4, 260, 200, 1.5)  # dónde la prensa apretó menos
    adentro = np.asarray(mascara.filter(ImageFilter.GaussianBlur(9)), np.float32) / 255
    adentro = np.clip((adentro - 0.55) / 0.45, 0, 1)  # 0 cerca del borde, 1 en el centro del trazo
    umbral = 1.15 - 0.55 * np.clip(zona * 0.5 + 0.5, 0, 1)  # en zonas flojas aparecen más huecos
    hueco = np.clip((veta - umbral) * 9, 0, 1) * adentro * fuerza  # canto nítido, como tinta que no tomó
    # pique: poros sueltos y nítidos de la madera, pocos y repartidos
    pique = np.clip((ruido_suave(w, h, semilla + 5, 2.6, 2.6, 0.7) - 2.4) * 6, 0, 1) * np.clip(adentro * 2, 0, 1) * fuerza
    carga = 0.9 + 0.1 * np.clip(veta * 0.35 + 0.5, 0, 1)
    a = borde * carga * (1 - 0.85 * hueco) * (1 - 0.7 * pique)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def campo(color, semilla, manchas=None, clase=None):
    """Campo impreso (v3, materia.py): el papel con su formación y la tinta que carga desigual.
    El papel claro va como papel de prensa; los colores, como tinta plana sobre papel."""
    clase = clase or ("prensa" if sum(color) > 600 else "tinta")
    return mt.imagen(mt.campo(W, H, color, semilla, clase))


def estampar(base, mascara, color, semilla, desfase=(0, 0), multiplicar=False, fuerza=1.0, opacidad=1.0, debajo_de=None):
    alfa = tinta(mascara, semilla, fuerza)
    if opacidad < 1:
        alfa = alfa.point(lambda v: int(v * opacidad))
    if desfase != (0, 0):
        alfa = ImageChops.offset(alfa, *desfase)
    if debajo_de is not None:  # la pasada de abajo solo asoma por fuera de la de arriba
        alfa = ImageChops.multiply(alfa, ImageChops.invert(debajo_de.filter(ImageFilter.MaxFilter(3))))
    capa = Image.new("RGBA", base.size, color + (0,))
    capa.putalpha(alfa)
    if multiplicar:
        rgb = Image.composite(Image.new("RGB", base.size, color), Image.new("RGB", base.size, (255, 255, 255)), capa.getchannel("A"))
        out = ImageChops.multiply(base.convert("RGB"), rgb).convert("RGBA")
        base.paste(out)
    else:
        base.alpha_composite(capa)


def semitono(foto, tam, celda, tinta_color, fondo_color, angulo=22, contraste=1.25, foco=(0.5, 0.5), luz=False):
    """Foto en semitono de una tinta (como la riso de Mutante). v3: trama de periódico de verdad (materia.py),
    con punto euclidiano a 45°, ganancia de punto y la fibra comiendo el borde de cada punto, sobre papel entintado."""
    g = dn.recortar(foto.convert("L"), f"{tam[0]}:{tam[1]}", foco).resize(tam, Image.LANCZOS)
    a = np.asarray(g, np.float32) / 255
    a = np.clip((a - 0.5) * contraste + 0.5, 0, 1)
    if luz:  # la tinta marca las luces: tinta clara sobre fondo oscuro, sin negativo
        a = 1 - a
    cob = mt.semitono(a, celda, 45 if angulo == 22 else angulo, 0.1, semilla=int(celda * 31 + tam[1]))
    base = mt.campo(tam[0], tam[1], fondo_color, 11, "tinta")
    claro = sum(tinta_color) > sum(fondo_color)  # tinta clara sobre fondo oscuro: cubre; oscura sobre claro: multiplica
    out = mt.entintar(base, cob, tinta_color, 12, multiplicar=not claro, borde=0)
    return mt.imagen(out)


def hoja(img, cx, cy, r, color):
    """El símbolo de Nuevos mundos posibles: una hoja inclinada con su nervio (va donde Al Aire lleva el punto)."""
    s = 4
    tam = round(r * 2.6 * s)
    m = Image.new("L", (tam, tam), 0)
    t = np.linspace(0, np.pi, 40)
    largo, ancho = r * 2.2 * s, r * 0.82 * s
    xs = np.concatenate([np.linspace(-largo / 2, largo / 2, 40), np.linspace(largo / 2, -largo / 2, 40)])
    ys = np.concatenate([-np.sin(t) * ancho, np.sin(t)[::-1] * ancho])
    ang = np.radians(-40)
    px = xs * np.cos(ang) - ys * np.sin(ang) + tam / 2
    py = xs * np.sin(ang) + ys * np.cos(ang) + tam / 2
    d = ImageDraw.Draw(m)
    d.polygon(list(zip(px, py)), fill=255)
    nx = np.array([-largo / 2 * 0.7, largo / 2 * 0.55])  # nervio calado
    d.line(list(zip(nx * np.cos(ang) + tam / 2, nx * np.sin(ang) + tam / 2)), fill=0, width=max(1, round(r * 0.14 * s)))
    tx = np.array([-largo / 2 - r * 0.45 * s, -largo / 2 + r * 0.1 * s])  # tallo
    d.line(list(zip(tx * np.cos(ang) + tam / 2, tx * np.sin(ang) + tam / 2)), fill=255, width=max(1, round(r * 0.18 * s)))
    m = m.resize((tam // s, tam // s), Image.LANCZOS)
    capa = Image.new("RGBA", m.size, color + (0,))
    capa.putalpha(m)
    img.alpha_composite(capa, (round(cx - m.width / 2), round(cy - m.height / 2)))


# El aro de Dial (marca v4, dial-web/src/lib/aro.mjs) en una caja de 200: radio, trazo, punto y respiro.
# Cada línea lo lleva con el punto en su estación (v3, 24 oct 2026: una familia, seis voces). Los puntos van
# siempre en la mitad de arriba: abajo a la derecha el aro se lee como una Q.
ARO = dict(R=84, trazo=22.4, punto=24.9, aire=9.4)
ARO_COMPACTO = dict(R=84, trazo=32.5, punto=26.9, aire=6.6)  # 24 px o menos: trazo más grueso
ESTACIONES = {"al-aire": 0, "nuevos-mundos": 90, "tecnologia": 45, "mundos": -45, "arte": -90, "dial": 45}


PLUMA = dict(eje=-28, contraste=0.42, curva=1.3, engrosa=1.12)  # marca v5: el aro trazado a pluma


def aro(img, cx, cy, tam, color, punto=None, angulo=0):
    """Dibuja el aro de Dial centrado en (cx, cy), de `tam` px de lado, con el punto en `angulo` (0° = arriba).
    Marca v5 (29 oct 2026): el aro de pluma, como la o de una pluma de punta ancha (dial-web/src/lib/aro.mjs)."""
    g = ARO_COMPACTO if tam <= 24 else ARO
    s = 8
    lado = round(tam * s)
    k = lado / 200
    m = Image.new("L", (lado, lado), 0)
    d = ImageDraw.Draw(m)
    rc = (g["R"] - g["trazo"] / 2) * k
    c = lado / 2
    t = g["trazo"] * PLUMA["engrosa"] * k
    th = np.linspace(0, 2 * np.pi, 360, endpoint=False)
    gr = t * (PLUMA["contraste"] + (1 - PLUMA["contraste"]) * np.abs(np.cos(th - np.radians(PLUMA["eje"]))) ** PLUMA["curva"])
    d.polygon([(c + (rc + q / 2) * np.cos(a_), c + (rc + q / 2) * np.sin(a_)) for a_, q in zip(th, gr)], fill=255)
    d.polygon([(c + (rc - q / 2) * np.cos(a_), c + (rc - q / 2) * np.sin(a_)) for a_, q in zip(th, gr)], fill=0)
    a = np.radians(angulo - 90)
    px, py = c + rc * np.cos(a), c + rc * np.sin(a)
    hueco = (g["punto"] + g["aire"]) * k
    d.ellipse([px - hueco, py - hueco, px + hueco, py + hueco], fill=0)
    m = m.resize((round(tam), round(tam)), Image.LANCZOS)
    capa = Image.new("RGBA", m.size, color + (0,))
    capa.putalpha(m)
    x0, y0 = round(cx - tam / 2), round(cy - tam / 2)
    img.alpha_composite(capa, (x0, y0))
    p = Image.new("L", (lado, lado), 0)
    rp = g["punto"] * k
    ImageDraw.Draw(p).ellipse([px - rp, py - rp, px + rp, py + rp], fill=255)
    p = p.resize((round(tam), round(tam)), Image.LANCZOS)
    capa = Image.new("RGBA", p.size, (punto or color) + (0,))
    capa.putalpha(p)
    img.alpha_composite(capa, (x0, y0))


def ancho_versal(texto_, f, tracking=0.06):
    """Ancho de un texto en versales con interletra (y kerning)."""
    if not texto_:
        return 0
    k = getattr(f, "kern", lambda a, b: 0)
    return sum(f.getlength(ch) for ch in texto_) + sum(k(texto_[i], texto_[i + 1]) for i in range(len(texto_) - 1)) \
        + f.size * tracking * (len(texto_) - 1)


def versal(img, x, y, texto_, f, fill, tracking=0.06, sombra=False, ancla="l"):
    """Versales con interletra, como se componen los antetítulos y las etiquetas en prensa (Pillow no trae
    tracking). y = línea base. sombra: una sombra carbón leve para letra pequeña clara sobre fotos.
    Devuelve el x final."""
    d = ImageDraw.Draw(img)
    total = ancho_versal(texto_, f, tracking)
    x = x - {"l": 0, "m": total / 2, "r": total}[ancla]
    if sombra:  # un halo blando, no una sombra corrida (la corrida se ve de procesador de texto)
        pad = round(f.size * 0.9)
        x0, y0 = int(x) - pad, int(y - f.size) - pad
        capa = Image.new("RGBA", (round(total) + 2 * pad, round(f.size * 1.3) + 2 * pad), (0, 0, 0, 0))
        versal(capa, x - x0, y - y0, texto_, f, CARBON + (255,), tracking)
        a = capa.getchannel("A").filter(ImageFilter.GaussianBlur(f.size * 0.22)).point(lambda v: int(v * 0.62))
        capa = Image.new("RGBA", capa.size, CARBON + (0,))
        capa.putalpha(a)
        img.alpha_composite(capa, (max(0, x0), max(0, y0)), (max(0, -x0), max(0, -y0)))
    k = getattr(f, "kern", lambda a, b: 0)
    for i, ch in enumerate(texto_):
        d.text((x, y), ch, font=f, fill=fill, anchor="ls")
        x += f.getlength(ch) + f.size * tracking + (k(ch, texto_[i + 1]) if i + 1 < len(texto_) else 0)
    return x


def etiqueta_f(tam):
    """La letra de las etiquetas de Al Aire (v3): la misma condensada de los titulares, en semibold."""
    return dn.sans(tam, 640, 82)


# ------------------------------------------------------------ tipografía

def madera(tam):  # titulares de impacto: Instrument Sans al 75 % de ancho y peso 700
    return dn.sans(tam, 700, 75)


def titular(texto, tam, ancho, interlineado=0.9, acento="banda"):
    """Corta en líneas. Devuelve [(palabras [(txt, acento)], ancho)]."""
    f, fa = madera(tam), dn.serif(tam * 1.1)
    toks = dn._tokens(texto)
    esp = f.getlength(" ")

    def wt(t):
        # en "banda" el acento va en la misma sans: medirlo con la serif desfasaba la franja
        return sum((fa if (a and acento == "serif") else f).getlength(x) for x, a in t)
    def cortar(lim):
        lineas, act, x = [], [], 0
        for t in toks:
            w = wt(t)
            if act and x + esp + w > lim:
                lineas.append(act)
                act, x = [], 0
            x += (esp if act else 0) + w
            act.append(t)
        lineas.append(act)
        return lineas
    n = len(cortar(ancho))  # mismo número de líneas, lo más parejas posible (sin viudas)
    lo, hi = ancho * 0.4, ancho
    for _ in range(18):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if len(cortar(mid)) > n else (lo, mid)
    return f, fa, cortar(hi), tam * interlineado, wt, esp


def alto_titular(texto, tam, ancho, interlineado=0.9, acento="banda"):
    _, _, lineas, alto, _, _ = titular(texto, tam, ancho, interlineado, acento)
    return len(lineas) * alto


def alto_texto(contenido, tam, ancho, inter=1.2):
    r = dn.Rico(contenido, tam, 500, interlineado=inter)
    r.f = dn.sans(tam, 500, 96)
    return r.alto(r.equilibradas(ancho))


def dibujar_titular(img, x, y, texto, tam, ancho, color=PAPEL, acento="banda", interlineado=0.9):
    """acento: "banda" (palabras sobre franja brasa, en carbón) o "serif" (cursiva brasa).

    Primero se pintan todas las franjas y después todo el texto: así las letras que bajan
    (g, j, p, q, y, coma) de la línea de arriba quedan encima de la franja y nunca cortadas."""
    f, fa, lineas, alto, wt, esp = titular(texto, tam, ancho, interlineado, acento)
    d = ImageDraw.Draw(img)
    asc = f.getmetrics()[0]

    extra = tam * 0.09 if acento == "banda" else 0  # aire entre la franja y la palabra vecina
    rects = []

    def franja(x0, x1, base):  # v3: se juntan y se imprimen todas juntas (materia.franja), no son rectángulos de pantalla
        rects.append([x0 - tam * 0.08, base - tam * 0.80, x1 + tam * 0.08, base + tam * 0.16])

    def en_franja(t, idx):
        """Una parte va en la franja si es acento, o si es puntuación pegada a un acento (¿ ? , .)."""
        txt, a = t[idx]
        if a:
            return True
        vecinos = [t[k][1] for k in (idx - 1, idx + 1) if 0 <= k < len(t)]
        return acento == "banda" and not any(c.isalnum() for c in txt) and any(vecinos)

    def es_acento(t):
        return any(a for _, a in t)

    def sep(prev, cur):
        return esp + (extra if es_acento(prev) != es_acento(cur) else 0)

    if acento == "banda":  # una franja continua por cada tramo de partes con acento
        for k, l in enumerate(lineas):
            base = y + asc + k * alto
            cx, tramo = x, None
            for i, t in enumerate(l):
                if i:
                    if tramo and not es_acento(t):
                        franja(*tramo, base)
                        tramo = None
                    cx += sep(l[i - 1], t) if not tramo else esp
                for idx, (txt, a) in enumerate(t):
                    w = f.getlength(txt)
                    if en_franja(t, idx):
                        tramo = [tramo[0] if tramo else cx, cx + w]
                    elif tramo:
                        franja(*tramo, base)
                        tramo = None
                    cx += w
            if tramo:
                franja(*tramo, base)
        mt.franja(img, rects, ACENTO, sum(map(ord, texto)) % 997)
    for k, l in enumerate(lineas):
        cx, base = x, y + asc + k * alto
        for i, t in enumerate(l):
            if i:
                cx += sep(l[i - 1], t)
            for idx, (txt, a) in enumerate(t):
                if a and acento == "serif":
                    d.text((cx, base), txt, font=fa, fill=ACENTO, anchor="ls")
                    cx += fa.getlength(txt)
                else:
                    col = CARBON if (acento == "banda" and en_franja(t, idx)) else color
                    d.text((cx, base), txt, font=f, fill=col, anchor="ls")
                    cx += f.getlength(txt)
    return y + len(lineas) * alto


def etiqueta(img, x, y, texto, fondo=None, color=CARBON, tam=28, punto=True):
    """Etiqueta en caja (v3, 24 oct 2026). La caja va impresa (materia.franja: canto que se abre, tinta que carga
    desigual) y la letra es la condensada de los titulares en versales con interletra: la mono dentro de una caja
    perfecta se veía de interfaz, "muy Claude". Con punto lleva el aro de Dial en la estación de Al Aire (arriba,
    como el foco de "en el aire" de una cabina de radio)."""
    fondo = fondo or ACENTO
    f = etiqueta_f(tam * 1.1)
    pad = tam * 0.55
    alto = tam * 1.7
    d_aro = tam * 0.92
    tx = x + pad + (d_aro + tam * 0.38 if punto else 0)
    w = ancho_versal(texto, f, 0.05) + (tx - x) + pad
    mt.franja(img, [(x, y, x + w, y + alto)], fondo, (sum(map(ord, texto)) + int(x)) % 997)
    cap = -f.getbbox("H", anchor="ls")[1]
    if punto:
        aro(img, x + pad + d_aro / 2, y + alto / 2, d_aro, color, angulo=ESTACIONES["al-aire"])
    versal(img, tx, y + alto / 2 + cap / 2, texto, f, color, 0.05)
    return x + w


def cabecera(img, fecha, oscuro=True, sobre_foto=True, logo_papel=False, sello=None):
    """Franja superior fija de Al Aire: etiqueta + fecha a la izquierda, logo a la derecha.
    v3: la fecha ya no va en caja; va en versales con una sombra leve y un velo un poco más alto arriba."""
    if oscuro and sobre_foto:
        img.alpha_composite(dn.degradado_superior(W, H, hasta=(T + 200) / H, fuerza=0.6))
        # sombra de esquina bajo el logo, para cielos y fachadas claras
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - (W - M - 85)) / 260) ** 2 + ((yy - (T + 22)) / 110) ** 2)
        g = np.zeros((H, W, 4), np.uint8)
        g[..., :3] = CARBON
        g[..., 3] = (np.clip(1 - r, 0, 1) ** 1.2 * 0.6 * 255).astype(np.uint8)
        img.alpha_composite(Image.fromarray(g, "RGBA"))
    fin = etiqueta(img, M, T, SELLO, fondo=sello, color=BRASA if sello else CARBON)  # sello: caja carbón sobre campo brasa
    fm, lg = dn.sans(21, 620, 100), dn.logo(38)
    alto = 28 * 1.7
    cap = -fm.getbbox("H", anchor="ls")[1]
    x, y = fin + 20, T + alto / 2 + cap / 2
    if x + ancho_versal(fecha, fm, 0.12) > W - M - R - lg.width - 24:  # sello largo: la fecha baja
        x, y = M, T + alto + 36
    versal(img, x, y, fecha, fm, (PAPEL if oscuro else CARBON) + (235,), 0.12, sombra=oscuro and sobre_foto)
    if logo_papel:  # manual: sobre terracota, todo en papel, incluido el punto
        a = np.asarray(lg).copy()
        a[a[..., 3] > 0, :3] = PAPEL
        lg = Image.fromarray(a)
    elif not oscuro:
        a = np.asarray(lg).copy()
        claro = a[..., 0] > 200
        a[claro, :3] = CARBON
        a[~claro & (a[..., 3] > 0), :3] = TERRACOTA
        lg = Image.fromarray(a)
    img.alpha_composite(lg, (W - M - lg.width, T + 2))


def rotulo_persona(img, persona):
    """Rótulo de persona (v2, 19 oct 2026): un punto sobre la persona y una guía que sale hacia el
    lado, a dos cajas planas como las de la cabecera: el nombre (papel) y el cargo (carbón, mono).

    persona: {"nombre", "cargo", "x", "y", "lado"}. x, y (fracciones) = el punto, sobre el hombro o
    el pecho, nunca sobre la cara. lado = "izq" o "der": hacia dónde sale el rótulo (por defecto,
    hacia el lado con más espacio). El rótulo se centra en la altura del punto."""
    d = ImageDraw.Draw(img)
    fn, fc = madera(38), etiqueta_f(20)  # v3: el cargo en versales condensadas, no en mono
    nombre, cargo = persona["nombre"], persona.get("cargo", "").upper()
    px, py = persona.get("x", 0.5) * W, persona.get("y", 0.5) * H
    lado = persona.get("lado") or ("der" if px < W / 2 else "izq")
    guia = 54
    wn, hn = fn.getlength(nombre) + 30, 52
    wc, hc = (ancho_versal(cargo, fc, 0.06) + 24, 32) if cargo else (0, 0)
    ancho = max(wn, wc)
    top = py - (hn + hc) / 2
    if lado == "der":
        x0 = min(px + guia, W - M - ancho)
        borde = x0
    else:
        x0 = max(px - guia - ancho, M)
        borde = x0 + ancho
    # cajas alineadas por el lado de la guía
    xn = x0 if lado == "der" else borde - wn
    xc = x0 if lado == "der" else borde - wc
    d.line([(px, py), (borde, py)], fill=PAPEL, width=3)
    mt.franja(img, [(xn, top, xn + wn, top + hn)], PAPEL, int(px) % 997)
    d.text((xn + 15, top + hn - 13), nombre, font=fn, fill=CARBON, anchor="ls")
    if cargo:
        mt.franja(img, [(xc, top + hn, xc + wc, top + hn + hc)], CARBON, int(py) % 997)
        versal(img, xc + 12, top + hn + hc - 10, cargo, fc, PAPEL, 0.06)
    r = 9
    d.ellipse([px - r - 3, py - r - 3, px + r + 3, py + r + 3], fill=PAPEL)
    d.ellipse([px - r, py - r, px + r, py + r], fill=ACENTO)


def partir(texto_, fuente, ancho):
    """Corta un texto en líneas que caben en `ancho` (nada se sale del cuadro)."""
    lineas, act = [], ""
    for w in (w for w in re.split(r"[ \t\r\n]+", texto_) if w):  # el espacio duro (U+00A0) no parte
        prueba = (act + " " + w).strip()
        if act and fuente.getlength(prueba) > ancho:
            lineas.append(act)
            act = w
        else:
            act = prueba
    if act:
        lineas.append(act)
    return lineas


def texto(img, x, y, contenido, tam, ancho, color, peso=500, inter=1.2):
    r = dn.Rico(contenido, tam, peso, color=color, interlineado=inter)
    r.f = dn.cuerpo(tam, 400 if peso <= 500 else 600)  # v5: la letra para leer es Bricolage
    return r.dibujar(ImageDraw.Draw(img), x, y, r.equilibradas(ancho))


def pie(img, contenido, color):
    """Crédito y fuentes (v3): letra de texto pequeña, en caja normal, como el pie de foto de un diario.
    Antes iba en mono y en mayúsculas, que era lo más "de máquina" de cada lámina."""
    if not dn.PIE:  # v5: los créditos van en la descripción ("pie": true en el JSON los vuelve a poner)
        return
    f = dn.cuerpo(19, 420)
    ancho = W - 2 * M - R
    while f.getlength(contenido) > ancho and f.size > 15:  # créditos largos: la letra baja un punto, no se corta
        f = dn.cuerpo(f.size - 1, 420)
    ImageDraw.Draw(img).text((M, H - B + 58), contenido, font=f, fill=color, anchor="ls")


# ------------------------------------------------------------ láminas (desde el JSON de la noticia)

def foto_base(cfg, lam):
    if lam.get("_video"):  # en video la foto es el propio video: la capa va sobre transparente
        return Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return dn.preparar_foto(cfg["_base"] / lam["foto"], lam.get("ajuste"), FORMATO, lam.get("foco")).convert("RGBA")


def credito(lam):
    c = lam.get("credito", "")
    if lam.get("_video") and c.startswith("Foto:"):
        c = "Video:" + c[5:]
    return c


def degradado_bajo(img, desde=0.42, fuerza=0.92):
    img.alpha_composite(dn.degradado_inferior(W, H, desde=desde, fuerza=fuerza))


def l_portada(cfg, lam):
    img = foto_base(cfg, lam)
    if lam.get("degradado"):  # fotos claras: degradado más alto y más fuerte, [desde, fuerza]
        degradado_bajo(img, *lam["degradado"])
    else:
        degradado_bajo(img, 0.34 if B < 200 else 0.28, 0.96)  # portada: titular grande, fotos cargadas
    cabecera(img, lam.get("meta", cfg["meta"]))
    tam = 108 * lam.get("escala", 1.0)
    baj = lam.get("bajada", "")
    an = W * lam["ancho"] - M if lam.get("ancho") else (W - 2 * M - R)  # columna, para no tapar lo esencial
    if lam.get("ancho") and lam["ancho"] < 0.65:
        x = np.linspace(0, 1, W)[None, :]
        g = np.zeros((H, W, 4), np.uint8)
        g[..., :3] = CARBON
        g[..., 3] = (0.55 * np.clip(1 - x / (lam["ancho"] + 0.2), 0, 1) ** 1.3 * np.ones((H, 1)) * 255).astype(np.uint8)
        img.alpha_composite(Image.fromarray(g, "RGBA"))
    alto = alto_titular(lam["titulo"], tam, an) + (30 + alto_texto(baj, 38, an - 40) if baj else 0)
    y = dibujar_titular(img, M, H - B - alto, lam["titulo"], tam, an)
    if baj:
        texto(img, M, y + 30, baj, 38, an - 40, PAPEL + (235,))
    pie(img, credito(lam), PAPEL + (190,))
    return img


def l_foto(cfg, lam):
    img = foto_base(cfg, lam)
    arriba = lam.get("posicion") == "arriba"
    if arriba:  # el cartel o la persona están abajo: el texto sube bajo la cabecera
        img.alpha_composite(dn.degradado_superior(W, H, hasta=0.55, fuerza=0.88))
    elif lam.get("degradado"):  # fotos claras: degradado más alto y más fuerte, [desde, fuerza]
        degradado_bajo(img, *lam["degradado"])
    else:
        degradado_bajo(img, 0.5 if B < 200 else 0.42, 0.88)
    cabecera(img, lam.get("meta", cfg["meta"]))
    ancho = W * lam["ancho"] - M if lam.get("ancho") else (W - 2 * M - R)
    tx, tt = lam.get("texto", ""), lam.get("titulo", "")
    alto = (alto_titular(tt, 84, ancho) + 18 if tt else 0) + alto_texto(tx, 42, ancho)
    y = H - B - alto if not arriba else T + 190
    if lam.get("rotulo"):
        etiqueta(img, M, y - 78, lam["rotulo"].upper(), fondo=PAPEL, punto=False, tam=26)
    if tt:
        y = dibujar_titular(img, M, y, tt, 84, ancho) + 18
    texto(img, M, y, tx, 42, ancho, PAPEL + (240,))
    personas = lam.get("persona") or []
    for p in ([personas] if isinstance(personas, dict) else personas):
        rotulo_persona(img, p)
    pie(img, credito(lam), PAPEL + (190,))
    return img


def palabra_madera(img, palabra, y_base, semilla, color=PAPEL, sombra=CARBON):
    tam = 360
    while madera(tam).getlength(palabra) > (W - 2 * M - R) + 20 and tam > 120:
        tam -= 10
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).text((M - tam * 0.04, y_base), palabra, font=madera(tam), fill=255, anchor="ls")
    # segunda pasada de otra tinta, con su propia textura y un registro apenas corrido (no es una sombra)
    estampar(img, m, sombra, semilla + 7, desfase=(7, 6), opacidad=0.85, debajo_de=m)
    estampar(img, m, color, semilla + 1)


def l_pais(cfg, lam, n):
    """Campo brasa (v5; antes terracota) con el país o el lugar en tipo de madera, en carbón."""
    img = campo(CAMPO, 10 + n)
    cabecera(img, lam.get("meta", cfg["meta"]), oscuro=False, sobre_foto=False, sello=CARBON)
    # el contenido se dibuja en su capa; si no cabe, todo el bloque (y el título) sube
    final = img
    img = Image.new("RGBA", (W, H * 2), (0, 0, 0, 0))
    y = T + 598
    if lam.get("rotulo"):
        etiqueta(img, M, y, lam["rotulo"].upper(), fondo=CARBON, color=PAPEL, punto=False, tam=26)
        y += 90
    if lam.get("texto"):
        y = texto(img, M, y, lam["texto"], 46, (W - 2 * M - R), CARBON) + 20
    d = ImageDraw.Draw(img)
    for i, it in enumerate(lam.get("items", []), 1):
        fi = dn.sans(48, 600, 88)
        d.text((M, y + 50), str(i), font=madera(54), fill=PAPEL, anchor="ls")  # v3: cifra de titular, sin el "01" de máquina
        for k, linea in enumerate(partir(it, fi, W - 2 * M - R - 70)):
            d.text((M + 70, y + 50 + k * 54), linea, font=fi, fill=CARBON, anchor="ls")
        y += 72 + 54 * (len(partir(it, fi, W - 2 * M - R - 70)) - 1)
    for c in lam.get("citas", []):
        y += 30
        d.text((M - 6, y + 96), "“", font=dn.serif(150), fill=CARBON, anchor="ls")
        r = dn.Rico(c["texto"], 52, 400, color=CARBON, interlineado=1.12)
        r.f = dn.serif(56)
        y = r.dibujar(d, M + 70, y + 10, r.lineas((W - 2 * M - R) - 70))
        versal(img, M + 70, y + 40, c["autor"].upper(), etiqueta_f(23), CARBON, 0.06)
        y += 50
    sube = max(0, y - (H - B - 30))
    sube = min(sube, 330)  # el título no puede subir más allá de la cabecera
    palabra_madera(final, lam["titulo"].upper(), T + 538 - sube, 3 + n, color=CARBON, sombra=SOMBRA)
    final.alpha_composite(img.crop((0, sube, W, sube + H)))
    if y - sube > H - B - 10:
        print(f"  ojo: la lámina {n} se pasa de alto; acorta el texto o los items")
    pie(final, lam.get("credito", ""), CARBON + (215,))
    return final


def l_citas(cfg, lam, n):
    """Papel limpio: las voces de las partes. Comillas grandes en terracota, texto sin textura."""
    img = campo(PAPEL, 20 + n, 0.03)
    cabecera(img, lam.get("rotulo", "").upper() or lam.get("meta", cfg["meta"]), oscuro=False, sobre_foto=False)
    d = ImageDraw.Draw(img)
    bloques = []
    for c in lam["citas"]:
        r = dn.Rico(c["texto"], 56, 600, color=CARBON, interlineado=1.1)
        r.f = dn.sans(56, 600, 88)
        bloques.append((r, r.lineas((W - 2 * M - R) - 100), c["autor"]))
    fa_ = etiqueta_f(23)  # v3: el autor en versales condensadas con interletra, no en mono
    ancho_a = W - 2 * M - R - 100 - 40
    total = sum(r.alto(l) + 80 + 30 * (len(partir(a_.upper(), fa_, ancho_a)) - 1) for r, l, a_ in bloques) + 70 * (len(bloques) - 1)
    y = T + 118 + (H - T - 118 - B - 20 - total) / 2
    for k, (r, l, autor) in enumerate(bloques):
        d.text((M - 8, y + 128), "“", font=dn.serif(200), fill=COMILLAS, anchor="ls")
        y = r.dibujar(d, M + 100, y + 10, l)
        lineas_a = partir(autor.upper(), fa_, ancho_a)
        for j, linea in enumerate(lineas_a):
            versal(img, M + 100, y + 40 + j * 30, linea, fa_, (95, 85, 76), 0.06)
        y += 30 * (len(lineas_a) - 1)
        y += 80
        if k < len(bloques) - 1:
            d.line([(M + 100, y), (W - M, y)], fill=(204, 194, 180), width=2)
            y += 70
    pie(img, lam.get("credito", ""), (95, 85, 76))
    return img


def l_analisis(cfg, lam, n):
    """Carbón + collage en semitono brasa con borde rasgado + análisis."""
    img = campo(FONDO, 30 + n, 0.06)
    alto_foto = round(H * lam.get("alto_semitono", 0.444))
    if lam.get("semitono"):
        foto = Image.open(cfg["_base"] / lam["semitono"]).convert("RGB")
        foco = tuple(lam.get("foco_semitono", (0.5, 0.45)))
        st = np.asarray(semitono(foto, (W, alto_foto), 7, ACENTO, FONDO, foco=foco, contraste=1.5, luz=True), np.float32)[..., :3]
        # v3: el borde es un papel rasgado a mano, con la franja de fibra clara que deja el desgarro y su sombra
        arriba, fibra = mt.rasgado(W, alto_foto, alto_foto - 44, 77 + n, amplitud=16)
        base = np.asarray(img, np.float32)[:alto_foto, :, :3]
        sombra = mt._blur(np.roll(arriba + fibra, 5, axis=0), 5) * 0.45
        base = base * (1 - sombra[..., None])
        out = base * (1 - arriba[..., None]) + st * arriba[..., None]
        out = out * (1 - fibra[..., None]) + np.array(HUESO, np.float32)[None, None, :] * fibra[..., None]
        img.paste(mt.imagen(out), (0, 0))
        img.alpha_composite(dn.degradado_superior(W, H, hasta=0.12, fuerza=0.6))
    cabecera(img, lam.get("rotulo", "").upper() or lam.get("meta", cfg["meta"]))
    y0 = alto_foto + 30 if lam.get("semitono") else T + 260  # sin foto, el análisis sube
    y = dibujar_titular(img, M, y0, lam["titulo"], 140 * lam.get("escala", 1.0), (W - 2 * M - R)) + 34
    d = ImageDraw.Draw(img)
    for i, it in enumerate(lam.get("items", []), 1):
        fi = dn.sans(46, 600, 88)
        partes = partir(it, fi, W - 2 * M - R - 70)
        d.text((M, y + 46), str(i), font=madera(52), fill=ACENTO, anchor="ls")
        for k, linea in enumerate(partes):
            d.text((M + 70, y + 46 + k * 52), linea, font=fi, fill=PAPEL, anchor="ls")
        y += 66 + 52 * (len(partes) - 1)
    if lam.get("cierre"):
        y += 22
        h = alto_texto(lam["cierre"], 42, (W - 2 * M - R) - 30)
        mt.franja(img, [(M, y + 4, M + 6, y + h - 8)], ACENTO, 5 + n)
        texto(img, M + 26, y, lam["cierre"], 42, (W - 2 * M - R) - 30, PAPEL + (235,))
    pie(img, lam.get("credito", ""), PAPEL + (170,))
    return img


def l_cta(cfg, lam, n):
    """Cierre (v2, 19 oct 2026): la pregunta para comentar y la invitación a seguir a Dial Medio.

    Campos: pregunta (con *acento*, abierta y sin tomar partido), texto (opcional, una frase que
    la aterriza), cuenta (por defecto @dialmedio). Siempre es la última lámina del carrusel."""
    img = campo(FONDO, 40 + n, 0.06)
    cabecera(img, (lam.get("rotulo") or "Conversemos").upper(), sobre_foto=False)
    d = ImageDraw.Draw(img)
    ancho = W - 2 * M - R
    # signo grande en tipo de madera, en terracota: la misma tinta de las láminas de país
    m = Image.new("L", (W, H), 0)
    fq = madera(560)
    ImageDraw.Draw(m).text((W - M - R + 30, T + 520), "?", font=fq, fill=255, anchor="rs")
    estampar(img, m, TINTA, 60 + n)
    pregunta = lam["pregunta"]
    tam = 104 * lam.get("escala", 1.0)
    texto_ = lam.get("texto", "")
    alto = alto_titular(pregunta, tam, ancho) + (28 + alto_texto(texto_, 40, ancho) if texto_ else 0)
    y_pie = H - B - 150
    y = max(T + 300, y_pie - 70 - alto)
    etiqueta(img, M, y - 82, "TU OPINIÓN", fondo=PAPEL, punto=False, tam=26)
    y = dibujar_titular(img, M, y, pregunta, tam, ancho)
    if texto_:
        texto(img, M, y + 28, texto_, 40, ancho, PAPEL + (225,))
    # acciones (v3): una línea en versales, sin cajas; la primera, que es la que más importa, en la tinta de la línea
    fa_ = etiqueta_f(27)
    x = M
    for k, palabra in enumerate(["COMENTA", "GUARDA", "COMPARTE"]):
        if k:
            x = versal(img, x + 14, y_pie + 34, "·", fa_, PAPEL + (150,), 0) + 14
        x = versal(img, x, y_pie + 34, palabra, fa_, ACENTO if k == 0 else PAPEL, 0.08)
    # firma: el logotipo grande, el lema de Dial Medio y la cuenta
    lg = dn.logo(64)
    img.alpha_composite(lg, (M, round(y_pie + 84)))
    d = ImageDraw.Draw(img)
    cuenta = lam.get("cuenta", "@dialmedio")
    d.text((W - M - R, y_pie + 84 + 46), cuenta, font=dn.sans(30, 560, 96), fill=PAPEL, anchor="rs")
    d.text((M + lg.width + 24, y_pie + 84 + 46), "Sintonizar es conversar.", font=dn.serif(34), fill=BRASA, anchor="ls")
    return img


def estilo_de(lam):
    if lam.get("estilo"):
        return lam["estilo"]
    if lam.get("tipo") == "portada":
        return "portada"
    if lam.get("tipo") == "cta" or lam.get("pregunta"):
        return "cta"
    if lam.get("tipo") == "texto":
        if lam.get("semitono"):
            return "analisis"
        return "citas" if lam.get("citas") and not lam.get("titulo") else "pais"
    return "foto"


def pegar_recorte(img, cfg, rc, n):
    """Recorte tipo collage (23 oct 2026): una foto pegada con borde de papel, el canto de abajo
    rasgado, un giro leve y sombra, que se sale de su franja. Campos: foto, x, y, ancho, alto,
    foco, giro, pie (texto en caja bajo la foto)."""
    foto = Image.open(cfg["_base"] / rc["foto"]).convert("RGB")
    w = rc.get("ancho", 300)
    h = rc.get("alto", round(w * 1.25))
    fx, fy = rc.get("foco", (0.5, 0.4))
    s = max(w / foto.width, h / foto.height)
    fw, fh = round(foto.width * s), round(foto.height * s)
    foto = foto.resize((fw, fh), Image.LANCZOS)
    cx = int(min(max(fx * fw - w / 2, 0), fw - w))
    cy = int(min(max(fy * fh - h / 2, 0), fh - h))
    foto = foto.crop((cx, cy, cx + w, cy + h))
    b = rc.get("borde", 14)
    papel = Image.new("RGBA", (w + 2 * b, h + 2 * b + 18), PAPEL + (255,))
    papel.paste(foto, (b, b))
    # v3: el canto de abajo es un rasgado de verdad (materia.rasgado), con la fibra más blanca que el papel
    arriba, fibra = mt.rasgado(papel.width, papel.height, papel.height - 16, 90 + n, amplitud=5)
    rgb = np.asarray(papel, np.float32)[..., :3]
    rgb = rgb * (1 - fibra[..., None]) + np.array((250, 247, 240), np.float32)[None, None, :] * fibra[..., None]
    papel = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(arriba + fibra, 0, 1) * 255]).astype(np.uint8), "RGBA")
    rot = papel.rotate(rc.get("giro", -4), expand=True, resample=Image.BICUBIC)
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sombra = Image.new("RGBA", rot.size, (20, 14, 10, 255))
    sombra.putalpha(rot.split()[3].filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.6)))
    x, y = rc["x"], rc["y"]
    capa.alpha_composite(sombra, (x + 12, y + 18))
    capa.alpha_composite(rot, (x, y))
    img.alpha_composite(capa)
    if rc.get("pie"):
        etiqueta(img, x + 26, y + rot.height - 46, rc["pie"].upper(), fondo=ACENTO, color=CARBON, punto=False, tam=24)


ESTILOS = {"portada": l_portada, "foto": l_foto, "pais": l_pais, "citas": l_citas, "analisis": l_analisis, "cta": l_cta}


def lamina(cfg, lam, n):
    """Una lámina de foto o de texto, en el formato de la noticia (4:5 por defecto)."""
    seccion(cfg)
    dn.PELICULA = cfg.get("pelicula", True) is not False  # reglas comunes v5, para todas las líneas
    dn.PIE = bool(cfg.get("pie"))
    formato = cfg.get("formato") or "4:5"
    a, b = (float(x) for x in formato.split(":"))
    lienzo(1080, round(1080 * b / a), formato)
    if cfg.get("seccion") == "nuevos-mundos":
        import nuevos_mundos
        return nuevos_mundos.lamina(cfg, lam, n).convert("RGB")
    if cfg.get("seccion") == "arte":
        import arte
        return arte.lamina(cfg, lam, n).convert("RGB")
    if cfg.get("seccion") == "tecnologia":
        import tecnologia
        return tecnologia.lamina(cfg, lam, n).convert("RGB")
    if cfg.get("seccion") == "mundos":
        import mundos
        return mundos.lamina(cfg, lam, n).convert("RGB")
    estilo = estilo_de(lam)
    fn = ESTILOS[estilo]
    im = fn(cfg, lam) if estilo in ("portada", "foto") else fn(cfg, lam, n)
    recortes = lam.get("recorte") or []
    if estilo == "portada" and recortes:  # Martín, 24 oct 2026: la portada es una sola foto, sin collage
        print("aviso: la portada no lleva recortes; se omiten (van en las láminas de adentro)")
        recortes = []
    for k, rc in enumerate([recortes] if isinstance(recortes, dict) else recortes):  # uno o varios (p. ej. los dos candidatos)
        pegar_recorte(im, cfg, rc, n + 3 * k)
    return im.convert("RGB")


def capa_video(cfg, lam, w, h):
    """Diseño de la lámina sobre transparente, para ponerlo encima del video."""
    seccion(cfg)
    lienzo(w, h)
    if cfg.get("seccion") == "nuevos-mundos":
        import nuevos_mundos
        return nuevos_mundos.capa_video(cfg, lam)
    if cfg.get("seccion") == "arte":
        import arte
        return arte.capa_video(cfg, lam)
    lam = dict(lam, _video=True)
    return (l_portada if estilo_de(lam) == "portada" else l_foto)(cfg, lam)
