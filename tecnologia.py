"""Estilo visual de Tecnología y poder (25 oct 2026), la línea de política de la tecnología de Al Aire.

Martín pidió un diseño propio y minimalista, inspirado un poco en X, para que cada sección tenga su plantilla y el
perfil gane diversidad. En la 2.ª ronda pidió una tipografía "más elegante e impactante", hecha como la haría un
diseñador profesional. Por eso esta línea no se dibuja con Pillow sino que se compone en HTML/CSS y la renderiza
Chrome (como el Expediente): así hay kerning real, interletra negativa en los titulares, líneas equilibradas
(text-wrap: balance), cifras tabulares y comillas colgadas.

- Geist y Geist Mono (Vercel, OFL): grotesca precisa, hecha para pantalla, con su mono a juego.
- Fondo casi negro, texto casi blanco, gris para lo secundario y un solo acento, verde señal (*así*).
- Escala tipográfica corta (96 / 76 / 36 / 18) sobre una retícula de 8 px, márgenes de 80 px.
- Cifras grandes en Geist ExtraLight: el contraste de peso con los titulares en SemiBold da la elegancia.
- La foto va en una tarjeta redondeada, en blanco y negro con contraste (`"color": true` la deja a color).
- Numeración 01 / 07 abajo, como un hilo. El símbolo de la línea es el cursor (un bloque verde).
- Nunca se dibuja una cita como si fuera una publicación de X de alguien real: las citas van como cita.
"""
import base64
import html
import io
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dial_noticias as dn  # noqa: E402
import al_aire as aa  # noqa: E402

NOMBRE = "Tecnología y poder"
RAIZ = Path(__file__).resolve().parent
CHROME = next((p for p in (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
) if Path(p).exists()), "chrome")

_cache = {}


def datos(ruta, mime):
    ruta = Path(ruta)
    if ruta not in _cache:
        _cache[ruta] = f"data:{mime};base64," + base64.b64encode(ruta.read_bytes()).decode()
    return _cache[ruta]


def logo_uri(alto):
    """El logo de Dial (con su terracota clara para fondo oscuro), al doble de resolución."""
    clave = ("logo", alto)
    if clave not in _cache:
        b = io.BytesIO()
        dn.logo(alto * 2).save(b, "PNG")
        _cache[clave] = "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
    return _cache[clave]


def foto_uri(ruta):
    """La foto, a un tamaño razonable para la tarjeta (la tarjeta mide como mucho 920 px de ancho)."""
    clave = ("foto", str(ruta))
    if clave not in _cache:
        im = Image.open(ruta).convert("RGB")
        im.thumbnail((2000, 2000), Image.LANCZOS)
        b = io.BytesIO()
        im.save(b, "JPEG", quality=92)
        _cache[clave] = "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
    return _cache[clave]


def rico(texto):
    """Escapa el texto y pone el acento (*así*) en verde señal; el espacio duro se respeta."""
    t = html.escape(texto or "")
    return re.sub(r"\*([^*]+)\*", r'<span class="ac">\1</span>', t)


CSS = """
@font-face{font-family:"Geist";src:url(%(geist)s);font-weight:100 900}
@font-face{font-family:"GeistMono";src:url(%(mono)s);font-weight:100 900}
:root{--fondo:#0A0A0A;--tinta:#EDEDEC;--gris:#8F8F92;--gris-2:#5E5E62;--filete:rgba(255,255,255,.11);--senal:#C8F546}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%(W)dpx;height:%(H)dpx;background:var(--fondo);overflow:hidden}
body{font-family:"Geist",sans-serif;color:var(--tinta);-webkit-font-smoothing:antialiased;
  font-kerning:normal;font-feature-settings:"kern","liga","calt";text-rendering:geometricPrecision}
.lam{position:absolute;inset:0;padding:%(T)dpx %(Rd)dpx %(B)dpx 80px;display:flex;flex-direction:column}
.ac{color:var(--senal)}
.cab{display:flex;justify-content:space-between;align-items:flex-start;height:84px;flex:none}
.cab .linea{display:flex;align-items:center;gap:14px;font-weight:560;font-size:27px;letter-spacing:-.018em}
.cursor{display:inline-block;width:13px;height:26px;background:var(--senal)}
.cab .meta{font-family:"GeistMono";font-size:19px;font-weight:450;letter-spacing:.09em;text-transform:uppercase;color:var(--gris);margin:10px 0 0 27px}
.cab img{height:38px;margin-top:-2px}
.cuerpo{flex:1;display:flex;flex-direction:column;min-height:0}
.centro{justify-content:center;padding-bottom:56px}
.pie{flex:none;height:40px;display:flex;justify-content:space-between;align-items:flex-end;gap:32px;
  font-family:"GeistMono";font-size:17px;font-weight:450;letter-spacing:.04em;text-transform:uppercase;color:var(--gris-2)}
.pie .cred{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;letter-spacing:.01em}
.pie .num{color:var(--gris);font-size:19px;letter-spacing:.08em;font-variant-numeric:tabular-nums;flex:none}
.rot{font-family:"GeistMono";font-size:21px;font-weight:500;letter-spacing:.12em;text-transform:uppercase;color:var(--gris);
  display:flex;align-items:center;gap:14px;margin-bottom:32px}
.rot::before{content:"";width:24px;height:3px;background:var(--senal)}
h1{font-weight:620;letter-spacing:-.047em;line-height:.98;text-wrap:balance}
h2{font-weight:600;letter-spacing:-.04em;line-height:1.02;text-wrap:balance}
p.baj{font-size:34px;line-height:1.3;letter-spacing:-.012em;color:var(--gris);font-weight:420;text-wrap:pretty;margin-top:24px;max-width:860px}
p.tx{font-size:36px;line-height:1.36;letter-spacing:-.014em;color:var(--gris);font-weight:420;text-wrap:pretty;margin-top:32px;max-width:860px}
p.tx.claro{color:var(--tinta)}
.tarjeta{flex:1;min-height:0;border-radius:28px;overflow:hidden;position:relative;margin-top:48px;margin-bottom:28px;
  box-shadow:0 0 0 1px var(--filete) inset}
.tarjeta img{position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover}
.bn img{filter:grayscale(1) contrast(1.16) brightness(.96)}
.tarjeta::after{content:"";position:absolute;inset:0;border-radius:28px;box-shadow:0 0 0 1px var(--filete) inset}
ol{list-style:none;margin-top:40px;border-top:1px solid var(--filete)}
ol li{display:grid;grid-template-columns:72px 1fr;padding:26px 0;border-bottom:1px solid var(--filete);
  font-size:36px;line-height:1.3;letter-spacing:-.016em;font-weight:440}
ol li span{text-wrap:pretty}
ol li b{font-family:"GeistMono";font-weight:500;font-size:22px;letter-spacing:.04em;color:var(--senal);padding-top:9px}
.dato{font-weight:200;letter-spacing:-.065em;line-height:.84;font-variant-numeric:tabular-nums lining-nums;margin-left:-.06em;white-space:nowrap}
.unidad{font-size:44px;font-weight:560;letter-spacing:-.03em;color:var(--senal);margin-top:28px}
blockquote{border-left:4px solid var(--senal);padding-left:40px}
blockquote p{font-size:54px;font-weight:500;letter-spacing:-.034em;line-height:1.14;text-indent:-.4em;text-wrap:pretty}
blockquote cite{display:block;font-style:normal;font-family:"GeistMono";font-size:18px;font-weight:500;letter-spacing:.1em;
  text-transform:uppercase;color:var(--gris);margin-top:32px;font-size:20px}
blockquote+blockquote{margin-top:72px}
.cierre{flex:none;border-top:1px solid var(--filete);padding-top:28px;display:flex;justify-content:space-between;align-items:flex-end}
.acciones{font-family:"GeistMono";font-size:21px;font-weight:500;letter-spacing:.12em;text-transform:uppercase;display:flex;gap:28px;margin-bottom:22px}
.acciones span:first-child{color:var(--senal)}
.cierre img{height:44px;display:block}
.cuenta{font-family:"GeistMono";font-size:22px;font-weight:450;letter-spacing:.04em;color:var(--gris)}
"""


def pagina(cfg, lam, n, cuerpo, pie=True):
    W, H = aa.W, aa.H
    total = len(cfg.get("laminas", [])) or n
    css = CSS % {"geist": datos(RAIZ / "fuentes/Geist-VF.ttf", "font/ttf"),
                 "mono": datos(RAIZ / "fuentes/GeistMono-VF.ttf", "font/ttf"),
                 "W": W, "H": H, "T": max(aa.T, 64), "B": max(aa.B - 40, 56), "Rd": 80 + aa.R}
    meta = html.escape(lam.get("meta", cfg.get("meta", "")))
    cab = (f'<div class="cab"><div><div class="linea"><span class="cursor"></span>{NOMBRE}</div>'
           f'<div class="meta">{meta}</div></div><img src="{logo_uri(38)}" alt=""></div>')
    abajo = ""
    if pie:
        cred = html.escape(aa.credito(lam))
        abajo = f'<div class="pie"><span class="cred">{cred}</span><span class="num">{n:02d} / {total:02d}</span></div>'
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{css}</style></head>'
            f'<body><div class="lam">{cab}{cuerpo}{abajo}</div></body></html>')


def tarjeta(cfg, lam):
    fx, fy = lam.get("foco", (0.5, 0.5))
    clase = "tarjeta" if lam.get("color") else "tarjeta bn"
    return (f'<div class="{clase}"><img src="{foto_uri(cfg["_base"] / lam["foto"])}" '
            f'style="object-position:{fx * 100:.1f}% {fy * 100:.1f}%" alt=""></div>')


def rotulo(lam):
    return f'<div class="rot">{html.escape(lam["rotulo"])}</div>' if lam.get("rotulo") else ""


# ------------------------------------------------------------ láminas

def l_portada(cfg, lam, n):
    """Como una publicación: titular, bajada y, debajo, la foto en tarjeta."""
    tam = 96 * lam.get("escala", 1.0)
    c = f'<div class="cuerpo"><h1 style="font-size:{tam:.0f}px;margin-top:64px">{rico(lam["titulo"])}</h1>'
    if lam.get("bajada"):
        c += f'<p class="baj">{rico(lam["bajada"])}</p>'
    if lam.get("foto"):
        c += tarjeta(cfg, lam)
    return pagina(cfg, lam, n, c + "</div>")


def l_foto(cfg, lam, n):
    """Foto en tarjeta y el texto debajo (o arriba con "posicion": "arriba")."""
    texto_ = rotulo(lam)
    if lam.get("titulo"):
        texto_ += f'<h2 style="font-size:60px">{rico(lam["titulo"])}</h2>'
    if lam.get("texto"):
        texto_ += f'<p class="tx claro" style="margin-top:20px">{rico(lam["texto"])}</p>'
    if lam.get("posicion") == "arriba":
        c = f'<div class="cuerpo"><div style="margin-top:56px">{texto_}</div>{tarjeta(cfg, lam)}</div>'
    else:
        c = f'<div class="cuerpo">{tarjeta(cfg, lam).replace("margin-top:48px", "")}<div style="margin-bottom:32px">{texto_}</div></div>'
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
        c += "<ol>" + "".join(f"<li><b>{k:02d}</b><span>{rico(t)}</span></li>" for k, t in enumerate(lam["items"], 1)) + "</ol>"
    return pagina(cfg, lam, n, c + "</div>")


def l_dato(cfg, lam, n):
    """Una cifra enorme y fina, la unidad en verde señal y la explicación debajo."""
    dato = str(lam["dato"])
    tam = lam.get("tam_dato") or min(340, int(1500 / max(len(dato), 3)))
    c = '<div class="cuerpo centro">' + rotulo(lam)
    c += f'<div class="dato" style="font-size:{tam}px">{html.escape(dato)}</div>'
    if lam.get("unidad"):
        c += f'<div class="unidad">{rico(lam["unidad"])}</div>'
    if lam.get("texto"):
        c += f'<p class="tx claro">{rico(lam["texto"])}</p>'
    return pagina(cfg, lam, n, c + "</div>")


def l_citas(cfg, lam, n):
    """La voz de una parte: la cita con comilla colgada y un filete verde; el autor en mono.
    No imita una publicación de X (sin avatar, usuario ni botones)."""
    c = '<div class="cuerpo centro">' + rotulo(lam)
    for cita in lam["citas"]:
        c += (f'<blockquote><p>“{rico(cita["texto"])}”</p>'
              f'<cite>{html.escape(cita["autor"])}</cite></blockquote>')
    return pagina(cfg, lam, n, c + "</div>")


def l_cta(cfg, lam, n):
    lam = dict(lam, meta=lam.get("rotulo") or "Conversemos")
    tam = 88 * lam.get("escala", 1.0)
    c = f'<div class="cuerpo centro"><h1 style="font-size:{tam:.0f}px">{rico(lam["pregunta"])}</h1>'
    if lam.get("texto"):
        c += f'<p class="tx">{rico(lam["texto"])}</p>'
    c += "</div>"
    c += ('<div class="cierre"><div><div class="acciones"><span>Comenta</span><span>Guarda</span><span>Comparte</span></div>'
          f'<img src="{logo_uri(44)}" alt=""></div><div class="cuenta">{html.escape(lam.get("cuenta", "@dialmedio"))}</div></div>')
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
