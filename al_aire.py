"""Estilo visual de Al Aire (v2, aprobado por Martín el 18 oct 2026).

Referentes: Mutante (campos planos, titulares condensados, collage en semitono,
etiquetas en caja) y La Linterna (tipos de madera, tinta con textura de prensa,
registro imperfecto). Todo dentro de la paleta Dial; la brasa pasa a ser el color
de Al Aire (el manual ya la reserva para los estados "en vivo").
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dial_noticias as dn  # noqa: E402

CARBON, PAPEL, HUESO = dn.CARBON, dn.PAPEL, (233, 223, 207)
TERRACOTA, BRASA = dn.TERRACOTA, (229, 138, 58)
W, H = 1080, 1350
M = 72
T, B, R = 62, 110, 0   # cabecera, margen inferior y margen derecho extra (zona segura en 9:16)
FORMATO = "4:5"
SELLO = "AL AIRE"


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


def tinta(mascara, semilla, fuerza=1.0):
    """Máscara (L) -> alfa con aspecto de tipo de madera: bordes mordidos y tinta desigual."""
    m = np.asarray(mascara.filter(ImageFilter.GaussianBlur(1.6)), np.float32) / 255
    n_borde = ruido_fractal(mascara.width, mascara.height, semilla, (3, 10), (0.6, 0.4))
    borde = np.clip((m - 0.5 + (n_borde - 0.5) * 0.55 * fuerza) * 5 + 0.5, 0, 1)
    carga = ruido_fractal(mascara.width, mascara.height, semilla + 1, (5, 30, 140), (0.35, 0.35, 0.3))
    poros = ruido_fractal(mascara.width, mascara.height, semilla + 2, (2, 4), (0.6, 0.4))
    a = borde * (0.80 + 0.20 * np.clip((carga - 0.25) / 0.5, 0, 1))
    a *= np.where(poros > 0.80, 0.55, 1.0) if fuerza > 0.5 else 1.0
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def campo(color, semilla, manchas=0.035):
    """Papel o tinta plana con moteado de impresión (no es grano de cámara)."""
    n = ruido_fractal(W, H, semilla, (40, 160, 500), (0.4, 0.35, 0.25))
    a = np.array(color, np.float32)[None, None, :] * (1 + (n[..., None] - 0.5) * manchas * 2)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def estampar(base, mascara, color, semilla, desfase=(0, 0), multiplicar=False, fuerza=1.0):
    alfa = tinta(mascara, semilla, fuerza)
    capa = Image.new("RGBA", base.size, color + (0,))
    capa.putalpha(alfa)
    if desfase != (0, 0):
        capa = ImageChops.offset(capa, *desfase)
    if multiplicar:
        rgb = Image.composite(Image.new("RGB", base.size, color), Image.new("RGB", base.size, (255, 255, 255)), capa.getchannel("A"))
        out = ImageChops.multiply(base.convert("RGB"), rgb).convert("RGBA")
        base.paste(out)
    else:
        base.alpha_composite(capa)


def semitono(foto, tam, celda, tinta_color, fondo_color, angulo=22, contraste=1.25, foco=(0.5, 0.5), luz=False):
    """Foto en semitono de una tinta (como la riso de Mutante)."""
    g = dn.recortar(foto.convert("L"), f"{tam[0]}:{tam[1]}", foco).resize(tam, Image.LANCZOS)
    a = np.asarray(g, np.float32) / 255
    a = np.clip((a - 0.5) * contraste + 0.5, 0, 1)
    if luz:  # la tinta marca las luces: tinta clara sobre fondo oscuro, sin negativo
        a = 1 - a
    g = Image.fromarray((a * 255).astype(np.uint8))
    s = 2
    grande = g.resize((tam[0] * s, tam[1] * s)).rotate(angulo, expand=True, fillcolor=255)
    gw, gh = grande.size
    c = celda * s
    pequ = np.asarray(grande.resize((gw // c + 1, gh // c + 1), Image.BOX), np.float32) / 255
    puntos = Image.new("L", (gw, gh), 0)
    d = ImageDraw.Draw(puntos)
    for j in range(pequ.shape[0]):
        for i in range(pequ.shape[1]):
            r = c * 0.72 * np.sqrt(1 - pequ[j, i])
            if r > 0.6:
                cx, cy = i * c + c / 2, j * c + c / 2
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    puntos = puntos.rotate(-angulo, fillcolor=0)
    l0, t0 = (gw - tam[0] * s) // 2, (gh - tam[1] * s) // 2
    puntos = puntos.crop((l0, t0, l0 + tam[0] * s, t0 + tam[1] * s)).resize(tam, Image.LANCZOS)
    out = Image.new("RGBA", tam, fondo_color + (255,))
    capa = Image.new("RGBA", tam, tinta_color + (0,))
    capa.putalpha(puntos)
    out.alpha_composite(capa)
    return out


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
    """acento: "banda" (palabras sobre franja brasa, en carbón) o "serif" (cursiva brasa)."""
    f, fa, lineas, alto, wt, esp = titular(texto, tam, ancho, interlineado, acento)
    d = ImageDraw.Draw(img)
    asc = f.getmetrics()[0]
    for l in lineas:
        cx = x
        base = y + asc
        if acento == "banda":  # una franja continua por cada tramo de palabras con acento
            bx = x
            tramo = None
            for i, t in enumerate(l):
                if i:
                    bx += esp
                w = wt(t)
                if t[0][1]:
                    tramo = [tramo[0] if tramo else bx, bx + w]
                elif tramo:
                    d.rectangle([tramo[0] - tam * 0.08, base - tam * 0.80, tramo[1] + tam * 0.08, base + tam * 0.16], fill=BRASA)
                    tramo = None
                bx += w
            if tramo:
                d.rectangle([tramo[0] - tam * 0.08, base - tam * 0.80, tramo[1] + tam * 0.08, base + tam * 0.16], fill=BRASA)
        for i, t in enumerate(l):
            if i:
                cx += esp
            es_ac = t[0][1]
            for txt, a in t:
                if a and acento == "serif":
                    d.text((cx, base), txt, font=fa, fill=BRASA, anchor="ls")
                    cx += fa.getlength(txt)
                else:
                    col = CARBON if (a and acento == "banda") else color
                    d.text((cx, base), txt, font=f, fill=col, anchor="ls")
                    cx += f.getlength(txt)
        y += alto
    return y


def etiqueta(img, x, y, texto, fondo=BRASA, color=CARBON, tam=28, punto=True):
    """Caja de rótulo en mono (como pide el manual) con el punto "en vivo"."""
    f = dn.mono(tam, medio=True)
    d = ImageDraw.Draw(img)
    pad = tam * 0.55
    tx = x + pad + (tam * 0.75 if punto else 0)
    w = f.getlength(texto) + (tx - x) + pad
    d.rectangle([x, y, x + w, y + tam * 1.7], fill=fondo)
    if punto:
        r = tam * 0.22
        cy = y + tam * 0.85
        d.ellipse([x + pad, cy - r, x + pad + 2 * r, cy + r], fill=color)
    d.text((tx, y + tam * 1.2), texto, font=f, fill=color, anchor="ls")
    return x + w


def cabecera(img, fecha, oscuro=True, sobre_foto=True, logo_papel=False):
    """Franja superior fija de Al Aire: etiqueta + fecha a la izquierda, logo a la derecha."""
    if oscuro and sobre_foto:
        img.alpha_composite(dn.degradado_superior(W, H, hasta=(T + 140) / H, fuerza=0.45))
        # sombra de esquina bajo el logo, para cielos y fachadas claras
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - (W - M - 85)) / 260) ** 2 + ((yy - (T + 22)) / 110) ** 2)
        g = np.zeros((H, W, 4), np.uint8)
        g[..., :3] = CARBON
        g[..., 3] = (np.clip(1 - r, 0, 1) ** 1.2 * 0.6 * 255).astype(np.uint8)
        img.alpha_composite(Image.fromarray(g, "RGBA"))
    fin = etiqueta(img, M, T, SELLO)
    d = ImageDraw.Draw(img)
    if oscuro and sobre_foto:  # sobre cielos claros la fecha se perdía: va en caja carbón
        fm = dn.mono(24)
        d.rectangle([fin, T, fin + fm.getlength(fecha) + 36, T + 28 * 1.7], fill=CARBON)
    d.text((fin + 18, T + 28 * 1.2), fecha, font=dn.mono(24), fill=(PAPEL if oscuro else CARBON) + (220,), anchor="ls")
    lg = dn.logo(38)
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


def texto(img, x, y, contenido, tam, ancho, color, peso=500, inter=1.2):
    r = dn.Rico(contenido, tam, peso, color=color, interlineado=inter)
    r.f = dn.sans(tam, peso, 96)
    return r.dibujar(ImageDraw.Draw(img), x, y, r.equilibradas(ancho))


def pie(img, contenido, color):
    ImageDraw.Draw(img).text((M, H - B + 58), contenido, font=dn.mono(20), fill=color, anchor="ls")


# ------------------------------------------------------------ láminas (desde el JSON de la noticia)

def foto_base(cfg, lam):
    if lam.get("_video"):  # en video la foto es el propio video: la capa va sobre transparente
        return Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return dn.preparar_foto(cfg["_base"] / lam["foto"], lam.get("ajuste"), FORMATO, lam.get("foco")).convert("RGBA")


def credito(lam):
    c = lam.get("credito", "")
    if lam.get("_video") and c.startswith("Foto:"):
        c = "Video:" + c[5:]
    return c.upper()


def degradado_bajo(img, desde=0.42, fuerza=0.92):
    img.alpha_composite(dn.degradado_inferior(W, H, desde=desde, fuerza=fuerza))


def l_portada(cfg, lam):
    img = foto_base(cfg, lam)
    degradado_bajo(img, 0.38 if B < 200 else 0.3)
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
        dn.rotulo_persona(ImageDraw.Draw(img), W, H, 1.0, p)
    pie(img, credito(lam), PAPEL + (190,))
    return img


def palabra_madera(img, palabra, y_base, semilla, color=PAPEL, sombra=CARBON):
    tam = 360
    while madera(tam).getlength(palabra) > (W - 2 * M - R) + 20 and tam > 120:
        tam -= 10
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).text((M - tam * 0.04, y_base), palabra, font=madera(tam), fill=255, anchor="ls")
    estampar(img, m, sombra, semilla, desfase=(9, 7))  # la segunda pasada, corrida
    estampar(img, m, color, semilla + 1)


def l_pais(cfg, lam, n):
    """Campo terracota con el país en tipo de madera (para países sin foto libre)."""
    img = campo(TERRACOTA, 10 + n)
    cabecera(img, lam.get("meta", cfg["meta"]), sobre_foto=False, logo_papel=True)
    palabra_madera(img, lam["titulo"].upper(), T + 538, 3 + n)
    y = T + 598
    if lam.get("rotulo"):
        etiqueta(img, M, y, lam["rotulo"].upper(), fondo=CARBON, color=PAPEL, punto=False, tam=26)
        y += 90
    if lam.get("texto"):
        y = texto(img, M, y, lam["texto"], 46, (W - 2 * M - R), PAPEL) + 20
    d = ImageDraw.Draw(img)
    for i, it in enumerate(lam.get("items", []), 1):
        d.text((M, y + 50), f"{i:02d}", font=dn.mono(30, True), fill=CARBON, anchor="ls")
        d.text((M + 70, y + 50), it, font=dn.sans(48, 600, 88), fill=PAPEL, anchor="ls")
        y += 72
    for c in lam.get("citas", []):
        y += 30
        d.text((M - 6, y + 96), "“", font=dn.serif(150), fill=CARBON, anchor="ls")
        r = dn.Rico(c["texto"], 52, 400, color=CARBON, interlineado=1.12)
        r.f = dn.serif(56)
        y = r.dibujar(d, M + 70, y + 10, r.lineas((W - 2 * M - R) - 70))
        d.text((M + 70, y + 40), c["autor"].upper(), font=dn.mono(22, True), fill=CARBON, anchor="ls")
        y += 50
    pie(img, lam.get("credito", "").upper(), PAPEL + (215,))
    return img


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
    total = sum(r.alto(l) + 80 for r, l, _ in bloques) + 70 * (len(bloques) - 1)
    y = T + 118 + (H - T - 118 - B - 20 - total) / 2
    for k, (r, l, autor) in enumerate(bloques):
        d.text((M - 8, y + 128), "“", font=dn.serif(200), fill=TERRACOTA, anchor="ls")
        y = r.dibujar(d, M + 100, y + 10, l)
        d.text((M + 100, y + 40), autor.upper(), font=dn.mono(22, True), fill=(95, 85, 76), anchor="ls")
        y += 80
        if k < len(bloques) - 1:
            d.line([(M + 100, y), (W - M, y)], fill=(204, 194, 180), width=2)
            y += 70
    pie(img, lam.get("credito", "").upper(), (95, 85, 76))
    return img


def l_analisis(cfg, lam, n):
    """Carbón + collage en semitono brasa con borde rasgado + análisis."""
    img = campo(CARBON, 30 + n, 0.06)
    alto_foto = round(H * 0.444)
    if lam.get("semitono"):
        foto = Image.open(cfg["_base"] / lam["semitono"]).convert("RGB")
        st = semitono(foto, (W, alto_foto), 7, BRASA, CARBON, foco=tuple(lam.get("foco_semitono", (0.5, 0.45))),
                      contraste=1.5, luz=True)
        ras = ruido_fractal(W, 1, 77 + n, (8, 40), (0.6, 0.4))[0]
        mk = Image.new("L", (W, alto_foto), 255)
        dm = ImageDraw.Draw(mk)
        for x in range(W):
            dm.line([(x, alto_foto - 30 - ras[x] * 46), (x, alto_foto)], fill=0)
        img.paste(st, (0, 0), mk)
        img.alpha_composite(dn.degradado_superior(W, H, hasta=0.12, fuerza=0.6))
    cabecera(img, lam.get("rotulo", "").upper() or lam.get("meta", cfg["meta"]))
    y = dibujar_titular(img, M, alto_foto + 30, lam["titulo"], 140 * lam.get("escala", 1.0), (W - 2 * M - R)) + 34
    d = ImageDraw.Draw(img)
    for i, it in enumerate(lam.get("items", []), 1):
        d.text((M, y + 46), f"{i:02d}", font=dn.mono(30, True), fill=BRASA, anchor="ls")
        d.text((M + 70, y + 46), it, font=dn.sans(46, 600, 88), fill=PAPEL, anchor="ls")
        y += 66
    if lam.get("cierre"):
        y += 22
        h = alto_texto(lam["cierre"], 42, (W - 2 * M - R) - 30)
        d.rectangle([M, y + 4, M + 6, y + h - 8], fill=BRASA)
        texto(img, M + 26, y, lam["cierre"], 42, (W - 2 * M - R) - 30, PAPEL + (235,))
    pie(img, lam.get("credito", "").upper(), PAPEL + (170,))
    return img


def estilo_de(lam):
    if lam.get("estilo"):
        return lam["estilo"]
    if lam.get("tipo") == "portada":
        return "portada"
    if lam.get("tipo") == "texto":
        if lam.get("semitono"):
            return "analisis"
        return "citas" if lam.get("citas") and not lam.get("titulo") else "pais"
    return "foto"


ESTILOS = {"portada": l_portada, "foto": l_foto, "pais": l_pais, "citas": l_citas, "analisis": l_analisis}


def lamina(cfg, lam, n):
    """Una lámina de foto o de texto, en el formato de la noticia (4:5 por defecto)."""
    global SELLO
    SELLO = cfg.get("sello", "Al aire").upper()
    formato = cfg.get("formato") or "4:5"
    a, b = (float(x) for x in formato.split(":"))
    lienzo(1080, round(1080 * b / a), formato)
    estilo = estilo_de(lam)
    fn = ESTILOS[estilo]
    im = fn(cfg, lam) if estilo in ("portada", "foto") else fn(cfg, lam, n)
    return im.convert("RGB")


def capa_video(cfg, lam, w, h):
    """Diseño de la lámina sobre transparente, para ponerlo encima del video."""
    global SELLO
    SELLO = cfg.get("sello", "Al aire").upper()
    lienzo(w, h)
    lam = dict(lam, _video=True)
    return (l_portada if estilo_de(lam) == "portada" else l_foto)(cfg, lam)
