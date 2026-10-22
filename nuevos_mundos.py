"""Estilo visual de Nuevos Mundos Posibles (v2, 22 oct 2026), la línea de buenas noticias de Al Aire.

Martín pidió que no fuera predecible ni cuadriculada: más suave, elegante y sutil, coherente con Dial,
con el verde y el naranja juntos. Referentes: The Guardian (titulares en serif, mucho aire, fotos
grandes, datos limpios), La Linterna (impresión) y Mutante (riso de dos tintas).

- Titulares en Instrument Serif, con el acento en cursiva (brasa sobre foto u oscuro, terracota sobre papel).
- Eucalipto (verde suave) + brasa: el par de la línea. Papel y hueso de Dial como campos claros.
- Fotos de las láminas sin foto en riso de dos tintas (eucalipto y brasa), sin grano.
- Rótulos sin caja: una hoja y el texto en mono, como los antetítulos del Guardian.
- La misma estructura de Al Aire: cabecera, logo, crédito abajo, lámina final de pregunta.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dial_noticias as dn  # noqa: E402
import al_aire as aa  # noqa: E402

CARBON, PAPEL, HUESO = dn.CARBON, dn.PAPEL, (233, 223, 207)
TERRACOTA, BRASA = dn.TERRACOTA, (229, 138, 58)
EUCALIPTO = (86, 112, 94)          # el verde de la línea: suave, apagado, hacia el gris
EUCALIPTO_HONDO = (44, 62, 50)     # el mismo verde, oscuro: fondo del cierre y tinta del riso
SALVIA = (200, 211, 190)           # verde muy claro, para barras y filetes
GRIS = (95, 85, 76)
SELLO = "NUEVOS MUNDOS POSIBLES"


def g(nombre):  # medidas vivas de al_aire (cambian con el formato)
    return getattr(aa, nombre)


# ------------------------------------------------------------ tipografía

def serif(tam):
    return dn.fuente("InstrumentSerif-Regular.ttf", tam)


def cursiva(tam):
    return dn.fuente("InstrumentSerif-Italic.ttf", tam)


def rico_serif(contenido, tam, color, acento, inter=1.0):
    r = dn.Rico(contenido, tam, color=color, acento=acento, interlineado=inter)
    r.f, r.fa = serif(tam), cursiva(tam)
    return r


def alto_titular(contenido, tam, ancho, inter=1.0):
    r = rico_serif(contenido, tam, PAPEL, BRASA, inter)
    return r.alto(r.equilibradas(ancho))


def titular(img, x, y, contenido, tam, ancho, color=PAPEL, acento=BRASA, inter=1.0):
    r = rico_serif(contenido, tam, color, acento, inter)
    return r.dibujar(ImageDraw.Draw(img), x, y, r.equilibradas(ancho))


def antetitulo(img, x, y, texto, color, hoja=None):
    """Rótulo sin caja: una hoja y el texto en mono. y = línea base. Sobre fotos y verdes, el texto va
    en papel y solo la hoja en brasa (la brasa en letra pequeña se pierde)."""
    aa.hoja(img, x + 11, y - 9, 10, hoja or color)
    ImageDraw.Draw(img).text((x + 30, y), texto.upper(), font=dn.mono(24, True), fill=color, anchor="ls")


def caja(img, x, y, texto, fondo, color, tam=26, hoja=None):
    """Caja mono como las de Al Aire (sello y acciones del cierre). Devuelve el borde derecho."""
    f = dn.mono(tam, medio=True)
    pad = tam * 0.55
    tx = x + pad + (tam * 1.05 if hoja else 0)
    w = f.getlength(texto) + (tx - x) + pad
    ImageDraw.Draw(img).rectangle([x, y, x + w, y + tam * 1.7], fill=fondo)
    if hoja:
        aa.hoja(img, x + pad + tam * 0.36, y + tam * 0.85, tam * 0.36, hoja)
    ImageDraw.Draw(img).text((tx, y + tam * 1.2), texto, font=f, fill=color, anchor="ls")
    return x + w


def cabecera(img, meta, fondo="foto"):
    """fondo: "foto", "claro" (papel) u "oscuro" (eucalipto). Sello eucalipto con la hoja brasa."""
    W, H, M, T = g("W"), g("H"), g("M"), g("T")
    if fondo == "foto":
        img.alpha_composite(dn.degradado_superior(W, H, hasta=(T + 150) / H, fuerza=0.5))
    sello_fondo = PAPEL if fondo == "oscuro" else EUCALIPTO
    sello_tinta = EUCALIPTO_HONDO if fondo == "oscuro" else PAPEL
    fin = caja(img, M, T, SELLO, sello_fondo, sello_tinta, tam=26, hoja=BRASA)
    lg = dn.logo(38)
    if fondo == "claro":
        a = np.asarray(lg).copy()
        claro = a[..., 0] > 200
        a[claro, :3] = CARBON
        a[~claro & (a[..., 3] > 0), :3] = TERRACOTA
        lg = Image.fromarray(a)
    fm = dn.mono(22)
    x, y = fin + 16, T + 26 * 1.2
    if x + fm.getlength(meta) > W - M - lg.width - 16:  # el sello es largo: la fecha baja
        x, y = M, T + 26 * 1.7 + 34
    if fondo == "foto":  # sobre cielos y paredes claras, la fecha va en caja carbón
        x = x if x == M else x - 16
        ImageDraw.Draw(img).rectangle([x, y - 27, x + fm.getlength(meta) + 28, y + 11], fill=CARBON)
        x += 14
    ImageDraw.Draw(img).text((x, y), meta, font=fm, fill=(CARBON if fondo == "claro" else PAPEL) + (225,), anchor="ls")
    img.alpha_composite(lg, (W - M - lg.width, T + 2))


def pie(img, contenido, color):
    aa.pie(img, contenido.upper(), color)


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


# ------------------------------------------------------------ láminas

def l_portada(cfg, lam, n):
    W, H, M, B, R = g("W"), g("H"), g("M"), g("B"), g("R")
    img = aa.foto_base(cfg, lam)
    aa.degradado_bajo(img, 0.36 if B < 200 else 0.3, 0.95)
    cabecera(img, lam.get("meta", cfg["meta"]))
    ancho = W * lam["ancho"] - M if lam.get("ancho") else (W - 2 * M - R)
    tam = 116 * lam.get("escala", 1.0)
    baj = lam.get("bajada", "")
    alto = alto_titular(lam["titulo"], tam, ancho, 0.98) + (26 + aa.alto_texto(baj, 38, ancho - 40) if baj else 0)
    y = H - B - alto
    if lam.get("rotulo"):
        antetitulo(img, M, y - 30, lam["rotulo"], PAPEL, BRASA)
    y = titular(img, M, y, lam["titulo"], tam, ancho, inter=0.98)
    if baj:
        aa.texto(img, M, y + 26, baj, 38, ancho - 40, PAPEL + (235,))
    pie(img, aa.credito(lam), PAPEL + (190,))
    return img


def l_foto(cfg, lam, n):
    W, H, M, T, B, R = g("W"), g("H"), g("M"), g("T"), g("B"), g("R")
    img = aa.foto_base(cfg, lam)
    arriba = lam.get("posicion") == "arriba"
    if arriba:
        img.alpha_composite(dn.degradado_superior(W, H, hasta=0.58, fuerza=0.86))
    else:
        aa.degradado_bajo(img, 0.46 if B < 200 else 0.4, 0.9)
    cabecera(img, lam.get("meta", cfg["meta"]))
    ancho = W * lam["ancho"] - M if lam.get("ancho") else (W - 2 * M - R)
    tx, tt = lam.get("texto", ""), lam.get("titulo", "")
    alto = (alto_titular(tt, 92, ancho) + 16 if tt else 0) + aa.alto_texto(tx, 40, ancho)
    y = H - B - alto if not arriba else T + 200
    if lam.get("rotulo"):
        antetitulo(img, M, y - 28, lam["rotulo"], PAPEL, BRASA)
    if tt:
        y = titular(img, M, y, tt, 92, ancho) + 16
    aa.texto(img, M, y, tx, 40, ancho, PAPEL + (240,))
    personas = lam.get("persona") or []
    for p in ([personas] if isinstance(personas, dict) else personas):
        aa.rotulo_persona(img, p)
    pie(img, aa.credito(lam), PAPEL + (190,))
    return img


def l_ficha(cfg, lam, n):
    """Papel con el dato grande en serif. Opcional: banda de foto en riso arriba (semitono, foco_semitono),
    antetítulo (rotulo), dato, dato_pie, titulo, texto, campos [[etiqueta, valor]] en lista con filetes,
    items numerados y cierre. También hace de lámina de análisis en esta línea."""
    W, H, M, T, B, R = g("W"), g("H"), g("M"), g("T"), g("B"), g("R")
    img = aa.campo(PAPEL, 50 + n, 0.025)
    ancho = W - 2 * M - R
    capa = Image.new("RGBA", (W, H * 2), (0, 0, 0, 0))  # el contenido va en su capa para poder centrarlo
    y = T + 150
    con_foto = bool(lam.get("semitono"))
    if con_foto:
        alto_foto = round(H * 0.4)
        foto = Image.open(cfg["_base"] / lam["semitono"]).convert("RGB")
        img.alpha_composite(riso(foto, (W, alto_foto), tuple(lam.get("foco_semitono", (0.5, 0.5)))), (0, 0))
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
    if lam.get("titulo"):
        y = titular(capa, M, y, lam["titulo"], 84 * lam.get("escala", 1.0), ancho, color=CARBON, acento=TERRACOTA) + 22
    if lam.get("texto"):
        y = aa.texto(capa, M, y, lam["texto"], 38, ancho, CARBON) + 22
    if lam.get("campos"):
        fe, fv = dn.mono(20, True), serif(40)
        col = 260
        for etq, valor in lam["campos"]:
            lineas = aa.partir(valor, fv, ancho - col)
            d.line([(M, y), (M + ancho, y)], fill=SALVIA, width=2)
            d.text((M, y + 44), etq.upper(), font=fe, fill=EUCALIPTO, anchor="ls")
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
    cabecera(img, lam.get("meta", cfg["meta"]), "claro")
    pie(img, lam.get("credito", ""), GRIS)
    return img


def l_serie(cfg, lam, n):
    """Una serie en barras horizontales: "serie": [["2021", 13038], ...]; la última barra va en brasa.
    Con rotulo, dato (el cambio, p. ej. "−74 %") y dato_pie arriba."""
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
    tope = max(v for _, v in serie)
    fe, fv = dn.mono(24, True), dn.sans(32, 600, 88)
    col, alto_barra, paso = 110, 46, 70
    largo = ancho - col - 150
    for k, (etq, v) in enumerate(serie):
        ultima = k == len(serie) - 1
        w = max(6, largo * v / tope)
        cy = y + k * paso
        d.text((M, cy + alto_barra * 0.72), str(etq), font=fe, fill=GRIS, anchor="ls")
        d.rectangle([M + col, cy, M + col + w, cy + alto_barra], fill=BRASA if ultima else SALVIA)
        d.text((M + col + w + 16, cy + alto_barra * 0.74), f"{v:,}".replace(",", "."), font=fv,
               fill=CARBON if ultima else GRIS, anchor="ls")
    y += paso * len(serie)
    if lam.get("unidad"):
        d.text((M + col, y + 20), lam["unidad"].upper(), font=dn.mono(20), fill=GRIS, anchor="ls")
    pie(img, lam.get("credito", ""), GRIS)
    return img


def l_citas(cfg, lam, n):
    """Hueso: las voces, en serif, con comillas grandes en brasa."""
    W, H, M, T, B, R = g("W"), g("H"), g("M"), g("T"), g("B"), g("R")
    img = aa.campo(HUESO, 20 + n, 0.025)
    cabecera(img, (lam.get("rotulo") or lam.get("meta", cfg["meta"])).upper(), "claro")
    d = ImageDraw.Draw(img)
    ancho = W - 2 * M - R - 90
    fa = dn.mono(21, True)
    bloques = []
    for c in lam["citas"]:
        r = rico_serif(c["texto"], 60, CARBON, TERRACOTA, 1.08)
        bloques.append((r, r.lineas(ancho), aa.partir(c["autor"].upper(), fa, ancho)))
    total = sum(r.alto(l) + 30 + 30 * len(a) for r, l, a in bloques) + 90 * (len(bloques) - 1)
    y = T + 120 + (H - T - 120 - B - total) / 2
    for k, (r, l, autor) in enumerate(bloques):
        d.text((M - 6, y + 150), "“", font=serif(230), fill=BRASA, anchor="ls")
        y = r.dibujar(d, M + 90, y, l) + 30
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
        foto = Image.open(cfg["_base"] / lam["semitono"]).convert("RGB")
        img.alpha_composite(riso(foto, (W, alto_foto), tuple(lam.get("foco_semitono", (0.5, 0.5))), fondo=HUESO), (0, 0))
        y = alto_foto + 30
    cabecera(img, lam.get("meta", cfg["meta"]), "claro" if lam.get("semitono") else "oscuro")
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


def l_dos(cfg, lam, n):
    """Dos personas con el mismo trato (p. ej. los candidatos de una elección): dos retratos del mismo
    tamaño lado a lado, nombre y cargo en cada uno, y abajo una banda eucalipto con titulo y texto.
    "personas": [{"foto", "foco", "nombre", "cargo", "credito"}, {...}]"""
    W, H, M, B, R = g("W"), g("H"), g("M"), g("B"), g("R")
    img = aa.campo(EUCALIPTO, 60 + n, 0.03)
    alto = round(H * 0.64)
    medio = 6
    an = (W - medio) // 2
    fn, fc = serif(50), dn.mono(19, True)
    for k, p in enumerate(lam["personas"]):
        foto = dn.preparar_foto(cfg["_base"] / p["foto"], p.get("ajuste"), f"{an}:{alto}", p.get("foco")).convert("RGBA")
        foto = foto.resize((an, alto), Image.LANCZOS)
        foto.alpha_composite(dn.degradado_inferior(an, alto, desde=0.55, fuerza=0.85))
        dd = ImageDraw.Draw(foto)
        dd.text((M * 0.6, alto - 64), p["nombre"], font=fn, fill=PAPEL, anchor="ls")
        dd.text((M * 0.6, alto - 30), p.get("cargo", "").upper(), font=fc, fill=PAPEL + (220,), anchor="ls")
        img.alpha_composite(foto, (k * (an + medio), 0))
    cabecera(img, lam.get("meta", cfg["meta"]))
    ancho = W - 2 * M - R
    y = alto + 48
    if lam.get("rotulo"):
        antetitulo(img, M, y + 4, lam["rotulo"], PAPEL, BRASA)
        y += 40
    if lam.get("titulo"):
        y = titular(img, M, y, lam["titulo"], 84, ancho) + 14
    if lam.get("texto"):
        aa.texto(img, M, y, lam["texto"], 36, ancho, PAPEL + (235,))
    creditos = " · ".join(p.get("credito", "") for p in lam["personas"] if p.get("credito"))
    pie(img, lam.get("credito", creditos), PAPEL + (190,))
    return img


def l_cta(cfg, lam, n):
    """Cierre: la pregunta para comentar, en serif sobre eucalipto hondo, con el signo en cursiva brasa."""
    W, H, M, T, B, R = g("W"), g("H"), g("M"), g("T"), g("B"), g("R")
    img = aa.campo(EUCALIPTO_HONDO, 40 + n, 0.04)
    cabecera(img, (lam.get("rotulo") or "Conversemos").upper(), "oscuro")
    d = ImageDraw.Draw(img)
    ancho = W - 2 * M - R
    d.text((W - M - R + 10, T + 560), "?", font=cursiva(640), fill=BRASA, anchor="rs")
    pregunta, texto_ = lam["pregunta"], lam.get("texto", "")
    tam = 100 * lam.get("escala", 1.0)
    alto = alto_titular(pregunta, tam, ancho) + (26 + aa.alto_texto(texto_, 38, ancho) if texto_ else 0)
    y_pie = H - B - 150
    y = max(T + 320, y_pie - 70 - alto)
    antetitulo(img, M, y - 30, "Tu opinión", PAPEL, BRASA)
    y = titular(img, M, y, pregunta, tam, ancho)
    if texto_:
        aa.texto(img, M, y + 26, texto_, 38, ancho, PAPEL + (225,))
    x = M
    for k, palabra in enumerate(["COMENTA", "GUARDA", "COMPARTE"]):
        x = caja(img, x, y_pie, palabra, BRASA if k == 0 else PAPEL, CARBON, 26, hoja=CARBON if k == 0 else None) + 10
    lg = dn.logo(64)
    img.alpha_composite(lg, (M, round(y_pie + 84)))
    d = ImageDraw.Draw(img)
    d.text((W - M - R, y_pie + 84 + 46), lam.get("cuenta", "@dialmedio"), font=dn.mono(28, True), fill=PAPEL, anchor="rs")
    d.text((M + lg.width + 24, y_pie + 84 + 46), "Sintonizar es conversar.", font=dn.serif(34), fill=BRASA, anchor="ls")
    return img


ESTILOS = {"portada": l_portada, "foto": l_foto, "ficha": l_ficha, "serie": l_serie, "citas": l_citas,
           "pais": l_lugar, "lugar": l_lugar, "dos": l_dos, "cta": l_cta}


def estilo_de(lam):
    if lam.get("estilo"):
        return lam["estilo"]
    if lam.get("personas"):
        return "dos"
    if lam.get("serie"):
        return "serie"
    if lam.get("tipo") == "texto" and (lam.get("dato") or lam.get("campos")):
        return "ficha"
    return aa.estilo_de(lam)


def lamina(cfg, lam, n):
    estilo = estilo_de(lam)
    if estilo == "analisis":  # en esta línea, el análisis es una ficha (papel, sin carbón)
        estilo = "ficha"
    return ESTILOS[estilo](cfg, lam, n)


def capa_video(cfg, lam):
    lam = dict(lam, _video=True)
    return (l_portada if estilo_de(lam) == "portada" else l_foto)(cfg, lam, 0)
