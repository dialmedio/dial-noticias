"""Estilo visual de Tecnología y poder (v3, 24 oct 2026), la línea de política de la tecnología de Al Aire.

Martín pidió un diseño propio y minimalista, inspirado un poco en X, y en la 2.ª ronda una tipografía "más elegante e
impactante". La v2 (Geist, negro de pantalla y verde señal) cumplía, pero era la línea más digital de todas: Geist es
la letra de Vercel, la de las interfaces de IA; el negro puro con un acento neón, la mono, el cursor y la foto en
tarjeta redondeada son lenguaje de app. En la revisión de conjunto (24 oct) Martín pidió que todo se viera lo menos
digital posible y otro color: "el verde de tecnología no me mata".

v3: la misma página negra y minimalista, pero impresa.

- **Color: violeta de sello.** El de la tinta de los sellos oficiales (notarías, registradurías, juzgados): la marca
  con la que el poder certifica. Una tecnología vieja de autoridad para hablar de las nuevas. En la rueda de Dial
  completa lo que faltaba: brasa (Al Aire), eucalipto (Termómetro), azul cianotipo (Nuevos mundos), ámbar (Arte) y
  violeta (Tecnología). Plano, nunca en degradado; sobre negro va en su tono claro para que se lea.
- **Archivo** (Omnibus-Type, Buenos Aires, OFL), grotesca con eje de ancho: titulares en semibold apretado, cifras
  en Thin expandida (el contraste de peso y ancho da la elegancia), rótulos en versales semiexpandidas. Sin mono.
- **Negro de imprenta:** un negro cálido con la formación de la tinta (materia.py), no el #0A0A0A de una pantalla.
- **Fotos como planchas:** a todo el ancho y con esquinas rectas, en blanco y negro hecho con mezcla de canales
  (no con un filtro), después de la misma colorización de Dial. `"color": true` las deja a color.
- **Símbolo:** el aro de Dial con el punto violeta en la estación de la línea (45°).
- Numeración 1/7 abajo, como un hilo, en la misma Archivo. Nunca se dibuja una cita como si fuera una publicación de
  X de alguien real: las citas van como cita.

Se compone en HTML/CSS y lo renderiza Chrome (kerning real, text-wrap balance/pretty, comillas colgadas).
"""
import base64
import html
import io
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dial_noticias as dn  # noqa: E402
import al_aire as aa  # noqa: E402
import materia as mt  # noqa: E402

NOMBRE = "Tecnología y poder"
RAIZ = Path(__file__).resolve().parent
CHROME = next((p for p in (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
) if Path(p).exists()), "chrome")

NEGRO = (20, 18, 17)          # negro de imprenta, cálido como el carbón de Dial
VIOLETA = "#9A8CD6"           # violeta de sello, en su tono claro (sobre negro); la tinta plena es #5B3FC4
VIOLETA_PLENO = "#5B3FC4"
_cache = {}


def datos(ruta, mime):
    ruta = Path(ruta)
    if ruta not in _cache:
        _cache[ruta] = f"data:{mime};base64," + base64.b64encode(ruta.read_bytes()).decode()
    return _cache[ruta]


def png_uri(im, fmt="PNG", **kw):
    b = io.BytesIO()
    im.save(b, fmt, **kw)
    return f"data:image/{fmt.lower()};base64," + base64.b64encode(b.getvalue()).decode()


def logo_uri(alto):
    """El logo de Dial (con su terracota clara para fondo oscuro), al doble de resolución."""
    clave = ("logo", alto)
    if clave not in _cache:
        _cache[clave] = png_uri(dn.logo(alto * 2))
    return _cache[clave]


def aro_uri(tam, color=(237, 234, 228), punto=(154, 140, 214)):
    """El aro de Dial con el punto violeta en la estación de la línea, al doble de resolución."""
    clave = ("aro", tam)
    if clave not in _cache:
        im = Image.new("RGBA", (tam * 2, tam * 2), (0, 0, 0, 0))
        aa.aro(im, tam, tam, tam * 2, color, punto, aa.ESTACIONES["tecnologia"])
        _cache[clave] = png_uri(im)
    return _cache[clave]


def fondo_uri():
    """El negro de imprenta: la tinta con su formación, generado una vez por corrida."""
    clave = ("fondo", aa.W, aa.H)
    if clave not in _cache:
        rgb = mt.campo(aa.W, aa.H, NEGRO, 45, "tinta", fuerza=0.8)
        _cache[clave] = png_uri(Image.fromarray(np.clip(rgb + 0.5, 0, 255).astype(np.uint8)), "JPEG", quality=95)
    return _cache[clave]


def byn(im):
    """Blanco y negro de oficio: mezcla de canales con algo más de rojo (la piel y los rostros respiran), una curva
    suave en S y negros que no llegan a cero, para que la foto se asiente en el negro de la página."""
    a = np.asarray(im.convert("RGB"), np.float32) / 255
    L = a[..., 0] * 0.36 + a[..., 1] * 0.54 + a[..., 2] * 0.10
    L = np.clip((L - 0.5) * 1.12 + 0.5, 0, 1)
    L = L + 0.06 * np.sin(np.pi * L) * (L - 0.5) * 2  # S suave
    L = 0.035 + L * 0.94
    g = Image.fromarray((np.clip(L, 0, 1) * 255 + 0.5).astype(np.uint8))
    return g.convert("RGB")


def foto_uri(ruta, color=False, ajuste=None):
    """La foto con la colorización de Dial (la misma de todas las líneas) y, si no se pide color, en blanco y negro."""
    clave = ("foto", str(ruta), color)
    if clave not in _cache:
        im = dn.preparar_foto(ruta, ajuste)
        im.thumbnail((2000, 2000), Image.LANCZOS)
        if not color:
            im = byn(im)
        _cache[clave] = png_uri(im, "JPEG", quality=92)
    return _cache[clave]


def rico(texto):
    """Escapa el texto y pone el acento (*así*) en violeta; el espacio duro se respeta."""
    t = html.escape(texto or "")
    return re.sub(r"\*([^*]+)\*", r'<span class="ac">\1</span>', t)


CSS = """
@font-face{font-family:"Archivo";src:url(%(archivo)s);font-weight:100 900;font-stretch:62%% 125%%}
:root{--fondo:rgb(%(negro)s);--tinta:#EDEAE4;--gris:#A29D96;--gris-2:#77726C;--filete:rgba(237,234,228,.14);--violeta:%(violeta)s}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%(W)dpx;height:%(H)dpx;background:var(--fondo);overflow:hidden}
body{font-family:"Archivo",sans-serif;color:var(--tinta);-webkit-font-smoothing:antialiased;
  font-kerning:normal;font-feature-settings:"kern","liga","calt";text-rendering:geometricPrecision}
.lam{position:absolute;inset:0;padding:%(T)dpx %(Rd)dpx %(B)dpx 72px;display:flex;flex-direction:column;
  background:url(%(fondo)s) center/cover}
.ac{color:var(--violeta)}
.cab{position:relative;z-index:3;display:flex;justify-content:space-between;align-items:flex-start;height:84px;flex:none}
.cab .linea{display:flex;align-items:center;gap:13px;font-weight:600;font-size:28px;letter-spacing:-.012em;font-stretch:100%%}
.cab .linea img{width:28px;height:28px}
.cab .meta{font-size:17px;font-weight:600;letter-spacing:.14em;font-stretch:112%%;text-transform:uppercase;color:var(--gris);margin:11px 0 0 41px}
.cab .logo{height:38px;margin-top:-1px}
.cuerpo{position:relative;z-index:2;flex:1;display:flex;flex-direction:column;min-height:0}
.centro{justify-content:center;padding-bottom:56px}
.pie{position:relative;z-index:3;flex:none;height:40px;display:flex;justify-content:space-between;align-items:flex-end;gap:32px;
  font-size:18px;font-weight:400;letter-spacing:.005em;color:var(--gris-2)}
.pie .cred{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pie .num{color:var(--gris);font-weight:500;font-size:19px;letter-spacing:.02em;font-variant-numeric:tabular-nums;flex:none}
.sobre .pie,.sobre .pie .num{color:rgba(237,234,228,.82)}
.rot{font-size:19px;font-weight:620;letter-spacing:.15em;font-stretch:112%%;text-transform:uppercase;color:var(--violeta);margin-bottom:30px}
h1{font-weight:640;letter-spacing:-.032em;line-height:.98;text-wrap:balance;font-stretch:94%%}
h2{font-weight:620;letter-spacing:-.026em;line-height:1.02;text-wrap:balance;font-stretch:96%%}
p.baj{font-size:34px;line-height:1.3;letter-spacing:-.008em;color:var(--gris);font-weight:400;text-wrap:pretty;margin-top:26px;max-width:860px}
p.tx{font-size:36px;line-height:1.36;letter-spacing:-.008em;color:var(--gris);font-weight:400;text-wrap:pretty;margin-top:32px;max-width:860px}
p.tx.claro{color:var(--tinta)}
/* la foto como plancha: a todo el ancho, esquinas rectas */
.plancha{position:absolute;left:0;right:0;overflow:hidden;z-index:1;background:#2a2725}
.plancha img{position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover}
.plancha.abajo::after{content:"";position:absolute;left:0;right:0;bottom:0;height:200px;
  background:linear-gradient(to top,rgba(14,12,11,.72),rgba(14,12,11,0))}
.plancha.arriba::after{content:"";position:absolute;left:0;right:0;top:0;height:220px;
  background:linear-gradient(to bottom,rgba(14,12,11,.74),rgba(14,12,11,0))}
ol{list-style:none;margin-top:40px;border-top:1px solid var(--filete)}
ol li{display:grid;grid-template-columns:70px 1fr;padding:26px 0;border-bottom:1px solid var(--filete);
  font-size:36px;line-height:1.3;letter-spacing:-.01em;font-weight:420}
ol li span{text-wrap:pretty}
ol li b{font-weight:300;font-size:46px;line-height:.95;font-stretch:110%%;color:var(--violeta)}
.dato{font-weight:160;letter-spacing:-.045em;line-height:.84;font-stretch:125%%;font-variant-numeric:lining-nums;margin-left:-.05em;white-space:nowrap}
.unidad{font-size:46px;font-weight:600;letter-spacing:-.02em;color:var(--violeta);margin-top:30px;text-wrap:balance}
blockquote{position:relative;padding-left:0}
blockquote p{font-size:56px;font-weight:500;letter-spacing:-.024em;line-height:1.14;text-indent:-.42em;text-wrap:pretty}
blockquote p .q{color:var(--violeta)}
blockquote cite{display:block;font-style:normal;font-size:19px;font-weight:620;letter-spacing:.14em;font-stretch:112%%;
  text-transform:uppercase;color:var(--gris);margin-top:34px}
blockquote+blockquote{margin-top:72px}
.cierre{flex:none;border-top:1px solid var(--filete);padding-top:28px;display:flex;justify-content:space-between;align-items:flex-end}
.acciones{font-size:21px;font-weight:620;letter-spacing:.14em;font-stretch:112%%;text-transform:uppercase;display:flex;gap:18px;margin-bottom:24px}
.acciones span:first-child{color:var(--violeta)}
.acciones i{font-style:normal;color:var(--gris-2)}
.cierre .logo{height:46px;display:block}
.cuenta{font-size:26px;font-weight:500;letter-spacing:-.005em;color:var(--gris)}
"""


def pagina(cfg, lam, n, cuerpo, pie=True, clase=""):
    W, H = aa.W, aa.H
    total = len(cfg.get("laminas", [])) or n
    r, g_, b = NEGRO
    css = CSS % {"archivo": datos(RAIZ / "fuentes/Archivo-VF.ttf", "font/ttf"), "fondo": fondo_uri(),
                 "negro": f"{r},{g_},{b}", "violeta": cfg.get("_violeta", VIOLETA),
                 "W": W, "H": H, "T": max(aa.T, 62), "B": max(aa.B - 44, 52), "Rd": 72 + aa.R}
    meta = html.escape(lam.get("meta", cfg.get("meta", "")))
    cab = (f'<div class="cab"><div><div class="linea"><img src="{aro_uri(28)}" alt="">{NOMBRE}</div>'
           f'<div class="meta">{meta}</div></div><img class="logo" src="{logo_uri(38)}" alt=""></div>')
    abajo = ""
    if pie:
        cred = html.escape(aa.credito(lam))
        abajo = f'<div class="pie"><span class="cred">{cred}</span><span class="num">{n}/{total}</span></div>'
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{css}</style></head>'
            f'<body><div class="lam {clase}">{cab}{cuerpo}{abajo}</div></body></html>')


def plancha(cfg, lam, top, bottom, donde="abajo"):
    """La foto a todo el ancho entre `top` y `bottom` (px desde arriba y desde abajo)."""
    fx, fy = lam.get("foco", (0.5, 0.5))
    src = foto_uri(cfg["_base"] / lam["foto"], lam.get("color"), lam.get("ajuste"))
    return (f'<div class="plancha {donde}" style="top:{top}px;bottom:{bottom}px"><img src="{src}" '
            f'style="object-position:{fx * 100:.1f}% {fy * 100:.1f}%" alt=""></div>')


def rotulo(lam):
    return f'<div class="rot">{html.escape(lam["rotulo"])}</div>' if lam.get("rotulo") else ""


# ------------------------------------------------------------ láminas

def l_portada(cfg, lam, n):
    """Titular y bajada arriba, en la página negra; la foto, a todo el ancho hasta el borde de abajo."""
    tam = 94 * lam.get("escala", 1.0)
    c = f'<div class="cuerpo"><h1 style="font-size:{tam:.0f}px;margin-top:58px">{rico(lam["titulo"])}</h1>'
    if lam.get("bajada"):
        c += f'<p class="baj">{rico(lam["bajada"])}</p>'
    c += "</div>"
    if lam.get("foto"):
        c += plancha(cfg, lam, round(aa.H * lam.get("corte", 0.5)), 0)
        return pagina(cfg, lam, n, c, clase="sobre")
    return pagina(cfg, lam, n, c)


def l_foto(cfg, lam, n):
    """La foto a todo el ancho arriba (bajo la cabecera) y el texto debajo; "posicion": "arriba" invierte."""
    texto_ = rotulo(lam)
    if lam.get("titulo"):
        texto_ += f'<h2 style="font-size:62px">{rico(lam["titulo"])}</h2>'
    if lam.get("texto"):
        texto_ += f'<p class="tx claro" style="margin-top:20px">{rico(lam["texto"])}</p>'
    H = aa.H
    if lam.get("posicion") == "arriba":
        c = f'<div class="cuerpo"><div style="margin-top:40px">{texto_}</div></div>' + plancha(cfg, lam, round(H * 0.56), 0)
        return pagina(cfg, lam, n, c, clase="sobre")
    corte = round(H * lam.get("alto_foto", 0.55))
    c = plancha(cfg, lam, 0, H - corte, "arriba") + f'<div class="cuerpo" style="justify-content:flex-end"><div style="margin-bottom:34px">{texto_}</div></div>'
    return pagina(cfg, lam, n, c)


def l_post(cfg, lam, n):
    """La lámina de texto: una idea dicha en grande, como una publicación."""
    tam = 76 * lam.get("escala", 1.0)
    c = '<div class="cuerpo centro">' + rotulo(lam)
    if lam.get("titulo"):
        c += f'<h2 style="font-size:{tam:.0f}px">{rico(lam["titulo"])}</h2>'
    if lam.get("texto"):
        c += f'<p class="tx">{rico(lam["texto"])}</p>'
    if lam.get("items"):
        c += "<ol>" + "".join(f"<li><b>{k}</b><span>{rico(t)}</span></li>" for k, t in enumerate(lam["items"], 1)) + "</ol>"
    return pagina(cfg, lam, n, c + "</div>")


def l_dato(cfg, lam, n):
    """Una cifra enorme, fina y expandida, la unidad en violeta y la explicación debajo."""
    dato = str(lam["dato"])
    tam = lam.get("tam_dato") or min(300, int(1180 / max(len(dato), 3)))
    c = '<div class="cuerpo centro">' + rotulo(lam)
    c += f'<div class="dato" style="font-size:{tam}px">{html.escape(dato)}</div>'
    if lam.get("unidad"):
        c += f'<div class="unidad">{rico(lam["unidad"])}</div>'
    if lam.get("texto"):
        c += f'<p class="tx claro">{rico(lam["texto"])}</p>'
    return pagina(cfg, lam, n, c + "</div>")


def l_citas(cfg, lam, n):
    """La voz de una parte: la cita con las comillas colgadas en violeta y el autor en versales.
    No imita una publicación de X (sin avatar, usuario ni botones)."""
    c = '<div class="cuerpo centro">' + rotulo(lam)
    for cita in lam["citas"]:
        c += (f'<blockquote><p><span class="q">“</span>{rico(cita["texto"])}<span class="q">”</span></p>'
              f'<cite>{html.escape(cita["autor"])}</cite></blockquote>')
    return pagina(cfg, lam, n, c + "</div>")


def l_cta(cfg, lam, n):
    lam = dict(lam, meta=lam.get("rotulo") or "Conversemos")
    tam = 88 * lam.get("escala", 1.0)
    c = f'<div class="cuerpo centro"><h1 style="font-size:{tam:.0f}px">{rico(lam["pregunta"])}</h1>'
    if lam.get("texto"):
        c += f'<p class="tx">{rico(lam["texto"])}</p>'
    c += "</div>"
    c += ('<div class="cierre"><div><div class="acciones"><span>Comenta</span><i>·</i><span>Guarda</span><i>·</i><span>Comparte</span></div>'
          f'<img class="logo" src="{logo_uri(46)}" alt=""></div><div class="cuenta">{html.escape(lam.get("cuenta", "@dialmedio"))}</div></div>')
    return pagina(cfg, lam, n, c, pie=False)


ESTILOS = {"portada": l_portada, "foto": l_foto, "post": l_post, "dato": l_dato, "citas": l_citas, "cta": l_cta}


def estilo_de(lam):
    if lam.get("estilo"):
        return lam["estilo"]
    if lam.get("dato"):
        return "dato"
    e = aa.estilo_de(lam)
    return "post" if e in ("pais", "analisis") else e


def render(doc):
    """Renderiza el HTML con Chrome sin cabeza y devuelve la lámina como imagen."""
    tmp = Path(tempfile.mkdtemp(prefix="tec_"))
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
    raise NotImplementedError("Tecnología y poder todavía no tiene versión para video")
