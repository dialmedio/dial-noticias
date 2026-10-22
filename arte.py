"""Estilo visual de Arte y memoria (nombre provisional, 22 oct 2026), la línea de arte e historia de Al Aire.

Martín pidió un diseño "más inspirado para mostrar fotografía", al nivel de Al Aire y Nuevos Mundos, con un tinte
más oscuro y "aesthetic", nada robótico, digital ni predecible. La idea: el cuarto oscuro y el álbum de fotos.

- Fondo de cuarto oscuro (casi negro, cálido, con fibra de papel) y fotos protagonistas, a sangre y reveladas
  con un tono más hondo (menos saturación, sombras cálidas, viñeta de copia).
- La obra se respeta: en la lámina `obra` va completa, sin recorte ni colorización, impresa con su borde de
  papel y sujeta con esquineros de álbum; debajo, la cartela de museo (título en cursiva, autor, año, técnica).
- `copias`: dos o tres fotos como copias sueltas sobre la mesa, un poco giradas, con su sombra.
- Titulares en Instrument Serif; el acento (*así*) en cursiva ámbar, sin franja: sobre el negro se lee solo.
- Antetítulos y cartelas en sans espaciada; la mono solo en créditos.
- Misma estructura de Al Aire: cabecera, logo, crédito abajo y lámina final de pregunta.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dial_noticias as dn  # noqa: E402
import al_aire as aa  # noqa: E402
import nuevos_mundos as nm  # noqa: E402  (tipografía serif y versalitas espaciadas)

NOMBRE = "Arte y memoria"          # provisional: lo decide Martín
NOCHE = (19, 16, 13)               # el fondo: cuarto oscuro, cálido
NOCHE_ALTA = (31, 26, 22)          # papel negro de álbum (esquineros) y campos un poco más claros
COPIA = (239, 230, 216)            # papel de copia fotográfica: bordes y texto
AMBAR = (232, 180, 138)            # el acento: la luz de seguridad del cuarto oscuro, cálida y legible sobre negro
TERRACOTA = dn.TERRACOTA_CLARA     # la terracota de Dial que se ve sobre oscuro
GRIS = (160, 147, 132)             # texto secundario y créditos

serif, cursiva, espaciado = nm.serif, nm.cursiva, nm.espaciado


def g(nombre):  # medidas vivas de al_aire (cambian con el formato)
    return getattr(aa, nombre)


# ------------------------------------------------------------ texto

def rico(contenido, tam, color=COPIA, inter=1.0):
    r = dn.Rico(contenido, tam, color=color, acento=AMBAR, interlineado=inter)
    r.f, r.fa = serif(tam), cursiva(tam)
    return r


def alto_titular(contenido, tam, ancho, inter=1.0):
    r = rico(contenido, tam, inter=inter)
    return r.alto(r.equilibradas(ancho))


def titular(img, x, y, contenido, tam, ancho, color=COPIA, inter=1.0):
    """Titular en serif; el acento en cursiva ámbar, sin franja."""
    r = rico(contenido, tam, color, inter)
    return r.dibujar(ImageDraw.Draw(img), x, y, r.equilibradas(ancho))


def antetitulo(img, x, y, texto, color=COPIA, sombra=False):
    """Antetítulo: un esquinero pequeño en terracota y el texto en sans espaciada. y = línea base."""
    esquinero_marca(img, x, y - 17, 15, TERRACOTA)
    espaciado(ImageDraw.Draw(img), x + 26, y, texto.upper(), dn.sans(21, 650, 100), color, sombra=sombra)


def esquinero_marca(img, x, y, lado, color):
    """El símbolo de la línea: un esquinero de álbum (triángulo rectángulo) visto de frente."""
    ImageDraw.Draw(img).polygon([(x, y), (x + lado, y), (x, y + lado)], fill=color)


def cabecera(img, meta, sobre_foto=True):
    """Cabecera de álbum: esquinero terracota y el nombre en serif cursiva, el logo a la derecha y, debajo,
    el lugar y la época de la historia en versalitas (no la fecha de hoy)."""
    W, M, T, R = g("W"), g("M"), g("T"), g("R")
    if sobre_foto:
        img.alpha_composite(velo_superior(W, g("H"), (T + 200) / g("H"), 0.78))
    d = ImageDraw.Draw(img)
    esquinero_marca(img, M, T + 6, 26, TERRACOTA)
    d.text((M + 40, T + 32), NOMBRE, font=cursiva(42), fill=COPIA, anchor="ls")
    lg = dn.logo(36)
    img.alpha_composite(lg, (W - M - R - lg.width, T + 2))
    espaciado(d, M + 40, T + 72, meta.upper(), dn.sans(18, 600, 100), COPIA + (200,), sombra=sobre_foto)


def pie(img, contenido, color=GRIS + (230,)):
    aa.pie(img, contenido.upper(), color)


# ------------------------------------------------------------ fondo y fotos

def fondo(semilla, color=NOCHE):
    """Negro cálido con la fibra y el moteado de un papel de álbum (muy leve)."""
    return aa.campo(color, semilla, 0.09)


def velo(W, H, desde, fuerza, color=NOCHE):
    """Degradado hacia el negro de la línea, más largo y más hondo que el de Al Aire."""
    y = np.linspace(0, 1, H)[:, None]
    t = np.clip((y - desde) / (1 - desde), 0, 1)
    alfa = np.repeat(fuerza * t ** 1.35, W, axis=1)
    capa = np.zeros((H, W, 4), np.uint8)
    capa[..., :3] = color
    capa[..., 3] = (np.clip(alfa, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(capa, "RGBA")


def velo_superior(W, H, hasta, fuerza, color=NOCHE):
    y = np.linspace(0, 1, H)[:, None]
    alfa = np.repeat(fuerza * np.clip(1 - y / hasta, 0, 1) ** 1.6, W, axis=1)
    capa = np.zeros((H, W, 4), np.uint8)
    capa[..., :3] = color
    capa[..., 3] = (alfa * 255).astype(np.uint8)
    return Image.fromarray(capa, "RGBA")


def revelar(img, fuerza=1.0):
    """El tono de la línea para las fotos a sangre (no para las obras): un poco menos de color, sombras
    hondas y cálidas, altas luces de papel y una viñeta de copia ampliada. Sin grano."""
    a = np.asarray(img.convert("RGB"), np.float32) / 255
    L = (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2])[..., None]
    a = L + (a - L) * (1 - 0.2 * fuerza)                                  # menos saturación
    a = np.clip((a - 0.5) * (1 + 0.08 * fuerza) + 0.5 - 0.03 * fuerza, 0, 1)  # más hondo
    sombra = np.clip(1 - L / 0.45, 0, 1) ** 1.5 * 0.12 * fuerza          # las sombras tiran a sepia oscuro
    a = a * (1 - sombra) + np.array(NOCHE, np.float32) / 255 * sombra
    H, W = a.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / np.sqrt(2)
    a = a * (1 - 0.32 * fuerza * np.clip(r - 0.3, 0, 1) ** 1.4 / 0.7 ** 1.4)[..., None]
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")


def foto_base(cfg, lam):
    if lam.get("_video"):
        return Image.new("RGBA", (g("W"), g("H")), (0, 0, 0, 0))
    return revelar(aa.foto_base(cfg, lam), lam.get("revelado", 1.0))


def copia(ruta, caja, borde=None, giro=0.0, esquineros=False, original=True, ajuste=None):
    """Una foto u obra como copia impresa: entera (sin recorte), escalada para caber en `caja` (ancho, alto),
    con borde de papel, sombra suave y, si se pide, esquineros de álbum. original=True no toca el color
    (las obras se respetan). Devuelve una imagen RGBA con la sombra incluida."""
    im = Image.open(ruta).convert("RGB")
    if not original:
        im = dn.colorizar(im, ajuste)
    an, al = caja
    b = round(min(an, al) * 0.028) if borde is None else borde
    esc = min((an - 2 * b) / im.width, (al - 2 * b) / im.height)
    im = im.resize((max(1, round(im.width * esc)), max(1, round(im.height * esc))), Image.LANCZOS)
    w, h = im.width + 2 * b, im.height + 2 * b
    pad = 60
    lienzo = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    sombra = Image.new("L", lienzo.size, 0)
    ImageDraw.Draw(sombra).rectangle([pad + 6, pad + 14, pad + w + 6, pad + h + 14], fill=200)
    sombra = sombra.filter(ImageFilter.GaussianBlur(18))
    capa = Image.new("RGBA", lienzo.size, (0, 0, 0, 0))
    capa.putalpha(sombra)
    lienzo.alpha_composite(capa)
    hoja = Image.new("RGBA", (w, h), COPIA + (255,))
    hoja.paste(im, (b, b))
    lienzo.alpha_composite(hoja, (pad, pad))
    if esquineros:
        poner_esquineros(lienzo, pad, pad, pad + w, pad + h, max(34, round(min(w, h) * 0.07)))
    if giro:
        lienzo = lienzo.rotate(giro, resample=Image.BICUBIC, expand=True)
    return lienzo


def poner_esquineros(img, x0, y0, x1, y1, lado):
    """Esquineros de álbum en papel negro sobre las cuatro puntas de la copia, con un filo de luz en el corte."""
    d = ImageDraw.Draw(img)
    s = 6
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        tri = [(cx - sx * s, cy - sy * s), (cx + sx * lado, cy - sy * s), (cx - sx * s, cy + sy * lado)]
        d.polygon(tri, fill=NOCHE_ALTA + (255,))
        d.line([tri[1], tri[2]], fill=(70, 61, 53, 255), width=2)


def pegar(img, capa, cx, cy):
    """Pega una copia (con sombra y margen) centrada en (cx, cy)."""
    img.alpha_composite(capa, (round(cx - capa.width / 2), round(cy - capa.height / 2)))


# ------------------------------------------------------------ láminas

def l_portada(cfg, lam, n):
    W, H, M, B, R = g("W"), g("H"), g("M"), g("B"), g("R")
    img = foto_base(cfg, lam)
    ancho = W * lam["ancho"] - M if lam.get("ancho") else (W - 2 * M - R)
    tam = 118 * lam.get("escala", 1.0)
    baj = lam.get("bajada", "")
    alto = alto_titular(lam["titulo"], tam, ancho, 0.98) + (28 + aa.alto_texto(baj, 38, ancho - 40) if baj else 0)
    y = H - B - alto
    img.alpha_composite(velo(W, H, max(0.05, (y - 520) / H), 0.97))
    cabecera(img, lam.get("meta", cfg["meta"]))
    if lam.get("rotulo"):
        antetitulo(img, M, y - 34, lam["rotulo"], sombra=True)
    y = titular(img, M, y, lam["titulo"], tam, ancho, inter=0.98)
    if baj:
        aa.texto(img, M, y + 28, baj, 38, ancho - 40, COPIA + (225,))
    pie(img, aa.credito(lam), COPIA + (170,))
    return img


def l_foto(cfg, lam, n):
    W, H, M, T, B, R = g("W"), g("H"), g("M"), g("T"), g("B"), g("R")
    img = foto_base(cfg, lam)
    arriba = lam.get("posicion") == "arriba"
    ancho = W * lam["ancho"] - M if lam.get("ancho") else (W - 2 * M - R)
    tx, tt = lam.get("texto", ""), lam.get("titulo", "")
    alto = (alto_titular(tt, 92, ancho) + 18 if tt else 0) + aa.alto_texto(tx, 40, ancho)
    if arriba:
        img.alpha_composite(velo_superior(W, H, 0.62, 0.92))
        y = T + 190
    else:
        y = H - B - alto
        img.alpha_composite(velo(W, H, max(0.15, (y - 300) / H), 0.95))
    cabecera(img, lam.get("meta", cfg["meta"]))
    if lam.get("rotulo"):
        antetitulo(img, M, y - 30, lam["rotulo"], sombra=True)
    if tt:
        y = titular(img, M, y, tt, 92, ancho) + 18
    aa.texto(img, M, y, tx, 40, ancho, COPIA + (235,))
    personas = lam.get("persona") or []
    for p in ([personas] if isinstance(personas, dict) else personas):
        aa.rotulo_persona(img, p)
    pie(img, aa.credito(lam), COPIA + (170,))
    return img


def cartela(img, x, y, c, ancho):
    """La cartela de museo: título de la obra en serif cursiva, autor y año en versalitas, técnica y colección
    en gris. c = {"titulo", "autor", "fecha", "tecnica", "lugar"} (todo opcional salvo el título)."""
    d = ImageDraw.Draw(img)
    d.line([(x, y), (x + 70, y)], fill=TERRACOTA, width=3)
    y += 22
    for linea in aa.partir(c["titulo"], cursiva(56), ancho):
        d.text((x, y + 48), linea, font=cursiva(56), fill=COPIA, anchor="ls")
        y += 58
    autor = " · ".join(v for v in (c.get("autor"), c.get("fecha")) if v)
    if autor:
        espaciado(d, x, y + 34, autor.upper(), dn.sans(21, 650, 100), AMBAR)
        y += 44
    resto = " · ".join(v for v in (c.get("tecnica"), c.get("lugar")) if v)
    for linea in aa.partir(resto, dn.sans(26, 500, 96), ancho):
        d.text((x, y + 30), linea, font=dn.sans(26, 500, 96), fill=GRIS, anchor="ls")
        y += 34
    return y


def alto_cartela(c, ancho):
    h = 22 + 58 * len(aa.partir(c["titulo"], cursiva(56), ancho))
    h += 44 if (c.get("autor") or c.get("fecha")) else 0
    resto = " · ".join(v for v in (c.get("tecnica"), c.get("lugar")) if v)
    return h + 34 * len(aa.partir(resto, dn.sans(26, 500, 96), ancho)) if resto else h


def l_obra(cfg, lam, n):
    """La obra completa, sin recorte ni cambio de color, como copia con borde y esquineros sobre el negro;
    debajo, la cartela y un texto corto. "obra": "fuentes/x.jpg", "cartela": {...}, "texto", "rotulo".
    "borde": 0 quita el borde de papel (para pinturas u objetos con su propio fondo)."""
    W, H, M, T, B, R = g("W"), g("H"), g("M"), g("T"), g("B"), g("R")
    img = fondo(80 + n)
    ancho = W - 2 * M - R
    c = lam.get("cartela")
    tx = lam.get("texto", "")
    abajo = (alto_cartela(c, ancho) + 20 if c else 0) + (aa.alto_texto(tx, 36, ancho) + 14 if tx else 0) + (48 if lam.get("rotulo") else 0)
    arriba = T + 120
    caja = (ancho + 20, H - B - abajo - arriba - 50)
    cp = copia(cfg["_base"] / lam["obra"], caja, lam.get("borde"), lam.get("giro", 0), lam.get("esquineros", True))
    pegar(img, cp, M + ancho / 2, arriba + caja[1] / 2 + 10)
    cabecera(img, lam.get("meta", cfg["meta"]), sobre_foto=False)
    y = H - B - abajo
    if lam.get("rotulo"):
        antetitulo(img, M, y + 26, lam["rotulo"])
        y += 48
    if c:
        y = cartela(img, M, y, c, ancho) + 20
    if tx:
        aa.texto(img, M, y, tx, 36, ancho, COPIA + (225,))
    pie(img, lam.get("credito", ""))
    return img


def l_copias(cfg, lam, n):
    """Dos o tres fotos como copias sueltas sobre la mesa, un poco giradas y montadas, y debajo rotulo,
    titulo y texto. "copias": [{"foto", "giro" (opcional)}, ...]. Respeta las fotos: sin recorte."""
    W, H, M, T, B, R = g("W"), g("H"), g("M"), g("T"), g("B"), g("R")
    img = fondo(90 + n)
    ancho = W - 2 * M - R
    tt, tx = lam.get("titulo", ""), lam.get("texto", "")
    abajo = (alto_titular(tt, 80, ancho) + 16 if tt else 0) + (aa.alto_texto(tx, 36, ancho) if tx else 0) + (50 if lam.get("rotulo") else 0)
    arriba, fondo_y = T + 120, H - B - abajo - 30
    copias = lam["copias"][:3]
    k = len(copias)
    alto_zona = fondo_y - arriba
    # posiciones: dos en diagonal; tres en abanico
    if k == 1:
        sitios = [(0.5, 0.5, 0.9, 0.95)]
    elif k == 2:
        sitios = [(0.36, 0.38, 0.62, 0.66), (0.64, 0.64, 0.62, 0.66)]
    else:
        sitios = [(0.3, 0.33, 0.5, 0.56), (0.7, 0.36, 0.5, 0.56), (0.5, 0.7, 0.54, 0.56)]
    giros = [-4.5, 3.5, -2] if k > 1 else [0]
    for i, (c, (fx, fy, fw, fh)) in enumerate(zip(copias, sitios)):
        cp = copia(cfg["_base"] / c["foto"], (round((ancho + 40) * fw), round(alto_zona * fh)), c.get("borde"),
                   c.get("giro", giros[i % len(giros)]), c.get("esquineros", False), c.get("original", True))
        pegar(img, cp, M - 20 + (ancho + 40) * fx, arriba + alto_zona * fy)
    cabecera(img, lam.get("meta", cfg["meta"]), sobre_foto=False)
    y = H - B - abajo
    if lam.get("rotulo"):
        antetitulo(img, M, y + 26, lam["rotulo"])
        y += 50
    if tt:
        y = titular(img, M, y, tt, 80, ancho) + 16
    if tx:
        aa.texto(img, M, y, tx, 36, ancho, COPIA + (225,))
    pie(img, lam.get("credito", ""))
    return img


def l_epoca(cfg, lam, n):
    """La época: un año o un dato enorme en serif cursiva ámbar, rotulo, titulo y texto. Con "tiempo":
    [["1890", "texto"], ...] es una línea de tiempo (años en cursiva, textos que se entienden solos).
    Opcional: "foto" de archivo como copia pequeña arriba a la derecha (sin recorte)."""
    W, H, M, T, B, R = g("W"), g("H"), g("M"), g("T"), g("B"), g("R")
    img = fondo(60 + n, NOCHE_ALTA if lam.get("claro") else NOCHE)
    ancho = W - 2 * M - R
    cabecera(img, lam.get("meta", cfg["meta"]), sobre_foto=False)
    capa = Image.new("RGBA", (W, H * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    y = 0
    if lam.get("dato"):
        tam = 330
        while cursiva(tam).getlength(lam["dato"]) > ancho and tam > 120:
            tam -= 10
        d.text((M - tam * 0.03, y + tam * 0.8), lam["dato"], font=cursiva(tam), fill=AMBAR, anchor="ls")
        y += tam * 0.92
    if lam.get("rotulo"):
        antetitulo(capa, M, y + 24, lam["rotulo"])
        y += 52
    if lam.get("titulo"):
        y = titular(capa, M, y, lam["titulo"], 82, ancho) + 22
    if lam.get("texto"):
        y = aa.texto(capa, M, y, lam["texto"], 38, ancho, COPIA + (230,)) + 24
    ft = dn.sans(34, 500, 96)
    for anio, texto_ in lam.get("tiempo", []):
        d.line([(M, y), (M + ancho, y)], fill=COPIA + (60,), width=1)
        lineas = aa.partir(texto_, ft, ancho - 190)
        d.text((M, y + 58), str(anio), font=cursiva(58), fill=AMBAR, anchor="ls")
        for k, linea in enumerate(lineas):
            d.text((M + 190, y + 50 + k * 42), linea, font=ft, fill=COPIA, anchor="ls")
        y += 76 + 42 * (len(lineas) - 1)
    arriba, abajo = T + 140, H - B - 20
    if lam.get("foto"):  # copia de archivo arriba; el bloque de texto se va al fondo
        alto_foto = abajo - arriba - y - 40
        if alto_foto > 220:
            cp = copia(cfg["_base"] / lam["foto"], (round(ancho * 0.8), round(alto_foto)), giro=lam.get("giro", 2.5))
            pegar(img, cp, W / 2, arriba + alto_foto / 2)
        y0 = abajo - y
    else:
        y0 = arriba + max(0, (abajo - arriba - y) * 0.5)
    img.alpha_composite(capa.crop((0, -round(y0), W, H - round(y0))))
    if y0 + y > abajo + 10:
        print(f"  ojo: la lámina {n} se pasa de alto; acorta el texto o la línea de tiempo")
    pie(img, lam.get("credito", ""))
    return img


def l_citas(cfg, lam, n):
    """La voz del artista: comillas grandes en terracota y la cita en serif (acento en cursiva ámbar)."""
    W, H, M, T, B, R = g("W"), g("H"), g("M"), g("T"), g("B"), g("R")
    img = fondo(20 + n)
    cabecera(img, (lam.get("rotulo") or lam.get("meta", cfg["meta"])).upper(), sobre_foto=False)
    d = ImageDraw.Draw(img)
    ancho = W - 2 * M - R - 70
    fa = dn.sans(22, 650, 100)
    bloques = []
    for c in lam["citas"]:
        r = rico(c["texto"], 62, COPIA, 1.08)
        bloques.append((r, r.lineas(ancho), aa.partir(c["autor"].upper(), fa, ancho)))
    total = sum(r.alto(l) + 34 + 32 * len(a) for r, l, a in bloques) + 100 * (len(bloques) - 1)
    y = T + 120 + (H - T - 120 - B - total) / 2
    for k, (r, l, autor) in enumerate(bloques):
        d.text((M - 8, y + 170), "“", font=serif(260), fill=TERRACOTA, anchor="ls")
        y = r.dibujar(d, M + 70, y, l) + 34
        for linea in autor:
            espaciado(d, M + 70, y + 8, linea, fa, AMBAR)
            y += 32
        if k < len(bloques) - 1:
            y += 50
            d.line([(M + 70, y), (M + 170, y)], fill=COPIA + (90,), width=2)
            y += 50
    pie(img, lam.get("credito", ""))
    return img


def l_cta(cfg, lam, n):
    """Cierre: la pregunta en serif sobre el negro, con el signo en cursiva terracota y la firma."""
    W, H, M, T, B, R = g("W"), g("H"), g("M"), g("T"), g("B"), g("R")
    img = fondo(40 + n)
    cabecera(img, (lam.get("rotulo") or "Conversemos").upper(), sobre_foto=False)
    d = ImageDraw.Draw(img)
    ancho = W - 2 * M - R
    d.text((W - M - R + 10, T + 600), "?", font=cursiva(660), fill=TERRACOTA + (235,), anchor="rs")
    pregunta, texto_ = lam["pregunta"], lam.get("texto", "")
    tam = 100 * lam.get("escala", 1.0)
    alto = alto_titular(pregunta, tam, ancho) + (26 + aa.alto_texto(texto_, 38, ancho) if texto_ else 0)
    y_pie = H - B - 150
    y = max(T + 330, y_pie - 70 - alto)
    antetitulo(img, M, y - 32, "Tu mirada")
    y = titular(img, M, y, pregunta, tam, ancho)
    if texto_:
        aa.texto(img, M, y + 26, texto_, 38, ancho, COPIA + (220,))
    fa = dn.sans(24, 650, 100)
    esquinero_marca(img, M, y_pie + 12, 18, TERRACOTA)
    x = M + 32
    for k, palabra in enumerate(["COMENTA", "GUARDA", "COMPARTE"]):
        if k:
            x = espaciado(d, x + 4, y_pie + 32, "·", fa, COPIA + (150,)) + 6
        x = espaciado(d, x, y_pie + 32, palabra, fa, AMBAR if k == 0 else COPIA)
    lg = dn.logo(64)
    img.alpha_composite(lg, (M, round(y_pie + 84)))
    d = ImageDraw.Draw(img)
    d.text((W - M - R, y_pie + 84 + 46), lam.get("cuenta", "@dialmedio"), font=dn.mono(28, True), fill=COPIA, anchor="rs")
    d.text((M + lg.width + 24, y_pie + 84 + 46), "Sintonizar es conversar.", font=dn.serif(34), fill=AMBAR, anchor="ls")
    return img


ESTILOS = {"portada": l_portada, "foto": l_foto, "obra": l_obra, "copias": l_copias, "epoca": l_epoca,
           "tiempo": l_epoca, "citas": l_citas, "cta": l_cta}


def estilo_de(lam):
    if lam.get("estilo"):
        return lam["estilo"]
    if lam.get("obra"):
        return "obra"
    if lam.get("copias"):
        return "copias"
    if lam.get("tiempo") or (lam.get("tipo") == "texto" and lam.get("dato")):
        return "epoca"
    e = aa.estilo_de(lam)
    return "epoca" if e in ("pais", "analisis") else e


def lamina(cfg, lam, n):
    return ESTILOS[estilo_de(lam)](cfg, lam, n)


def capa_video(cfg, lam):
    lam = dict(lam, _video=True)
    return (l_portada if estilo_de(lam) == "portada" else l_foto)(cfg, lam, 0)
