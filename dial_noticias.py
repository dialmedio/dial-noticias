"""Generador de piezas de noticias de Dial Medio.

Uso:
    python dial_noticias.py noticias/<noticia>.json [--solo=1,3]

Cada lámina respeta la proporción de su foto o video. Lado corto = 1080 px.
Si "foto" es un video (.mp4, .mov...), sale el video completo con la misma
colorización (como LUT) y el mismo diseño encima, con su audio.
Sin grano: Martín prefiere la imagen limpia (el grano se veía como baja calidad).
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAIZ = Path(__file__).resolve().parent
FUENTES = RAIZ / "fuentes"

CARBON = (23, 19, 15)
PAPEL = (244, 238, 229)
TERRACOTA = (192, 68, 42)
TERRACOTA_CLARA = (224, 105, 74)  # la terracota normal se pierde sobre oscuro

LADO_CORTO = 1080


# ---------------------------------------------------------------- colorización

def _desenfoque(x, r):
    """Desenfoque tipo gaussiano: tres pasadas de caja con sumas acumuladas."""
    r = max(1, int(r))
    for eje in (0, 1):
        for _ in range(3):
            p = np.pad(x, [(r + 1, r) if e == eje else (0, 0) for e in range(x.ndim)], mode="edge")
            c = np.cumsum(p, axis=eje)
            sl_hi = [slice(None)] * x.ndim
            sl_lo = [slice(None)] * x.ndim
            sl_hi[eje] = slice(2 * r + 1, None)
            sl_lo[eje] = slice(0, -(2 * r + 1))
            x = (c[tuple(sl_hi)] - c[tuple(sl_lo)]) / (2 * r + 1)
    return x


def _lum(a):
    return a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722


AJUSTE_BASE = {"exposicion": 0.0, "calidez": 0.0, "contraste": 1.0, "saturacion": 1.0, "balance": 0.55}


def estimar(a, aj):
    """Parámetros automáticos de la corrección (balance, niveles, exposición)."""
    p = {"g": np.ones(3, np.float32)}
    L = _lum(a)
    # 1. Balance de blancos parcial (mundo gris sobre medios tonos poco saturados)
    sat = a.max(-1) - a.min(-1)
    m = (L > 0.12) & (L < 0.85) & (sat < 0.35)
    if m.sum() > 1000:
        medias = a[m].mean(0)
        g = medias.mean() / np.maximum(medias, 1e-4)
        p["g"] = np.clip(1 + (g - 1) * aj["balance"], 0.9, 1.1)
    a = a * p["g"]
    # 2. Niveles: punto negro y blanco por luminancia (sin estirar de más las noches)
    L = _lum(a)
    p["lo"] = min(float(np.percentile(L, 0.5)), 0.07)
    p["hi"] = max(float(np.percentile(L, 99.6)), 0.72)
    a = np.clip((a - p["lo"]) / (p["hi"] - p["lo"]), 0, 1.2)
    # 3. Exposición: lleva la mediana hacia 0.40 (con límites)
    med = float(np.median(np.clip(_lum(a), 1e-4, None)))
    p["gamma"] = float(np.clip(np.log(0.40) / np.log(max(med, 1e-3)), 0.72, 1.3)) * 2 ** (-aj["exposicion"])
    return p


def aplicar(a, p, aj, claridad=True):
    """Corrección + look base. Sin claridad es puntual (sirve para LUT de video)."""
    a = a * p["g"]
    a = np.clip((a - p["lo"]) / (p["hi"] - p["lo"]), 0, 1.2)
    L = np.clip(_lum(a), 1e-4, None)
    Ln = np.clip(L, 0, 1) ** p["gamma"]

    # 4. Curva en S suave con pie profundo (negros densos, luces que no se queman)
    s = Ln * Ln * (3 - 2 * Ln)
    Ln = Ln + 0.36 * aj["contraste"] * (s - Ln)
    hombro = 0.92
    Ln = np.where(Ln > hombro, hombro + (1 - hombro) * np.tanh((Ln - hombro) / (1 - hombro)), Ln)

    # 5. Claridad: contraste local en medios tonos
    if claridad:
        base = _desenfoque(Ln, Ln.shape[1] * 0.012)
        Ln = Ln + 0.2 * (Ln - base) * (4 * Ln * (1 - Ln))

    # aplica la nueva luminancia conservando el color
    a = a * (np.clip(Ln, 0, 1.2) / L)[..., None]

    # 6. Saturación natural (sube poco y protege lo ya saturado)
    L = _lum(a)[..., None]
    satc = a.max(-1, keepdims=True) - a.min(-1, keepdims=True)
    factor = (1.10 - 0.18 * np.clip(satc, 0, 1)) * aj["saturacion"]
    a = L + (a - L) * factor

    # 7. Virado muy leve: luces cálidas, sombras neutras-frías
    L = np.clip(_lum(a), 0, 1)[..., None]
    calor = 0.018 + 0.02 * aj["calidez"]
    a = a + np.concatenate([calor * L ** 2, 0.004 * L ** 2, -calor * L ** 2], -1)
    a = a + np.concatenate([-0.004 * (1 - L) ** 3, 0 * L, 0.006 * (1 - L) ** 3], -1)

    # 8. Negros de impresión (apenas levantados)
    return np.clip(0.012 + np.clip(a, 0, 1) * 0.982, 0, 1)


def colorizar(img, ajuste=None):
    """Corrección automática + look base (contraste editorial, color natural).

    ajuste (opcional, por lámina): {"exposicion": 0.0, "calidez": 0.0,
    "contraste": 1.0, "saturacion": 1.0, "balance": 0.55}
    """
    aj = dict(AJUSTE_BASE, **(ajuste or {}))
    a = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    a = aplicar(a, estimar(a, aj), aj)
    out = Image.fromarray((a * 255 + 0.5).astype(np.uint8))
    return out.filter(ImageFilter.UnsharpMask(radius=1.3, percent=55, threshold=2))


# ---------------------------------------------------------------- tipografía

def fuente(nombre, tam, wdth=None, wght=None):
    f = ImageFont.truetype(str(FUENTES / nombre), int(round(tam)))
    if wdth is not None:
        f.set_variation_by_axes([wdth, wght])
    return f


def sans(tam, peso=600, ancho=88):
    return fuente("InstrumentSans-VF.ttf", tam, ancho, peso)


def serif(tam):
    return fuente("InstrumentSerif-Italic.ttf", tam)


def mono(tam, medio=False):
    return fuente("IBMPlexMono-Medium.ttf" if medio else "IBMPlexMono-Regular.ttf", tam)


def _tokens(texto):
    """'Con *danza y carteles*, cientos' -> [(palabra, acento)]"""
    out, previo = [], " "
    for i, trozo in enumerate(re.split(r"\*", texto)):
        for j, w in enumerate(trozo.split()):
            pegado = j == 0 and out and not trozo[:1].isspace() and not previo[-1:].isspace()
            if pegado:  # puntuación pegada a un acento: "*carteles*," -> sin espacio
                out[-1] = out[-1] + [(w, i % 2 == 1)]
            else:
                out.append([(w, i % 2 == 1)])
        previo = trozo or previo
    return out


class Rico:
    """Texto con acentos en serif cursiva terracota (*así*)."""

    def __init__(self, texto, tam, peso=600, color=PAPEL, acento=TERRACOTA_CLARA, interlineado=1.02):
        self.tok = _tokens(texto)
        self.f = sans(tam, peso)
        self.fa = serif(tam * 1.16)
        self.color, self.acento = color, acento
        self.tam = tam
        self.alto_linea = tam * interlineado

    def _w(self, tok, ac=None):
        return sum((self.fa if a else self.f).getlength(t) for t, a in tok)

    def _esp(self, ac):
        return (self.fa if ac else self.f).getlength(" ")

    def lineas(self, ancho):
        lin, act, x = [], [], 0
        for tok in self.tok:
            w, ac = tok, tok[0][1]
            ww = self._w(tok)
            sep = self._esp(ac) if act else 0
            if act and x + sep + ww > ancho:
                lin.append(act)
                act, x = [], 0
                sep = 0
            act.append(tok)
            x += sep + ww
        if act:
            lin.append(act)
        return lin

    def ancho_linea(self, l):
        return sum(self._w(t) for t in l) + sum(self._esp(t[0][1]) for t in l[1:])

    def equilibradas(self, ancho):
        """Mismo número de líneas, pero lo más parejas posible."""
        n = len(self.lineas(ancho))
        lo, hi = ancho * 0.4, ancho
        for _ in range(18):
            mid = (lo + hi) / 2
            if len(self.lineas(mid)) > n:
                lo = mid
            else:
                hi = mid
        return self.lineas(hi)

    def alto(self, lin):
        return self.alto_linea * len(lin)

    def dibujar(self, d, x, y, lin):
        """y = tope del bloque. Devuelve el y final."""
        asc = self.f.getmetrics()[0]
        for l in lin:
            cx = x
            base = y + asc
            for i, tok in enumerate(l):
                if i:
                    cx += self._esp(tok[0][1])
                for w, ac in tok:
                    f = self.fa if ac else self.f
                    d.text((cx, base), w, font=f, fill=self.acento if ac else self.color, anchor="ls")
                    cx += f.getlength(w)
            y += self.alto_linea
        return y


# ---------------------------------------------------------------- capas

def degradado_inferior(W, H, desde=0.42, fuerza=0.88):
    y = np.linspace(0, 1, H)[:, None]
    t = np.clip((y - desde) / (1 - desde), 0, 1)
    alfa = fuerza * (t ** 1.6)
    # un poco más denso hacia la izquierda, donde va el texto
    x = np.linspace(0, 1, W)[None, :]
    alfa = alfa * (1.0 - 0.22 * x)
    capa = np.zeros((H, W, 4), np.uint8)
    capa[..., :3] = CARBON
    capa[..., 3] = (np.clip(alfa, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(capa, "RGBA")


def degradado_superior(W, H, hasta=0.2, fuerza=0.4):
    y = np.linspace(0, 1, H)[:, None]
    t = np.clip(1 - y / hasta, 0, 1)
    alfa = np.repeat(fuerza * t ** 1.8, W, axis=1)
    capa = np.zeros((H, W, 4), np.uint8)
    capa[..., :3] = CARBON
    capa[..., 3] = (alfa * 255).astype(np.uint8)
    return Image.fromarray(capa, "RGBA")


def textura(img, semilla, grano=0.0, vineta=0.16):
    """Viñeta suave. El grano está en 0: Martín lo vio como baja calidad (18 oct 2026)."""
    a = np.asarray(img, dtype=np.float32) / 255.0
    H, W = a.shape[:2]
    if grano:
        rng = np.random.default_rng(semilla)
        ruido = rng.normal(0, 1, (H, W)).astype(np.float32)
        ruido = 0.6 * ruido + 0.4 * _desenfoque(ruido, 1) * 2.2
        L = _lum(a)[..., None]
        a = a + grano * ruido[..., None] * (0.35 + 0.65 * 4 * L * (1 - L))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / np.sqrt(2)
    a = a * (1 - vineta * np.clip(r - 0.35, 0, 1) ** 1.5 / 0.65 ** 1.5)[..., None]
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


def logo(alto):
    im = Image.open(RAIZ / "marca" / "dial-medio-letras-claro.png").convert("RGBA")
    im = im.crop(im.getbbox())
    # sobre foto, la terracota pasa a terracota clara (la normal se pierde)
    a = np.asarray(im).astype(np.float32)
    calido = (a[..., 0] - a[..., 2]) > 60
    a[calido, :3] = TERRACOTA_CLARA
    im = Image.fromarray(a.astype(np.uint8), "RGBA")
    return im.resize((round(im.width * alto / im.height), round(alto)), Image.LANCZOS)


def sello(d, x, y, texto, tam, meta=None):
    """Nodo terracota con halo + texto. y = línea base del texto."""
    f = sans(tam, 600)
    r = tam * 0.3
    cy = y - tam * 0.34
    cx = x + r
    for k, al in ((2.3, 40), (1.65, 80)):
        d.ellipse([cx - r * k, cy - r * k, cx + r * k, cy + r * k], outline=TERRACOTA_CLARA + (al,), width=max(2, round(tam * 0.05)))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=TERRACOTA_CLARA)
    tx = x + r * 2 + tam * 0.55
    d.text((tx, y), texto, font=f, fill=PAPEL, anchor="ls")
    if meta:
        fm = mono(tam * 0.56)
        mx = tx + f.getlength(texto) + tam * 0.7
        d.text((mx, y), meta, font=fm, fill=PAPEL + (190,), anchor="ls")


# ---------------------------------------------------------------- láminas

def recortar(im, formato, foco=(0.5, 0.5)):
    """formato "4:5", "9:16", "1:1"...; foco = punto (x, y) en fracciones que debe quedar dentro."""
    a, b = (float(x) for x in formato.split(":"))
    W, H = im.size
    obj = a / b
    if W / H > obj:
        nw, nh = round(H * obj), H
    else:
        nw, nh = W, round(W / obj)
    x0 = min(max(foco[0] * W - nw / 2, 0), W - nw)
    y0 = min(max(foco[1] * H - nh / 2, 0), H - nh)
    return im.crop((round(x0), round(y0), round(x0) + nw, round(y0) + nh))


def preparar_foto(ruta, ajuste, formato=None, foco=None):
    im = Image.open(ruta)
    im = im.convert("RGB")
    if formato:
        im = recortar(im, formato, foco or (0.5, 0.5))
    W, H = im.size
    esc = LADO_CORTO / min(W, H)
    tam = (round(W * esc), round(H * esc))
    if formato:  # medidas exactas (p. ej. 1080 × 1920), sin errores de redondeo
        a, b = (float(x) for x in formato.split(":"))
        tam = (LADO_CORTO, round(LADO_CORTO * b / a)) if a <= b else (round(LADO_CORTO * a / b), LADO_CORTO)
    im = im.resize(tam, Image.LANCZOS)
    return colorizar(im, ajuste)


def rotulo_persona(d, W, H, t, persona):
    """Rótulo de nombre y cargo con piquito hacia la persona (x, y en fracciones)."""
    fn, fc = sans(30 * t, 650, 92), sans(24 * t, 450, 92)
    nombre, cargo = persona["nombre"], persona.get("cargo", "")
    pad = 22 * t
    w = max(fn.getlength(nombre), fc.getlength(cargo) if cargo else 0) + 2 * pad
    h = pad * 0.8 + 30 * t + (8 * t + 24 * t if cargo else 0) + pad * 0.8
    cx, top = persona.get("x", 0.5) * W, persona.get("y", 0.6) * H
    x0 = min(max(cx - w / 2, 24 * t), W - w - 24 * t)
    pico = 14 * t
    d.polygon([(cx - pico, top), (cx + pico, top), (cx, top - pico)], fill=PAPEL)
    d.rectangle([x0, top, x0 + w, top + h], fill=PAPEL)
    d.text((x0 + w / 2, top + pad * 0.8 + 30 * t * 0.8), nombre, font=fn, fill=CARBON, anchor="ms")
    if cargo:
        d.text((x0 + w / 2, top + pad * 0.8 + 30 * t + 8 * t + 24 * t * 0.8), cargo, font=fc,
               fill=CARBON + (200,), anchor="ms")


def graficos(cfg, lam, W, H, video=False):
    """Devuelve (fondo, frente): degradados que van bajo el grano, y textos + logo + sombras."""
    u = min(W, H) / 1080  # unidad: 1 px a 1080 de lado corto
    horizontal = W > H
    alto_vertical = H / W >= 1.6  # 9:16: Instagram y TikTok tapan abajo y a la derecha
    # en horizontal la foto se ve más pequeña en el celular: letra 22 % más grande
    t = u * (1.22 if horizontal else 1.0)
    margen = 72 * u
    ancho_txt = (W * 0.72) if horizontal else (W - 2 * margen - (110 * u if alto_vertical else 0))
    if lam.get("ancho"):  # fracción del ancho, para no tapar lo importante de la foto
        ancho_txt = W * lam["ancho"] - margen
    tipo = lam.get("tipo", "foto")
    y_fin = H - (330 * u if alto_vertical else margen * 1.15)
    y_logo = margen * (1.9 if alto_vertical else 0.85)

    fondo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    arriba = lam.get("posicion") == "arriba"  # texto arriba cuando abajo hay algo que no se debe tapar
    if arriba:
        fondo.alpha_composite(degradado_superior(W, H, hasta=0.6, fuerza=0.88))
        fondo.alpha_composite(degradado_inferior(W, H, desde=0.8, fuerza=0.45))
    else:
        fondo.alpha_composite(degradado_superior(W, H, hasta=0.26 if alto_vertical else 0.2))
        desde = 0.36 if tipo == "portada" else 0.5
        if alto_vertical:
            desde = 0.3 if tipo == "portada" else 0.42
        fondo.alpha_composite(degradado_inferior(W, H, desde=desde, fuerza=0.9 if tipo == "portada" else 0.84))

    if lam.get("ancho") and lam["ancho"] < 0.65:
        # texto en columna: sombra lateral para que se lea sobre fondos claros
        x = np.linspace(0, 1, W)[None, :]
        yv = np.linspace(0, 1, H)[:, None]
        lado = np.clip(1 - x / (lam["ancho"] + 0.18), 0, 1) ** 1.3
        vert = np.clip((1 - yv / 0.3) if arriba else (yv - 0.25) / 0.3, 0, 1)
        g = np.zeros((H, W, 4), np.uint8)
        g[..., :3] = CARBON
        g[..., 3] = (0.62 * lado * vert * 255).astype(np.uint8)
        fondo.alpha_composite(Image.fromarray(g, "RGBA"))

    frente = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if video:  # en video la viñeta va en la capa (en foto la pone textura())
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / np.sqrt(2)
        v = np.zeros((H, W, 4), np.uint8)
        v[..., 3] = (0.16 * np.clip(r - 0.35, 0, 1) ** 1.5 / 0.65 ** 1.5 * 255).astype(np.uint8)
        frente.alpha_composite(Image.fromarray(v, "RGBA"))

    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)

    # logo arriba a la derecha, con una sombra de esquina para fondos claros
    lg = logo(40 * t)
    cx, cy = W - margen - lg.width / 2, y_logo + lg.height / 2
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - cx) / (lg.width * 1.1)) ** 2 + ((yy - cy) / (lg.height * 2.6)) ** 2)
    esquina = np.zeros((H, W, 4), np.uint8)
    esquina[..., :3] = CARBON
    esquina[..., 3] = (np.clip(1 - r, 0, 1) ** 1.2 * 0.6 * 255).astype(np.uint8)
    frente.alpha_composite(Image.fromarray(esquina, "RGBA"))
    capa.alpha_composite(lg, (round(W - margen - lg.width), round(y_logo)))

    # crédito abajo a la derecha (en 9:16, debajo del texto y a la izquierda, fuera de la zona de botones)
    fc = sans(19 * t, 500, 92)
    credito = lam.get("credito", cfg.get("credito", ""))
    if video and credito.startswith("Foto:"):
        credito = "Video:" + credito[5:]
    if credito:
        if alto_vertical:
            d.text((margen, y_fin + 46 * u), credito, font=fc, fill=PAPEL + (200,), anchor="ls")
        else:
            d.text((W - margen, H - margen * 0.62), credito, font=fc, fill=PAPEL + (200,), anchor="rs")

    if tipo == "portada":
        esc_t = lam.get("escala", 1.0)  # titular más pequeño cuando va en una columna angosta
        tt = Rico(lam["titulo"], (92 if horizontal else 84) * t * esc_t, 600)
        lt = tt.equilibradas(ancho_txt)
        bj = Rico(lam.get("bajada", ""), (44 if horizontal else 40) * t, 450, color=PAPEL + (235,),
                  interlineado=1.22) if lam.get("bajada") else None
        lb = bj.equilibradas(ancho_txt * 0.92) if bj else []
        alto_total = tt.alto(lt) + (bj.alto(lb) + 22 * t if bj else 0)
        y = y_fin - alto_total
        if arriba:
            y = y_logo + lg.height + 110 * t
        y_sello = y - 34 * t
        sello(d, margen, y_sello, cfg.get("sello", ""), 36 * t, cfg.get("meta"))
        y = tt.dibujar(d, margen - 3 * t, y + 6 * t, lt)
        if bj:
            # filete terracota a la izquierda de la bajada
            y += 22 * t
            d.rectangle([margen, y + 6 * t, margen + 5 * t, y + bj.alto(lb) - 10 * t], fill=TERRACOTA_CLARA)
            bj.dibujar(d, margen + 24 * t, y, lb)
    elif lam.get("texto"):
        tx = Rico(lam["texto"], (52 if horizontal else 48) * t, 500, interlineado=1.16)
        lt = tx.equilibradas(ancho_txt)
        y = y_fin - tx.alto(lt)
        if arriba:
            y = y_logo + lg.height + (100 if lam.get("rotulo") else 50) * t
        if lam.get("rotulo"):
            fr = sans(30 * t, 650, 96)
            yr = y - 24 * t
            d.ellipse([margen, yr - 22 * t, margen + 15 * t, yr - 7 * t], fill=TERRACOTA_CLARA)
            d.text((margen + 28 * t, yr), lam["rotulo"].upper(), font=fr, fill=PAPEL, anchor="ls")
            y += 14 * t
        tx.dibujar(d, margen - 2 * t, y, lt)

    personas = lam.get("persona") or []
    for persona in ([personas] if isinstance(personas, dict) else personas):
        rotulo_persona(d, W, H, t, persona)

    # sombra suave bajo todo lo gráfico, para que se lea sobre cualquier fondo
    al = capa.getchannel("A").filter(ImageFilter.GaussianBlur(14 * u))
    sombra = Image.new("RGBA", (W, H), CARBON + (0,))
    sombra.putalpha(al.point(lambda v: int(v * 0.55)))
    frente.alpha_composite(sombra)
    frente.alpha_composite(capa)
    return fondo, frente


def lamina(cfg, lam, n):
    foto = preparar_foto(cfg["_base"] / lam["foto"], lam.get("ajuste"),
                         lam.get("formato", cfg.get("formato")), lam.get("foco"))
    W, H = foto.size
    fondo, frente = graficos(cfg, lam, W, H)
    base = foto.convert("RGBA")
    base.alpha_composite(fondo)
    img = textura(base.convert("RGB"), semilla=cfg.get("semilla", 7) * 100 + n).convert("RGBA")
    img.alpha_composite(frente)
    return img.convert("RGB")


def lamina_texto(cfg, lam, n):
    """Lámina sin foto (carbón con luz tungsteno): para datos, citas o análisis.

    Campos: rotulo, titulo (admite *acento*), dato + dato_pie, texto, items [..], citas [{texto, autor}], cierre.
    """
    formato = cfg.get("formato") or "4:5"
    a, b = (float(x) for x in formato.split(":"))
    W, H = (LADO_CORTO, round(LADO_CORTO * b / a)) if a <= b else (round(LADO_CORTO * a / b), LADO_CORTO)
    u = min(W, H) / 1080
    margen = 72 * u
    ancho = W - 2 * margen

    # fondo carbón con un resplandor cálido arriba a la izquierda (la .luz de la marca)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W * 0.2) / (W * 0.95)) ** 2 + ((yy - H * 0.12) / (H * 0.75)) ** 2)
    luz = np.clip(1 - r, 0, 1) ** 2
    base = np.array(CARBON, np.float32)[None, None, :] + luz[..., None] * np.array([34, 20, 8], np.float32)
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")
    lg = logo(40 * u)
    img.alpha_composite(lg, (round(W - margen - lg.width), round(margen * 0.85)))

    # el contenido se dibuja en una capa aparte y luego se centra en el alto disponible
    capa = Image.new("RGBA", (W, H * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    y0 = 40 * u
    y = y0
    if lam.get("rotulo"):
        fr = sans(30 * u, 650, 96)
        d.ellipse([margen, y - 22 * u, margen + 15 * u, y - 7 * u], fill=TERRACOTA_CLARA)
        d.text((margen + 28 * u, y), lam["rotulo"].upper(), font=fr, fill=PAPEL, anchor="ls")
        y += 40 * u
    if lam.get("titulo"):
        tt = Rico(lam["titulo"], 150 * u * lam.get("escala", 1.0), 600)
        lt = tt.equilibradas(ancho)
        y = tt.dibujar(d, margen - 4 * u, y, lt) + 30 * u
    if lam.get("dato"):
        fd = sans(170 * u, 600, 88)
        d.text((margen - 4 * u, y + 130 * u), lam["dato"], font=fd, fill=TERRACOTA_CLARA, anchor="ls")
        y += 160 * u
        if lam.get("dato_pie"):
            pie = Rico(lam["dato_pie"], 34 * u, 450, color=PAPEL + (220,), interlineado=1.22)
            y = pie.dibujar(d, margen, y, pie.lineas(ancho * 0.85)) + 30 * u
    if lam.get("texto"):
        tx = Rico(lam["texto"], 54 * u, 500, color=PAPEL + (240,), interlineado=1.2)
        y = tx.dibujar(d, margen - 2 * u, y, tx.equilibradas(ancho)) + 34 * u
    for item in lam.get("items", []):
        it = Rico(item, 50 * u, 600, interlineado=1.12)
        li = it.lineas(ancho - 50 * u)
        cy = y + 50 * u * 0.45
        d.ellipse([margen, cy - 9 * u, margen + 18 * u, cy + 9 * u], fill=TERRACOTA_CLARA)
        y = it.dibujar(d, margen + 50 * u, y, li) + 24 * u
    for cita in lam.get("citas", []):
        fq = serif(120 * u)
        y += 16 * u
        d.text((margen - 6 * u, y + 112 * u), "\u201c", font=fq, fill=TERRACOTA_CLARA, anchor="ls")
        ct = Rico(cita["texto"], 50 * u, 500, interlineado=1.16)
        y = ct.dibujar(d, margen + 62 * u, y + 8 * u, ct.lineas(ancho - 62 * u)) + 8 * u
        if cita.get("autor"):
            fa = sans(30 * u, 450, 92)
            d.text((margen + 62 * u, y + 30 * u), cita["autor"], font=fa, fill=PAPEL + (170,), anchor="ls")
            y += 46 * u
        y += 44 * u
    if lam.get("cierre"):  # remate con filete terracota, como la bajada de la portada
        y += 10 * u
        ci = Rico(lam["cierre"], 46 * u, 500, color=PAPEL + (235,), interlineado=1.22)
        lc = ci.equilibradas(ancho - 24 * u)
        d.rectangle([margen, y + 6 * u, margen + 5 * u, y + ci.alto(lc) - 10 * u], fill=TERRACOTA_CLARA)
        y = ci.dibujar(d, margen + 24 * u, y, lc) + 20 * u

    # centra el bloque entre el logo y el crédito (sin subir más allá del logo)
    tope, fondo_y = margen * 0.85 + lg.height + 60 * u, H - margen * 1.3
    usado = y - y0
    dy = max(tope, tope + (fondo_y - tope - usado) / 2) - y0
    img.alpha_composite(capa, (0, round(dy)))
    d = ImageDraw.Draw(img)
    y = y + dy

    credito = lam.get("credito", "")
    if credito:
        fc = sans(21 * u, 500, 92)
        d.text((margen, H - margen * 0.75), credito, font=fc, fill=PAPEL + (170,), anchor="ls")
    if y > H - margen * 1.1:
        print(f"  ojo: la lámina {n} se pasa de alto ({round(y)} > {round(H - margen * 1.2)}); recorta el texto")
    return img.convert("RGB")


# ---------------------------------------------------------------- video

VIDEOS = {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi", ".3gp"}


def ffmpeg():
    """ffmpeg del sistema o, si no hay, el que trae imageio-ffmpeg (se instala solo)."""
    import shutil
    import subprocess
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "imageio-ffmpeg"], check=True)
        import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def _duracion(ff, ruta):
    import subprocess
    err = subprocess.run([ff, "-hide_banner", "-i", str(ruta)], capture_output=True, text=True,
                         encoding="utf-8", errors="replace").stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else 0.0


def _fotograma(ff, ruta, seg):
    import io
    import subprocess
    out = subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-ss", f"{seg:.2f}", "-i", str(ruta),
                          "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                         capture_output=True).stdout
    return Image.open(io.BytesIO(out)).convert("RGB")


def _lut(ruta, p, aj, n=33):
    """Escribe un .cube con la corrección (sin claridad, que no es puntual)."""
    v = np.linspace(0, 1, n, dtype=np.float32)
    b, g, r = np.meshgrid(v, v, v, indexing="ij")  # en .cube el rojo varía más rápido
    red = np.stack([r, g, b], -1).reshape(n * n, n, 3)
    out = aplicar(red, p, aj, claridad=False).reshape(-1, 3)
    with open(ruta, "w", encoding="ascii") as f:
        f.write(f"TITLE \"Dial Medio\"\nLUT_3D_SIZE {n}\n")
        f.writelines(f"{x:.6f} {y:.6f} {z:.6f}\n" for x, y, z in out)


def video(cfg, lam, n, ruta_salida):
    """Video completo, con la colorización y el diseño encima. Conserva el audio."""
    import subprocess
    import tempfile
    ff = ffmpeg()
    ruta = (cfg["_base"] / lam["foto"]).resolve()
    dur = _duracion(ff, ruta)
    tiempos = [dur * k for k in (0.1, 0.3, 0.5, 0.7, 0.9)] if dur > 1 else [0]
    muestras = [_fotograma(ff, ruta, s) for s in tiempos]
    W0, H0 = muestras[0].size
    filtros = []
    formato = lam.get("formato", cfg.get("formato"))
    if formato:
        foco = lam.get("foco") or (0.5, 0.5)
        muestras = [recortar(m, formato, foco) for m in muestras]
        x0, y0 = _caja(W0, H0, formato, foco)
        W0, H0 = muestras[0].size
        filtros.append(f"crop={W0}:{H0}:{x0}:{y0}")
    esc = LADO_CORTO / min(W0, H0)
    W, H = round(W0 * esc / 2) * 2, round(H0 * esc / 2) * 2

    # la corrección se mide sobre varios fotogramas a la vez, para que no cambie en el video
    chicas = [np.asarray(m.resize((480, round(480 * H0 / W0)))) for m in muestras]
    mosaico = np.concatenate(chicas, 0).astype(np.float32) / 255.0
    aj = dict(AJUSTE_BASE, **(lam.get("ajuste") or {}))
    p = estimar(mosaico, aj)

    fondo, frente = graficos(cfg, lam, W, H, video=True)
    fondo.alpha_composite(frente)
    with tempfile.TemporaryDirectory() as tmp:
        _lut(Path(tmp) / "look.cube", p, aj)
        fondo.save(Path(tmp) / "capa.png")
        filtros += [f"scale={W}:{H}:flags=lanczos", "format=gbrp", "lut3d=file=look.cube",
                    "unsharp=5:5:0.35"]
        grafo = f"[0:v]{','.join(filtros)}[v];[v][1:v]overlay=0:0:format=auto,format=yuv420p[sal]"
        cmd = [ff, "-hide_banner", "-loglevel", "error", "-y", "-i", str(ruta),
               "-loop", "1", "-i", "capa.png", "-filter_complex", grafo, "-map", "[sal]", "-map", "0:a?",
               "-shortest", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "9M",
               "-bufsize", "18M", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(Path(ruta_salida).resolve())]
        subprocess.run(cmd, check=True, cwd=tmp)
    return W, H


def _caja(W, H, formato, foco):
    """Esquina superior izquierda del recorte que haría recortar()."""
    a, b = (float(x) for x in formato.split(":"))
    obj = a / b
    nw, nh = (round(H * obj), H) if W / H > obj else (W, round(W / obj))
    x0 = min(max(foco[0] * W - nw / 2, 0), W - nw)
    y0 = min(max(foco[1] * H - nh / 2, 0), H - nh)
    return round(x0), round(y0)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    solo = None
    for a in sys.argv[1:]:
        if a.startswith("--solo="):
            solo = {int(x) for x in a[7:].split(",")}
    ruta_json = Path(args[0]).resolve()
    cfg = json.loads(ruta_json.read_text(encoding="utf-8"))
    cfg["_base"] = ruta_json.parent  # fotos y salida pueden ser relativas al JSON
    salida = cfg["_base"] / cfg.get("salida", "salida")
    salida.mkdir(parents=True, exist_ok=True)
    hechas = []
    # formato por defecto: 4:5 para todo; un video solo va en 9:16; "original" conserva la proporción
    if "formato" not in cfg:
        solo_video = len(cfg["laminas"]) == 1 and Path(cfg["laminas"][0].get("foto", "")).suffix.lower() in VIDEOS
        cfg["formato"] = "9:16" if solo_video else "4:5"
    if cfg["formato"] in (None, "original"):
        cfg["formato"] = None
    for n, lam in enumerate(cfg["laminas"], 1):
        if solo and n not in solo:
            continue
        nombre = f"{cfg.get('prefijo', 'lamina')}-{n:02d}"
        if lam.get("tipo") == "texto":
            im = lamina_texto(cfg, lam, n)
            ruta = salida / f"{nombre}.jpg"
            im.save(ruta, quality=94, subsampling=0, optimize=True)
            tam = im.size
        elif Path(lam["foto"]).suffix.lower() in VIDEOS:
            ruta = salida / f"{nombre}.mp4"
            tam = video(cfg, lam, n, ruta)
        else:
            im = lamina(cfg, lam, n)
            ruta = salida / f"{nombre}.jpg"
            im.save(ruta, quality=94, subsampling=0, optimize=True)
            tam = im.size
        hechas.append(ruta)
        print(ruta, tam)
    if not solo:  # un zip con todo el carrusel, cómodo para bajar al celular
        import zipfile
        zz = salida / f"{cfg.get('prefijo', 'lamina')}.zip"
        with zipfile.ZipFile(zz, "w") as z:
            for r in hechas:
                z.write(r, r.name)
        print(zz)


if __name__ == "__main__":
    main()
