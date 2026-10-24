"""Estilo visual de Termómetro (antes Nuevos Mundos Posibles; v2, 22 oct 2026), la línea de clima y ambiente de Al Aire.

Martín pidió que no fuera predecible ni cuadriculada: más suave, elegante y sutil, coherente con Dial,
con el verde y el naranja juntos. Referentes: The Guardian (titulares en serif, mucho aire, fotos
grandes, datos limpios), La Linterna (impresión) y Mutante (riso de dos tintas).

- Titulares en Instrument Serif, con el acento en cursiva (brasa sobre foto u oscuro, terracota sobre papel).
- Eucalipto (verde suave) + brasa: el par de la línea. Papel y hueso de Dial como campos claros.
- Fotos de las láminas sin foto en riso de dos tintas (eucalipto y brasa), sin grano.
- Rótulos sin caja, en sans espaciada del color de la línea, como los antetítulos del Guardian (v3: sin hoja ni mono;
  el símbolo es el aro de Dial con el punto brasa a las tres, en la cabecera). Papel reciclado en las láminas claras.
- La misma estructura de Al Aire: cabecera, logo, crédito abajo, lámina final de pregunta.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dial_noticias as dn  # noqa: E402
import al_aire as aa  # noqa: E402
import materia as mt  # noqa: E402

CARBON, PAPEL, HUESO = dn.CARBON, dn.PAPEL, (233, 223, 207)
RECICLADO = (236, 233, 223)        # v3: las láminas claras van en papel reciclado (con sus motas), no en el papel de Dial
RECICLADO_HUESO = (230, 223, 208)  # el mismo papel, más cálido, para las citas
TERRACOTA, BRASA = dn.TERRACOTA, (229, 138, 58)
EUCALIPTO = (86, 112, 94)          # el verde de la línea: suave, apagado, hacia el gris
EUCALIPTO_HONDO = (44, 62, 50)     # el mismo verde, oscuro: fondo del cierre y tinta del riso
SALVIA = (200, 211, 190)           # verde muy claro, para barras y filetes
GRIS = (95, 85, 76)
SELLO = "TERMÓMETRO"
# v3 (revisión de conjunto, 24 oct 2026): sobre las fotos la franja va en eucalipto con la cursiva en papel. Con la
# franja brasa, en la rejilla del perfil una portada de Termómetro no se distinguía de una de Al Aire. La brasa
# sigue en el antetítulo, el punto del aro, el dato destacado y los campos verdes (el verde y el naranja juntos).
FRANJA_FOTO = dict(franja=EUCALIPTO, acento=PAPEL)


def g(nombre):  # medidas vivas de al_aire (cambian con el formato)
    return getattr(aa, nombre)


# ------------------------------------------------------------ tipografía

def serif(tam):
    return dn.fuente("InstrumentSerif-Regular.ttf", tam)


def cursiva(tam):
    return dn.fuente("InstrumentSerif-Italic.ttf", tam)


def rico_serif(contenido, tam, color, inter=1.0):
    r = dn.Rico(contenido, tam, color=color, acento=CARBON, interlineado=inter)
    r.f, r.fa = serif(tam), cursiva(tam)
    return r


def dibujar_franja(img, r, x, y, lineas, franja, acento=CARBON):
    """Como Rico.dibujar, pero el acento (*así*) va en cursiva carbón sobre una franja (22 oct 2026:
    la cursiva naranja sola no siempre se leía). Primero se pintan todas las franjas y después todo
    el texto, para que las letras que bajan de la línea de arriba no queden tapadas."""
    d = ImageDraw.Draw(img)
    asc = r.f.getmetrics()[0]
    tam = r.tam
    posiciones = []  # (x, base, palabra, acento)
    yy = y
    for l in lineas:
        cx, base = x, yy + asc
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
    if rects:
        franja_impresa(img, rects, franja, sum(map(ord, "".join(p[2] for p in posiciones))) % 997)
    for cx, base, w, ac, _ in posiciones:
        d.text((cx, base), w, font=r.fa if ac else r.f, fill=acento if ac else r.color, anchor="ls")
    return yy


def franja_impresa(img, rects, color, semilla):
    """Franjas con tinta de impresión (v3: la misma de todas las líneas, materia.franja)."""
    mt.franja(img, rects, color, semilla)


def alto_titular(contenido, tam, ancho, inter=1.0):
    r = rico_serif(contenido, tam, PAPEL, inter)
    return r.alto(r.equilibradas(ancho))


def titular(img, x, y, contenido, tam, ancho, color=PAPEL, franja=BRASA, inter=1.0, acento=CARBON):
    """Titular en serif con el acento sobre franja: brasa sobre fotos y verdes, salvia sobre papel."""
    r = rico_serif(contenido, tam, color, inter)
    return dibujar_franja(img, r, x, y, r.equilibradas(ancho), franja, acento)


def espaciado(d, x, y, texto, f, fill, tracking=0.14, sombra=False):
    """Texto en versalitas con espacio entre letras (PIL no lo trae). Devuelve el x final.
    sombra: una sombra carbón de 2 px, para letra pequeña clara sobre fotos con zonas claras."""
    return aa.versal(d._image, x, y, texto, f, fill, tracking, sombra)  # v3: con kerning entre letras


def antetitulo(img, x, y, texto, color, hoja=None, sombra=False):
    """Antetítulo como en prensa: sans espaciada en el color de la línea, sin caja ni símbolo (v3: el símbolo
    de la línea es el aro de la cabecera; repetirlo en cada antetítulo era adorno). y = línea base.
    `hoja` es la tinta del antetítulo sobre los verdes (brasa); sobre fotos (sombra) va en papel, que se lee mejor."""
    tinta = color if sombra else (hoja or color)
    espaciado(ImageDraw.Draw(img), x, y, texto.upper(), dn.sans(21, 650, 100), tinta, sombra=sombra)


def cabecera(img, meta, fondo="foto"):
    """Cabecera de sección, como la de un periódico (22 oct 2026: las cajas se veían "muy digitales"):
    la hoja brasa y "Termómetro" en serif cursiva, el logo a la derecha, un filete fino
    a todo el ancho y debajo la fecha en versalitas. fondo: "foto", "claro" (papel) u "oscuro" (verdes)."""
    W, H, M, T, R = g("W"), g("H"), g("M"), g("T"), g("R")
    if fondo == "foto":
        img.alpha_composite(dn.degradado_superior(W, H, hasta=(T + 230) / H, fuerza=0.8))
    tinta = CARBON if fondo == "claro" else PAPEL
    d = ImageDraw.Draw(img)
    # v3: el aro de Dial con el punto brasa en la estación de Termómetro (a las tres), en lugar de la hoja
    aa.aro(img, M + 14, T + 21, 28, tinta, BRASA, aa.ESTACIONES["nuevos-mundos"])
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
    espaciado(d, M, T + 88, meta.upper(), dn.sans(20, 650, 100), tinta + (240,), sombra=fondo == "foto")


def pie(img, contenido, color):
    aa.pie(img, contenido, color)  # v3: en caja normal, como pie de foto


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
    return foto.resize(tam, Image.LANCZOS).convert("RGBA")


# ------------------------------------------------------------ láminas

def l_portada(cfg, lam, n):
    W, H, M, B, R = g("W"), g("H"), g("M"), g("B"), g("R")
    img = aa.foto_base(cfg, lam)
    ancho = W * lam["ancho"] - M if lam.get("ancho") else (W - 2 * M - R)
    tam = 116 * lam.get("escala", 1.0)
    baj = lam.get("bajada", "")
    alto = alto_titular(lam["titulo"], tam, ancho, 0.98) + (26 + aa.alto_texto(baj, 38, ancho - 40) if baj else 0)
    y = H - B - alto
    # el degradado arranca un poco antes del texto, por alto que sea el bloque (cielos claros)
    img.alpha_composite(dn.degradado_inferior(W, H, desde=max(0.05, (y - 480) / H), fuerza=0.85))  # velo largo
    aa.degradado_bajo(img, max(0.12, (y - 150) / H), 0.97)
    cabecera(img, lam.get("meta", cfg["meta"]))
    if lam.get("rotulo"):
        antetitulo(img, M, y - 30, lam["rotulo"], PAPEL, BRASA, sombra=True)
    y = titular(img, M, y, lam["titulo"], tam, ancho, inter=0.98, **FRANJA_FOTO)
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
    ancho = W * lam["ancho"] - M if lam.get("ancho") else (W - 2 * M - R)
    tx, tt = lam.get("texto", ""), lam.get("titulo", "")
    alto = (alto_titular(tt, 92, ancho) + 16 if tt else 0) + aa.alto_texto(tx, 40, ancho)
    y = H - B - alto if not arriba else T + 200
    if not arriba:
        aa.degradado_bajo(img, max(0.2, (y - 170) / H), 0.92)
    cabecera(img, lam.get("meta", cfg["meta"]))
    if lam.get("rotulo"):
        antetitulo(img, M, y - 28, lam["rotulo"], PAPEL, BRASA, sombra=True)
    if tt:
        y = titular(img, M, y, tt, 92, ancho, **FRANJA_FOTO) + 16
    aa.texto(img, M, y, tx, 40, ancho, PAPEL + (240,))
    personas = lam.get("persona") or []
    for p in ([personas] if isinstance(personas, dict) else personas):
        aa.rotulo_persona(img, p)
    pie(img, aa.credito(lam), PAPEL + (190,))
    return img


def l_ficha(cfg, lam, n):
    """Papel con el dato grande en serif. Opcional: banda de foto en riso arriba (semitono, foco_semitono),
    antetítulo (rotulo), dato, dato_pie, destacado (la frase clave sobre franja brasa), titulo, texto,
    campos [[etiqueta, valor]] en lista con filetes,
    items numerados y cierre. También hace de lámina de análisis en esta línea."""
    W, H, M, T, B, R = g("W"), g("H"), g("M"), g("T"), g("B"), g("R")
    img = aa.campo(RECICLADO, 50 + n, clase="reciclado")
    ancho = W - 2 * M - R
    capa = Image.new("RGBA", (W, H * 2), (0, 0, 0, 0))  # el contenido va en su capa para poder centrarlo
    y = T + 150
    con_foto = bool(lam.get("semitono"))
    if con_foto:
        alto_foto = round(H * lam.get("alto_foto", 0.4))
        img.alpha_composite(banda(cfg, lam, (W, alto_foto)), (0, 0))
        y = alto_foto + 56
        if lam.get("pie_foto"):  # v3: pie de foto en cursiva, como en un libro, no en mono
            ImageDraw.Draw(img).text((M, alto_foto + 36), lam["pie_foto"], font=cursiva(26), fill=GRIS, anchor="ls")
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
        y = titular(capa, M, y, lam["titulo"], 84 * lam.get("escala", 1.0), ancho, color=CARBON, franja=SALVIA) + 22
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
        mt.franja(capa, [(M, y + 4, M + 5, y + h - 8)], BRASA, 9 + n)
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
    img = aa.campo(RECICLADO, 55 + n, clase="reciclado")
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
    fe, fv = cursiva(36), dn.sans(32, 600, 88)  # v3: los años en cursiva serif, no en mono
    col, alto_barra, paso = 110, 46, (70 if len(serie) <= 6 else 62)
    largo = ancho - col - 150
    for k, fila in enumerate(serie):
        etq, v = fila[0], fila[1]
        ultima = k == len(serie) - 1
        tono = tonos[grupos.index(fila[2]) % 2] if len(fila) > 2 and fila[2] in grupos else SALVIA
        w = max(6, largo * v / tope)
        cy = y + k * paso
        d.text((M, cy + alto_barra * 0.76), str(etq), font=fe, fill=GRIS, anchor="ls")
        mt.franja(img, [(M + col, cy, M + col + w, cy + alto_barra)], BRASA if ultima else tono, 31 + k)  # barras impresas
        d.text((M + col + w + 16, cy + alto_barra * 0.74), f"{v:,}".replace(",", "."), font=fv,
               fill=CARBON if ultima else GRIS, anchor="ls")
    y += paso * len(serie)
    if grupos:
        x = M + col
        for k, nombre in enumerate(grupos):
            mt.franja(img, [(x, y + 4, x + 22, y + 26)], tonos[k % 2], 51 + k)
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
    img = aa.campo(RECICLADO_HUESO, 20 + n, clase="reciclado")
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
        foto = foto.resize((an, alto), Image.LANCZOS)
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
    fa = dn.sans(24, 650, 100)
    x = M
    for k, palabra in enumerate(["COMENTA", "GUARDA", "COMPARTE"]):
        if k:
            x = espaciado(d, x + 8, y_pie + 32, "·", fa, PAPEL + (160,)) + 10
        x = espaciado(d, x, y_pie + 32, palabra, fa, BRASA if k == 0 else PAPEL)
    lg = dn.logo(64)
    img.alpha_composite(lg, (M, round(y_pie + 84)))
    d = ImageDraw.Draw(img)
    d.text((W - M - R, y_pie + 84 + 46), lam.get("cuenta", "@dialmedio"), font=dn.sans(30, 560, 96), fill=PAPEL, anchor="rs")
    d.text((M + lg.width + 24, y_pie + 84 + 46), "Sintonizar es conversar.", font=dn.serif(34), fill=BRASA, anchor="ls")
    return img


ESTILOS = {"portada": l_portada, "foto": l_foto, "ficha": l_ficha, "serie": l_serie, "citas": l_citas,
           "pais": l_lugar, "lugar": l_lugar, "paises": l_paises, "dos": l_dos, "cta": l_cta}


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
    estilo = estilo_de(lam)
    if estilo == "analisis":  # en esta línea, el análisis es una ficha (papel, sin carbón)
        estilo = "ficha"
    return ESTILOS[estilo](cfg, lam, n)


def capa_video(cfg, lam):
    lam = dict(lam, _video=True)
    return (l_portada if estilo_de(lam) == "portada" else l_foto)(cfg, lam, 0)
