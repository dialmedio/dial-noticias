# dial-noticias

Kit de Dial Medio para publicar noticias del día: a partir de fotos o videos, genera carruseles e historias con la colorización y el diseño de la marca.

- `SISTEMA.md`: el proceso completo (investigación, criterio editorial, formato, entrega). Es la fuente de verdad.
- `PROMPT.md`: el prompt que se pega en una conversación nueva junto con las fotos o videos.
- `dial_noticias.py`: el generador (Python + Pillow + numpy; ffmpeg para videos).
- `al_aire.py`: el diseño Al Aire (cabecera, titulares condensados con franja brasa, láminas sin foto); `nuevos_mundos.py` (Termómetro), `arte.py`, `tecnologia.py` y `mundos.py`, las demás líneas.
- `oficio.py` (kerning real con fontTools) y `materia.py` (papel, tinta, trama y rasgado): lo común de todas las líneas desde la v3.
- `iluminado.py` (grabado de buril, fotograbado para personas, aguada, paisaje continuo, pincelada, hoja rasgada, dos voces) ; `afiche.py` (portada de cartel por capas, anillos de pluma, franja de resaltador por renglón, banda de foto rasgada, retrato en blanco y negro, cierre con la misión); y `REFERENTES.md` (lo aprendido de los referentes que manda Martín, una ficha por referente y una caja de herramientas que las junta). Requieren además `scipy` y `rembg`.
- `ejemplo/`: el JSON del plantón del Museo Nacional (17 oct 2026). Las fotos no están incluidas.

```bash
pip install pillow numpy fonttools
python dial_noticias.py ejemplo/2026-10-17-planton-museo.json
```

Las tipografías (Instrument Sans, Instrument Serif, IBM Plex Mono, Newsreader, Archivo, Geist) tienen licencia SIL Open Font License 1.1. El logo de Dial Medio es una marca de Dial y solo se usa en piezas de Dial.
