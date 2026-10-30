"""Estilo visual de Nuevos mundos posibles (24 oct 2026), la línea de los viernes sobre salidas al modelo.

Martín pidió un diseño que fuera un diálogo entre el archivo, el solarpunk, lo minimalista y lo elegante de un medio
de talla internacional. La idea que lo amarra es el **cianotipo**: la impresión al sol con la que Anna Atkins hizo en
1843 el primer libro ilustrado con fotografías (de algas). Es archivo (planos, copias, herbarios), es sol y es
naturaleza, y no se parece a ninguna otra línea de Dial:

- Dos tintas sobre papel de archivo: azul cianotipo (la tinta) y oro de sol (el acento). Ninguna otra línea usa azul.
- Newsreader (Production Type, OFL), una serif hecha para periodismo, con tamaño óptico: fina y amplia en los
  titulares, cómoda en el texto. Instrument Sans espaciada para rótulos y créditos (v3: la mono solo queda en la
  signatura de la tarjeta de catálogo, que era escrita a máquina).
- El archivo está en la estructura: cada pieza es una ficha numerada (N.º), las fotos llevan pie como láminas de un
  libro, el crédito va en vertical al canto de la foto y la lámina `ficha` es la tarjeta de catálogo de la
  investigación (autor, obra, año, qué encontró), con su perforación abajo.
- El solarpunk está en la luz y en la materia: el oro de sol, el papel y la emulsión azul pintada a pincel. El símbolo es
  el aro de Dial (marca v4) en la estación de la línea: aro azul (papel sobre azul) con el punto de oro a las 10:30.
  Martín descartó el sol del primer borrador ("se ve como de juego indie").
- Texturas (24 oct, 2.ª ronda: "un poco más de arte"; v3 el mismo día: "se ve muy digital"): las láminas azules son
  un cianotipo a brocha sobre papel de archivo (cianotipo.py: pasadas que se montan, cerdas, pincel seco, diente del
  papel); el papel claro sale de materia.py, el sol de la cifra va impreso en oro y el aro del cierre es un fotograma.
  Ya no hay líneas de onda ni ruido SVG.
- Lo minimalista: retícula de 8 px, márgenes de 88 px, filetes de un pixel, nada de cajas ni franjas.
- `"tratamiento": "cianotipo"` en una foto la vuelve impresión al sol (para fotos de archivo, vestigios, planos);
  por defecto las fotos van a color, como las da la realidad.
- La lámina `balance` (lo que muestra / lo que falta) es el criterio de la línea hecho forma: resultados, críticas y
  límites en cada pieza. `"fondo": "cian"` invierte cualquier lámina de texto para dar ritmo.

Se compone en HTML/CSS y lo renderiza Chrome, como Tecnología y poder: kerning real, tamaños ópticos, cifras
de estilo antiguo, líneas equilibradas y comillas colgadas.
"""
import base64
import html
import io
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dial_noticias as dn  # noqa: E402
import al_aire as aa  # noqa: E402

NOMBRE = "Nuevos mundos posibles"
RAIZ = Path(__file__).resolve().parent
CHROME = next((p for p in (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
) if Path(p).exists()), "chrome")

PAPEL, TINTA, CIAN, CIAN_HONDO, SOL = "#F1EDE3", "#14243A", "#1F4A80", "#14335C", "#E7B043"
# extremos del cianotipo: la sombra en azul de Prusia y la luz en papel
SOMBRA_CIANO, LUZ_CIANO = (14, 38, 72), (236, 232, 220)

_cache = {}


def datos(ruta, mime):
    ruta = Path(ruta)
    if ruta not in _cache:
        _cache[ruta] = f"data:{mime};base64," + base64.b64encode(ruta.read_bytes()).decode()
    return _cache[ruta]


def png_uri(im):
    b = io.BytesIO()
    im.save(b, "PNG")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


def logo_uri(alto, oscuro):
    """El logo de Dial al doble de resolución: claro sobre azul; sobre papel, letras en tinta y la i en terracota."""
    clave = ("logo", alto, oscuro)
    if clave not in _cache:
        lg = dn.logo(alto * 2)
        if oscuro:
            a = np.asarray(lg).copy()
            claro = a[..., 0] > 200
            a[claro, :3] = (20, 36, 58)
            a[~claro & (a[..., 3] > 0), :3] = dn.TERRACOTA
            lg = Image.fromarray(a)
        _cache[clave] = png_uri(lg)
    return _cache[clave]


def cianotipo(im):
    """Impresión al sol: la luminancia, con el contraste ajustado, entre el azul de Prusia y el papel,
    con el moteado de la emulsión (cianotipo.py)."""
    import cianotipo as cia
    g = ImageOps.autocontrast(im.convert("L"), cutoff=1)
    mote = cia.ruido(g.width, g.height, max(g.width, g.height) / 5, semilla=7)
    t = np.clip((np.asarray(g).astype(np.float32) / 255.0) ** 0.92 + 0.07 * (mote - 0.5), 0, 1)
    s, luz = np.array(SOMBRA_CIANO, np.float32), np.array(LUZ_CIANO, np.float32)
    rgb = s + (luz - s) * t[..., None]
    return Image.fromarray(np.clip(rgb + 0.5, 0, 255).astype(np.uint8), "RGB")


def foto_uri(ruta, tratamiento=None):
    clave = ("foto", str(ruta), tratamiento)
    if clave not in _cache:
        if tratamiento == "cianotipo":
            im = ImageOps.exif_transpose(Image.open(ruta)).convert("RGB")
            im.thumbnail((2200, 2200), Image.LANCZOS)
            im = cianotipo(im)
        else:  # v3: la misma colorización de Dial que en todas las líneas
            im = dn.preparar_foto(ruta, None)
            im.thumbnail((2200, 2200), Image.LANCZOS)
        b = io.BytesIO()
        im.save(b, "JPEG", quality=92)
        _cache[clave] = "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
    return _cache[clave]


def rico(texto):
    """Escapa el texto y pone el acento (*así*) en cursiva; el espacio duro se respeta."""
    t = html.escape(texto or "")
    return re.sub(r"\*([^*]+)\*", r"<em>\1</em>", t)


ESTACION = -45  # la posición del punto de la línea en el dial de Dial (Dial madre a 45°). Solo en la mitad de arriba:
# abajo a la derecha el aro se lee como una Q
# El aro de la marca v4 (dial-web/src/lib/aro.mjs), en una caja de 200 × 200: radio, trazo, punto y respiro
ARO = dict(R=84, trazo=22.4, punto=24.9, aire=9.4)
_n_aro = [0]


def aro(tam=30, color=CIAN_HONDO, punto=SOL, angulo=ESTACION, extra=""):
    """El símbolo de la línea: el aro de Dial con el punto en la estación de Nuevos mundos."""
    _n_aro[0] += 1
    i = f"aro{_n_aro[0]}"
    rc = ARO["R"] - ARO["trazo"] / 2
    a = math.radians(angulo - 90)
    px, py = 100 + rc * math.cos(a), 100 + rc * math.sin(a)
    # v5: el aro de pluma (mismo trazo que al_aire.aro y dial-web/src/lib/aro.mjs)
    p, t = aa.PLUMA, ARO["trazo"] * aa.PLUMA["engrosa"]
    ext, inn = [], []
    for k in range(180):
        th = k * 2 * math.pi / 180
        q = t * (p["contraste"] + (1 - p["contraste"]) * abs(math.cos(th - math.radians(p["eje"]))) ** p["curva"])
        ext.append(f"{100 + (rc + q / 2) * math.cos(th):.2f},{100 + (rc + q / 2) * math.sin(th):.2f}")
        inn.append(f"{100 + (rc - q / 2) * math.cos(th):.2f},{100 + (rc - q / 2) * math.sin(th):.2f}")
    anillo = "M" + "L".join(ext) + "Z M" + "L".join(reversed(inn)) + "Z"
    return (f'<svg class="aro" width="{tam}" height="{tam}" viewBox="0 0 200 200" aria-hidden="true"{extra}>'
            f'<mask id="{i}" maskUnits="userSpaceOnUse" x="0" y="0" width="200" height="200"><rect width="200" height="200" fill="#fff"/>'
            f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{ARO["punto"] + ARO["aire"]}" fill="#000"/></mask>'
            f'<path d="{anillo}" fill="{color}" fill-rule="evenodd" mask="url(#{i})"/>'
            f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{ARO["punto"]}" fill="{punto}"/></svg>')


def textura_uri(clave, fabricar):
    """Las texturas de cianotipo se generan una vez por corrida (cianotipo.py) y van como WebP con alfa."""
    if clave not in _cache:
        b = io.BytesIO()
        fabricar().save(b, "WEBP", quality=88)
        _cache[clave] = "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode()
    return _cache[clave]


def emulsion(semilla=1):
    """La impresión al sol a pincel que cubre la lámina azul: el papel asoma en los bordes."""
    import cianotipo
    W, H = aa.W, aa.H
    return textura_uri(("emulsion", semilla, W, H), lambda: cianotipo.impresion(W, H, (16, 22, W - 16, H - 22), semilla))


def mascara_pincel(w=904, h=740, semilla=3):
    """La máscara de los bordes a pincel para las fotos en cianotipo (opaco = emulsión)."""
    import cianotipo

    def hacer():
        a = cianotipo.borde(w, h, (22, 22, w - 22, h - 22), semilla, cola=46)
        return Image.fromarray(np.dstack([np.full((h, w, 3), 255, np.uint8), (a * 255).astype(np.uint8)]), "RGBA")
    return textura_uri(("mascara", w, h, semilla), hacer)


def papel_uri():
    """El papel de archivo de la línea (v3, materia.py): formación, fibras y alguna mancha de óxido. Reemplaza el
    ruido SVG de la v2, que se veía como lo que era: un filtro de pantalla."""
    import materia
    W, H = aa.W, aa.H

    def hacer():
        rgb = materia.papel(W, H, (241, 237, 227), 21, "archivo")
        return Image.fromarray(np.clip(rgb + 0.5, 0, 255).astype(np.uint8))
    return textura_uri(("papel", W, H), hacer)


def _tinta_rgba(mascara, color, semilla):
    """Una mancha de tinta impresa (borde que se abre donde la fibra chupa, carga desigual) como RGBA."""
    import materia
    m = np.asarray(mascara, np.float32) / 255
    h, w = m.shape
    a = materia.mordido(m, semilla, 1.2) * materia.carga(w, h, semilla + 3, 1.4)
    rgb = np.zeros((h, w, 3), np.float32) + np.array(color, np.float32)
    return Image.fromarray(np.dstack([rgb, np.clip(a, 0, 1) * 255]).astype(np.uint8), "RGBA")


def sol_uri(diam):
    """El sol de la cifra, impreso en oro (v3): ya no es un círculo vectorial perfecto."""
    def hacer():
        s = 4
        m = Image.new("L", (diam * s, diam * s), 0)
        ImageDraw.Draw(m).ellipse([2, 2, diam * s - 2, diam * s - 2], fill=255)
        m = m.resize((diam, diam), Image.LANCZOS)
        return _tinta_rgba(m, (231, 176, 67), diam)
    return textura_uri(("sol", diam), hacer)


def fotograma_uri(tam):
    """El aro del cierre como fotograma: en un cianotipo, lo que tapa el sol deja el papel en blanco, con el borde
    blando donde el objeto no tocaba del todo el papel. El punto va en oro, impreso encima."""
    import materia

    def hacer():
        lado = tam
        mk = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
        aa.aro(mk, lado / 2, lado / 2, lado, (255, 255, 255), (0, 0, 0), ESTACION)
        a = np.asarray(mk, np.float32)
        anillo = (a[..., 3] / 255) * (a[..., 0] / 255)
        punto = (a[..., 3] / 255) * (1 - a[..., 0] / 255)
        blando = np.asarray(Image.fromarray((anillo * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.2)), np.float32) / 255
        velo = materia.ruido(lado, lado, 90, 5, 3)
        alfa = np.clip(blando * (0.93 + 0.07 * velo), 0, 1)  # algo de luz se coló: el blanco no es parejo
        rgb = np.zeros((lado, lado, 3), np.float32) + np.array((238, 234, 224), np.float32)
        out = Image.fromarray(np.dstack([rgb, alfa * 255]).astype(np.uint8), "RGBA")
        out.alpha_composite(_tinta_rgba(Image.fromarray((punto * 255).astype(np.uint8)), (231, 176, 67), 9))
        return out
    return textura_uri(("fotograma", tam), hacer)


CSS = """
@font-face{font-family:"News";src:url(%(news)s);font-weight:200 800;font-style:normal}
@font-face{font-family:"News";src:url(%(newsi)s);font-weight:200 800;font-style:italic}
@font-face{font-family:"ISans";src:url(%(sans)s);font-weight:400 700}
:root{--papel:%(papel)s;--tinta:%(tinta)s;--cian:%(cian)s;--sol:%(sol)s;--gris:#59647A;--filete:rgba(20,36,58,.2);--fondo:var(--papel)}
.cian{--fondo:var(--papel);--tinta:#F1EDE3;--cian:%(sol)s;--gris:rgba(241,237,227,.74);--filete:rgba(241,237,227,.26)}
.emulsion{position:absolute;inset:0;width:100%%;height:100%%;z-index:0;pointer-events:none}
.cian .cab,.cian .ficha,.cian .cuerpo,.cian .pie,.cian .cierre-pie{position:relative;z-index:2}
.placa.cianotipo{background:transparent;-webkit-mask-image:var(--pincel);mask-image:var(--pincel);-webkit-mask-size:100%% 100%%;mask-size:100%% 100%%}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%(W)dpx;height:%(H)dpx;overflow:hidden}
body{font-family:"News",serif;color:var(--tinta);-webkit-font-smoothing:antialiased;font-optical-sizing:auto;
  font-kerning:normal;font-feature-settings:"kern","liga","onum","pnum";text-rendering:geometricPrecision}
.lam{position:absolute;inset:0;background:var(--fondo);color:var(--tinta);padding:%(T)dpx %(Rd)dpx %(B)dpx 88px;
  display:flex;flex-direction:column}
.lam{background:var(--fondo) url(%(papel_img)s) center/cover}
em{font-style:italic;color:var(--cian)}
.cab{position:relative;display:flex;justify-content:space-between;align-items:center;height:44px;flex:none;z-index:2}
.marca{display:flex;align-items:center;gap:14px;font-style:italic;font-size:31px;font-weight:420;letter-spacing:-.008em;color:var(--tinta)}
.cab img{height:36px}
.cab .aro{flex:none}
.ficha{position:relative;z-index:2;flex:none;margin-top:20px;padding-top:14px;border-top:1px solid var(--filete);
  display:flex;justify-content:space-between;align-items:baseline;gap:24px}
.mono{font-family:"ISans",sans-serif;font-weight:600;font-size:16px;letter-spacing:.13em;text-transform:uppercase;color:var(--gris);
  font-feature-settings:"tnum"}
.fig{font-family:"News",serif;font-style:italic;font-weight:400;font-size:24px;letter-spacing:0;text-transform:none;color:var(--gris)}
.maquina{font-family:"ISans",sans-serif;font-weight:600;font-size:15px;letter-spacing:.13em;text-transform:uppercase}
.meta{font-family:"ISans",sans-serif;font-weight:600;font-size:17px;letter-spacing:.17em;text-transform:uppercase;color:var(--tinta);
  flex:1;padding-left:4px}
.cuerpo{position:relative;z-index:2;flex:1;display:flex;flex-direction:column;min-height:0}
.centro{justify-content:center;padding-bottom:40px}
.pie{position:relative;z-index:2;flex:none;border-top:1px solid var(--filete);padding-top:14px;
  display:flex;justify-content:space-between;gap:32px;align-items:baseline}
.pie .mono{font-size:17px;font-weight:450;letter-spacing:.005em;text-transform:none;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pie .fig{font-size:22px}
.rot{font-family:"ISans",sans-serif;font-weight:600;font-size:18px;letter-spacing:.17em;text-transform:uppercase;color:var(--cian);
  display:flex;align-items:center;gap:14px;margin-bottom:30px}
.rot::before{content:"";width:12px;height:12px;border-radius:50%%;background:var(--sol);flex:none}
h1{font-weight:330;letter-spacing:-.022em;line-height:1.02;text-wrap:balance}
h2{font-weight:360;letter-spacing:-.018em;line-height:1.08;text-wrap:balance}
h1 em,h2 em{font-weight:340}
p.baj{font-size:31px;line-height:1.34;color:var(--gris);font-weight:400;text-wrap:pretty;margin-top:22px;max-width:820px}
p.tx{font-size:35px;line-height:1.4;font-weight:380;text-wrap:pretty;margin-top:30px;max-width:860px}
p.tx.gris{color:var(--gris)}
/* portada: la foto a sangre arriba y el titular en papel */
.por-foto{position:absolute;left:0;right:0;top:0;height:%(HF)dpx;overflow:hidden;z-index:1}
.por-foto img{width:100%%;height:100%%;object-fit:cover;display:block}
.por-foto::after{content:"";position:absolute;inset:0;background:linear-gradient(to bottom,rgba(10,20,34,.42),rgba(10,20,34,0) 19%%)}
.portada .cab .marca{color:#F1EDE3}
.vertical{position:absolute;z-index:3;right:22px;writing-mode:vertical-rl;transform:rotate(180deg);
  font-family:"ISans",sans-serif;font-size:15px;font-weight:450;letter-spacing:.01em;color:rgba(241,237,227,.92);white-space:nowrap;
  text-shadow:0 0 6px rgba(10,20,34,.45)}
.por-texto{position:absolute;z-index:2;left:88px;right:%(Rd)dpx;top:%(HF)dpx;bottom:%(B)dpx;display:flex;flex-direction:column}
.por-texto .titulares{flex:1;display:flex;flex-direction:column;justify-content:center;padding:24px 0 12px}
/* foto con pie de lámina, como en un libro */
.placa{position:relative;flex:1;min-height:0;margin-top:44px;overflow:hidden;background:#d9d3c4}
.placa img{position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover}
.leyenda{display:grid;grid-template-columns:120px 1fr;gap:0 24px;margin:30px 0 34px}
.leyenda .num{font-family:"News",serif;font-style:italic;font-size:27px;color:var(--gris);padding-top:6px}
.leyenda h2{font-size:52px}
.leyenda p.tx{font-size:31px;margin-top:14px;color:var(--gris)}
/* listas numeradas con cifras de estilo antiguo en cursiva */
ol{list-style:none;margin-top:40px;border-top:1px solid var(--filete)}
ol li{display:grid;grid-template-columns:64px 1fr;padding:24px 0;border-bottom:1px solid var(--filete);font-size:34px;line-height:1.32;font-weight:380}
ol li span{text-wrap:pretty}
ol li b{font-style:italic;font-weight:400;font-size:40px;line-height:1.1;color:var(--cian)}
/* el dato: la cifra fina sobre un sol */
.dato-caja{position:relative;align-self:flex-start;margin-left:-6px}
.dato-caja .sol{position:absolute;width:var(--r);height:var(--r);left:calc(var(--r) * -0.18);top:calc(var(--r) * -0.12)}
.dato{position:relative;font-weight:220;letter-spacing:-.045em;line-height:.9;white-space:nowrap;font-feature-settings:"lnum","tnum"}
.unidad{font-style:italic;font-size:48px;font-weight:380;letter-spacing:-.01em;color:var(--cian);margin-top:34px;text-wrap:balance}
/* la ficha de catálogo */
.tarjeta{position:relative;margin-top:8px;background:#FBF9F3;color:#14243A;border:1px solid rgba(20,36,58,.16);
  box-shadow:0 1px 0 rgba(20,36,58,.05),0 22px 40px -28px rgba(20,36,58,.45);padding:36px 44px 64px}
.tarjeta .tope{display:flex;justify-content:space-between;align-items:baseline;border-bottom:2px solid %(cian)s;padding-bottom:16px}
.tarjeta .tope .mono{color:#59647A}
.tarjeta .tope b{font-family:"ISans";font-weight:600;font-size:17px;letter-spacing:.17em;text-transform:uppercase;color:%(cian)s}
.tarjeta dl{display:grid;grid-template-columns:190px 1fr;margin-top:6px}
.tarjeta dt,.tarjeta dd{padding:17px 0;border-bottom:1px solid rgba(31,74,128,.16)}
.tarjeta dt{font-family:"ISans";font-weight:600;font-size:16px;letter-spacing:.15em;text-transform:uppercase;color:#59647A;padding-top:24px}
.tarjeta dd{font-size:33px;line-height:1.28;font-weight:400;text-wrap:pretty}
.tarjeta dd em{color:%(cian)s}
.tarjeta .agujero{position:absolute;left:50%%;bottom:22px;width:22px;height:22px;margin-left:-11px;border-radius:50%%;
  background:var(--fondo);box-shadow:inset 0 1px 2px rgba(20,36,58,.35)}
/* balance: lo que muestra y lo que falta */
.balance{display:grid;grid-template-columns:1fr 1fr;gap:0 48px;margin-top:44px}
.balance h3{font-family:"ISans";font-weight:600;font-size:19px;letter-spacing:.17em;text-transform:uppercase;
  display:flex;align-items:center;gap:12px;padding-bottom:18px;border-bottom:2px solid var(--tinta)}
.balance h3::before{content:"";width:14px;height:14px;border-radius:50%%;flex:none}
.balance .si h3::before{background:var(--sol)}
.balance .no h3::before{border:2px solid var(--tinta)}
.balance li{list-style:none;padding:24px 0;border-bottom:1px solid var(--filete);font-size:33px;line-height:1.3;font-weight:380;text-wrap:pretty}
/* citas */
blockquote{position:relative;padding-left:0}
blockquote p{font-style:italic;font-size:54px;font-weight:340;letter-spacing:-.012em;line-height:1.16;text-indent:-.42em;text-wrap:pretty}
blockquote p::first-letter{color:var(--cian)}
blockquote cite{display:flex;gap:14px;align-items:center;font-style:normal;font-family:"ISans";font-weight:600;font-size:18px;letter-spacing:.15em;
  text-transform:uppercase;color:var(--gris);margin-top:34px}
blockquote cite::before{content:"";width:40px;height:1px;background:var(--gris)}
blockquote+blockquote{margin-top:70px}
/* cierre: el aro como fotograma (la forma que tapó el sol y dejó el papel en blanco) */
.fotograma{position:absolute;z-index:1}
.cierre-pie{position:relative;z-index:2;flex:none;display:flex;justify-content:space-between;align-items:flex-end}
.acciones{font-family:"ISans";font-weight:600;font-size:19px;letter-spacing:.17em;text-transform:uppercase;display:flex;gap:30px;margin-bottom:20px}
.acciones span:first-child{color:var(--sol)}
.cierre-pie img{height:44px;display:block}
"""


def css(cian=False):
    W, H = aa.W, aa.H
    return CSS % {"news": datos(RAIZ / "fuentes/Newsreader-VF.ttf", "font/ttf"),
                  "newsi": datos(RAIZ / "fuentes/Newsreader-Italic-VF.ttf", "font/ttf"),
                  "sans": datos(RAIZ / "fuentes/InstrumentSans-VF.ttf", "font/ttf"),
                  "papel": PAPEL, "papel_img": papel_uri(), "tinta": TINTA, "cian": CIAN, "hondo": CIAN_HONDO, "sol": SOL,
                  "W": W, "H": H, "T": max(aa.T, 56), "B": max(aa.B - 58, 52), "Rd": 88 + aa.R,
                  "HF": round(H * 0.6), "HO": H - 420}


def cabecera(oscuro):
    simbolo = aro(32) if oscuro else aro(32, color=PAPEL)
    return (f'<div class="cab"><div class="marca">{simbolo}{NOMBRE}</div>'
            f'<img src="{logo_uri(36, oscuro)}" alt=""></div>')


def tira(cfg, lam, n):
    """La tira de catálogo bajo la cabecera: número de ficha, tema y lugar, y la lámina."""
    total = len(cfg.get("laminas", [])) or n
    num = cfg.get("ficha")
    izq = f'<span class="mono">Ficha N.º {html.escape(str(num))}</span>' if num else ""
    meta = html.escape(lam.get("meta", cfg.get("meta", "")))
    return (f'<div class="ficha">{izq}<span class="meta">{meta}</span>'
            f'<span class="fig">{n} / {total}</span></div>')


def pie(lam):
    cred = lam.get("fuentes") or lam.get("credito") or ""
    if not cred or not dn.PIE:  # v5: créditos y fuentes van en la descripción
        return ""
    return f'<div class="pie"><span class="mono">{html.escape(cred)}</span></div>'


def pagina(cfg, lam, n, cuerpo, clase="", con_pie=True):
    cian = lam.get("fondo") == "cian" or "cian" in clase
    clase = (clase + (" cian" if cian and "cian" not in clase else "")).strip()
    abajo = pie(lam) if con_pie else ""
    fondo = f'<img class="emulsion" src="{emulsion(n)}" alt="">' if cian else ""
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{css()}</style></head>'
            f'<body><div class="lam {clase}">{fondo}{cabecera(not cian)}{tira(cfg, lam, n)}{cuerpo}{abajo}</div></body></html>')


def rotulo(lam):
    return f'<div class="rot">{html.escape(lam["rotulo"])}</div>' if lam.get("rotulo") else ""


def img_foto(cfg, lam):
    fx, fy = lam.get("foco", (0.5, 0.5))
    uri = foto_uri(cfg["_base"] / lam["foto"], lam.get("tratamiento"))
    return f'<img src="{uri}" style="object-position:{fx * 100:.1f}% {fy * 100:.1f}%" alt="">'


def vertical(texto, donde):
    """El crédito en vertical al canto derecho de la foto, de abajo hacia arriba, como en los libros."""
    return f'<div class="vertical" style="{donde}px">{html.escape(texto)}</div>' if texto and dn.PIE else ""  # v5: créditos en la descripción


# ------------------------------------------------------------ láminas

def l_portada(cfg, lam, n):
    """La foto a sangre en la parte de arriba y el titular en papel."""
    total = len(cfg.get("laminas", [])) or n
    largo = len(re.sub(r"[*]", "", lam["titulo"]))
    tam = (108 if largo <= 24 else 92 if largo <= 40 else 78) * lam.get("escala", 1.0)
    num = cfg.get("ficha")
    meta = html.escape(lam.get("meta", cfg.get("meta", "")))
    texto = f'<div class="titulares"><h1 style="font-size:{tam:.0f}px">{rico(lam["titulo"])}</h1>'
    if lam.get("bajada"):
        texto += f'<p class="baj">{rico(lam["bajada"])}</p>'
    texto += "</div>"
    izq = f'Ficha N.º {html.escape(str(num))} · ' if num else ""
    texto += (f'<div class="pie"><span class="mono" style="text-transform:uppercase;letter-spacing:.13em;font-weight:600;font-size:16px">{izq}{meta}</span>'
              f'<span class="fig">{n} / {total}</span></div>')
    foto = f'<div class="por-foto">{img_foto(cfg, lam)}</div>' if lam.get("foto") else ""
    cuerpo = (f'{foto}{vertical(lam.get("credito", ""), "bottom:" + str(aa.H - round(aa.H * 0.6) + 22))}'
              f'<div class="por-texto">{texto}</div>')
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{css()}</style></head>'
            f'<body><div class="lam portada">{cabecera(False)}{cuerpo}</div></body></html>')


def l_foto(cfg, lam, n):
    """La foto como lámina de libro: placa a todo el ancho y debajo su pie (rótulo, título y texto)."""
    ley = rotulo(lam)
    if lam.get("titulo"):
        ley += f'<h2>{rico(lam["titulo"])}</h2>'
    if lam.get("texto"):
        ley += f'<p class="tx">{rico(lam["texto"])}</p>'
    num = f'Lám. {n}'
    placa = ('<div class="placa cianotipo" style="--pincel:url(' + mascara_pincel(semilla=n) + ')">'
             if lam.get("tratamiento") == "cianotipo" else '<div class="placa">')
    cuerpo = (f'<div class="cuerpo">{placa}{img_foto(cfg, lam)}{vertical(lam.get("credito", ""), "bottom:16")}</div>'
              f'<div class="leyenda"><div class="num">{num}</div><div>{ley}</div></div></div>')
    lam = dict(lam, credito="", fuentes=lam.get("fuentes"))
    return pagina(cfg, lam, n, cuerpo)


def l_post(cfg, lam, n):
    """Una idea dicha en grande; con `items`, una lista numerada en cursiva."""
    tam = 78 * lam.get("escala", 1.0)
    c = '<div class="cuerpo centro">' + rotulo(lam)
    if lam.get("titulo"):
        c += f'<h2 style="font-size:{tam:.0f}px">{rico(lam["titulo"])}</h2>'
    if lam.get("texto"):
        c += f'<p class="tx gris">{rico(lam["texto"])}</p>'
    if lam.get("items"):
        c += "<ol>" + "".join(f"<li><b>{k}</b><span>{rico(t)}</span></li>" for k, t in enumerate(lam["items"], 1)) + "</ol>"
    return pagina(cfg, lam, n, c + "</div>")


def l_dato(cfg, lam, n):
    """La cifra enorme y fina sobre un sol; la unidad en cursiva y la explicación debajo."""
    dato = str(lam["dato"])
    tam = lam.get("tam_dato") or min(330, int(1250 / max(len(dato), 3)))
    c = '<div class="cuerpo centro">' + rotulo(lam)
    sol = f'<img class="sol" src="{sol_uri(round(tam * 0.9))}" alt="">'  # v3: el sol impreso, sin las ondas
    c += (f'<div class="dato-caja" style="--r:{tam * 0.9:.0f}px;margin-top:{tam * 0.1:.0f}px">{sol}'
          f'<div class="dato" style="font-size:{tam}px">{html.escape(dato)}</div></div>')
    if lam.get("unidad"):
        c += f'<div class="unidad">{rico(lam["unidad"])}</div>'
    if lam.get("texto"):
        c += f'<p class="tx">{rico(lam["texto"])}</p>'
    return pagina(cfg, lam, n, c + "</div>")


def l_ficha(cfg, lam, n):
    """La tarjeta de catálogo de la investigación, el libro o la experiencia: `campos` es una lista de
    [etiqueta, valor]; `titulo` va arriba y `texto` debajo de la tarjeta."""
    c = '<div class="cuerpo centro">' + rotulo(lam)
    if lam.get("titulo"):
        c += f'<h2 style="font-size:{56 * lam.get("escala", 1.0):.0f}px;margin-bottom:40px">{rico(lam["titulo"])}</h2>'
    filas = "".join(f"<dt>{html.escape(k)}</dt><dd>{rico(v)}</dd>" for k, v in lam["campos"])
    tope = html.escape(lam.get("tipo_ficha", "Ficha de investigación"))
    der = html.escape(lam.get("signatura", ""))
    c += (f'<div class="tarjeta"><div class="tope"><b>{tope}</b><span class="maquina">{der}</span></div>'
          f'<dl>{filas}</dl><div class="agujero"></div></div>')
    if lam.get("texto"):
        c += f'<p class="tx gris" style="margin-top:36px">{rico(lam["texto"])}</p>'
    return pagina(cfg, lam, n, c + "</div>")


def l_balance(cfg, lam, n):
    """Lo que muestra y lo que falta, lado a lado. `columnas`: [[título, [puntos…]], [título, [puntos…]]]."""
    c = '<div class="cuerpo centro">' + rotulo(lam)
    if lam.get("titulo"):
        c += f'<h2 style="font-size:{68 * lam.get("escala", 1.0):.0f}px">{rico(lam["titulo"])}</h2>'
    cols = ""
    for (titulo, puntos), clase in zip(lam["columnas"], ("si", "no")):
        cols += (f'<div class="{clase}"><h3>{html.escape(titulo)}</h3><ul>'
                 + "".join(f"<li>{rico(p)}</li>" for p in puntos) + "</ul></div>")
    c += f'<div class="balance">{cols}</div>'
    if lam.get("texto"):
        c += f'<p class="tx gris" style="margin-top:36px">{rico(lam["texto"])}</p>'
    return pagina(cfg, lam, n, c + "</div>")


def l_citas(cfg, lam, n):
    """La voz: cursiva grande con la comilla colgada en azul (en oro sobre fondo cian); el autor en versalitas."""
    c = '<div class="cuerpo centro">' + rotulo(lam)
    for cita in lam["citas"]:
        c += (f'<blockquote><p>“{rico(cita["texto"])}”</p>'
              f'<cite>{html.escape(cita["autor"])}</cite></blockquote>')
    return pagina(cfg, lam, n, c + "</div>")


def orbitas():
    """El cierre: el aro de la línea en grande, como fotograma sobre la impresión al sol (v3: sin las líneas de onda,
    que se veían como un radar de pantalla)."""
    return (f'<img class="fotograma" src="{fotograma_uri(420)}" alt="" '
            f'style="left:calc(64% - 210px);top:{aa.H - 640}px;width:420px;height:420px">')


def l_cta(cfg, lam, n):
    lam = dict(lam, meta=lam.get("rotulo") or "Conversemos")
    tam = 80 * lam.get("escala", 1.0)
    c = (f'{orbitas()}<div class="cuerpo" style="justify-content:flex-start;padding-top:96px">'
         f'<h1 style="font-size:{tam:.0f}px">{rico(lam["pregunta"])}</h1>')
    if lam.get("texto"):
        c += f'<p class="tx gris" style="margin-top:28px">{rico(lam["texto"])}</p>'
    c += "</div>"
    c += ('<div class="cierre-pie"><div><div class="acciones"><span>Comenta</span><span>Guarda</span><span>Comparte</span></div>'
          f'<img src="{logo_uri(44, False)}" alt=""></div>'
          f'<span style="font-family:ISans;font-size:26px;font-weight:500;color:rgba(241,237,227,.85)">{html.escape(lam.get("cuenta", "@dialmedio"))}</span></div>')
    return pagina(cfg, lam, n, c, clase="cian", con_pie=False)


ESTILOS = {"portada": l_portada, "foto": l_foto, "post": l_post, "dato": l_dato, "ficha": l_ficha,
           "balance": l_balance, "citas": l_citas, "cta": l_cta}


def estilo_de(lam):
    if lam.get("estilo"):
        return lam["estilo"]
    if lam.get("campos"):
        return "ficha"
    if lam.get("columnas"):
        return "balance"
    if lam.get("dato"):
        return "dato"
    e = aa.estilo_de(lam)
    return "post" if e in ("pais", "analisis") else e


def render(doc):
    """Renderiza el HTML con Chrome sin cabeza y devuelve la lámina como imagen."""
    tmp = Path(tempfile.mkdtemp(prefix="mundos_"))
    h, png = tmp / "l.html", tmp / "l.png"
    h.write_text(doc, encoding="utf-8")
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
           f"--window-size={aa.W},{aa.H}", f"--user-data-dir={tmp / 'perfil'}", "--virtual-time-budget=4000",
           f"--screenshot={png}", h.as_uri()]
    subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    if not png.exists():
        raise RuntimeError("Chrome no generó la lámina (¿está instalado?)")
    return Image.open(png).convert("RGBA")


def lamina(cfg, lam, n):
    return render(ESTILOS[estilo_de(lam)](cfg, lam, n))


def capa_video(cfg, lam):
    raise NotImplementedError("Nuevos mundos posibles todavía no tiene versión para video")
