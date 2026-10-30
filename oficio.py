"""Oficio tipográfico para las láminas que dibuja Pillow (v3, 24 oct 2026).

Pillow sin libraqm compone el texto letra por letra con su avance y sin kerning: la tabla GPOS de las fuentes
modernas no se lee, así que pares como "Lo", "Te", "V." o "r," quedan abiertos. Es una de las cosas que hacen que
una lámina se vea "de máquina" aunque el diseño esté bien. Este módulo lee el kerning de la fuente con fontTools
(en la instancia exacta de la variable: ancho y peso) y lo aplica al medir y al dibujar, sin cambiar nada más:

- `Fuente` es una FreeTypeFont que mide con kerning (`getlength`) y sabe el ajuste de cada par (`kern`).
- `ImageDraw.text` se parchea una sola vez: si la fuente es `Fuente`, el texto se dibuja en tramos entre los pares
  con ajuste, respetando el ancla (l, m, r). Con cualquier otra fuente, todo sigue igual.
- Las tablas se guardan en `fuentes/.cache/` (no se suben al repo). Si fontTools no está, no hay kerning y nada falla.
"""
import pickle
from pathlib import Path

from PIL import ImageDraw, ImageFont

CACHE = Path(__file__).resolve().parent / "fuentes" / ".cache"
_tablas = {}


# ------------------------------------------------------------ lectura del kerning (GPOS, función kern)

def _valor(v1, v2):
    x = 0
    if v1 is not None:
        x += getattr(v1, "XAdvance", 0) or 0
    if v2 is not None:
        x += getattr(v2, "XPlacement", 0) or 0
    return x


def _leer(ruta, ejes):
    from fontTools.ttLib import TTFont
    f = TTFont(str(ruta))
    if ejes and "fvar" in f:
        from fontTools.varLib import instancer
        validos = {a.axisTag for a in f["fvar"].axes}
        f = instancer.instantiateVariableFont(f, {k: v for k, v in ejes.items() if k in validos})
    upem = f["head"].unitsPerEm
    cmap = f.getBestCmap() or {}
    lookups = []
    if "GPOS" in f and f["GPOS"].table.FeatureList:
        g = f["GPOS"].table
        indices = sorted({i for fr in g.FeatureList.FeatureRecord if fr.FeatureTag == "kern"
                          for i in fr.Feature.LookupListIndex})
        for li in indices:
            subtablas = []
            for st in g.LookupList.Lookup[li].SubTable:
                if getattr(st, "LookupType", None) == 9 or hasattr(st, "ExtSubTable"):
                    st = st.ExtSubTable
                if getattr(st, "LookupType", 2) != 2:
                    continue
                cob = {gl: k for k, gl in enumerate(st.Coverage.glyphs)}
                if st.Format == 1:
                    pares = []
                    for ps in st.PairSet:
                        pares.append({r.SecondGlyph: _valor(r.Value1, getattr(r, "Value2", None)) for r in ps.PairValueRecord})
                    subtablas.append((1, cob, pares))
                elif st.Format == 2:
                    c1 = dict(st.ClassDef1.classDefs) if st.ClassDef1 else {}
                    c2 = dict(st.ClassDef2.classDefs) if st.ClassDef2 else {}
                    matriz = [[_valor(r.Value1, getattr(r, "Value2", None)) for r in fila.Class2Record] for fila in st.Class1Record]
                    subtablas.append((2, cob, (c1, c2, matriz)))
            if subtablas:
                lookups.append(subtablas)
    return {"upem": upem, "cmap": cmap, "lookups": lookups}


def tabla(ruta, ejes=None):
    """El kerning de una fuente (en la instancia dada por `ejes`, p. ej. {"wdth": 75, "wght": 700})."""
    ruta = Path(ruta)
    ejes = {k: round(v) for k, v in (ejes or {}).items()}
    clave = (ruta.name, tuple(sorted(ejes.items())))
    if clave in _tablas:
        return _tablas[clave]
    archivo = CACHE / ("%s-%s.pkl" % (ruta.stem, "-".join(f"{k}{v}" for k, v in sorted(ejes.items())) or "base"))
    t = None
    try:
        if archivo.exists() and archivo.stat().st_mtime >= ruta.stat().st_mtime:
            t = pickle.loads(archivo.read_bytes())
    except Exception:
        t = None
    if t is None:
        try:
            t = _leer(ruta, ejes)
            CACHE.mkdir(parents=True, exist_ok=True)
            archivo.write_bytes(pickle.dumps(t))
        except Exception:  # sin fontTools o fuente rara: sin kerning
            t = {"upem": 1000, "cmap": {}, "lookups": []}
    t["_memo"] = {}
    _tablas[clave] = t
    return t


def ajuste(t, a, b):
    """Ajuste del par (a, b) en unidades de la fuente. Cada lookup suma; dentro de un lookup manda la primera
    subtabla que cubre la primera letra (como HarfBuzz)."""
    memo = t["_memo"]
    if (a, b) in memo:
        return memo[(a, b)]
    ga, gb = t["cmap"].get(ord(a)), t["cmap"].get(ord(b))
    total = 0
    if ga and gb:
        for subtablas in t["lookups"]:
            for fmt, cob, datos in subtablas:
                k = cob.get(ga)
                if k is None:
                    continue
                if fmt == 1:
                    v = datos[k].get(gb)
                    if v is None:
                        continue  # este par no está en esta subtabla: se sigue buscando
                    total += v
                else:
                    c1, c2, matriz = datos
                    total += matriz[c1.get(ga, 0)][c2.get(gb, 0)]
                break
    memo[(a, b)] = total
    return total


# ------------------------------------------------------------ la fuente y el dibujo

class Fuente(ImageFont.FreeTypeFont):
    """FreeTypeFont que mide y dibuja con kerning."""

    def __init__(self, ruta, tam, ejes=None):
        super().__init__(str(ruta), int(round(tam)))
        self.ejes = ejes or {}
        if ejes:
            nombres = [a["name"].decode() if isinstance(a["name"], bytes) else a["name"] for a in self.get_variation_axes()]
            # Pillow pide los ejes en el orden de la fuente
            orden = {"Weight": "wght", "Width": "wdth", "Optical size": "opsz", "Optical Size": "opsz"}
            self.set_variation_by_axes([ejes.get(orden.get(n, n), a["default"]) for n, a in zip(nombres, self.get_variation_axes())])
        self._t = tabla(ruta, ejes)
        self._esc = self.size / self._t["upem"]

    def kern(self, a, b):
        return ajuste(self._t, a, b) * self._esc

    def ajustes(self, texto):
        return [self.kern(texto[i], texto[i + 1]) for i in range(len(texto) - 1)]

    def getlength(self, text, *args, **kwargs):
        base = super().getlength(text, *args, **kwargs)
        return base + (sum(self.ajustes(text)) if len(text) > 1 and "\n" not in text else 0)


_texto_original = ImageDraw.ImageDraw.text


def _texto(self, xy, text, fill=None, font=None, anchor=None, *args, **kwargs):
    if not isinstance(font, Fuente) or not isinstance(text, str) or len(text) < 2 or "\n" in text:
        return _texto_original(self, xy, text, fill, font, anchor, *args, **kwargs)
    aj = font.ajustes(text)
    if not any(abs(a) > 0.05 for a in aj):
        return _texto_original(self, xy, text, fill, font, anchor, *args, **kwargs)
    anchor = anchor or "la"
    total = font.getlength(text)
    x, y = xy
    x0 = x - {"l": 0, "m": total / 2, "r": total}.get(anchor[0], 0)
    inicio, off = 0, 0.0
    for i, a in enumerate(aj + [None]):
        if a is None or abs(a) > 0.05:
            tramo = text[inicio:i + 1]
            _texto_original(self, (x0 + off, y), tramo, fill, font, "l" + anchor[1], *args, **kwargs)
            off += ImageFont.FreeTypeFont.getlength(font, tramo) + (a or 0)
            inicio = i + 1


ImageDraw.ImageDraw.text = _texto
