# dial-noticias

Kit de Dial Medio para publicar noticias del día: a partir de fotos o videos, genera carruseles e historias con la colorización y el diseño de la marca.

- `SISTEMA.md`: el proceso completo (investigación, criterio editorial, formato, entrega). Es la fuente de verdad.
- `PROMPT.md`: el prompt que se pega en una conversación nueva junto con las fotos o videos.
- `dial_noticias.py`: el generador (Python + Pillow + numpy; ffmpeg para videos).
- `ejemplo/`: el JSON del plantón del Museo Nacional (17 oct 2026). Las fotos no están incluidas.

```bash
pip install pillow numpy
python dial_noticias.py ejemplo/2026-10-17-planton-museo.json
```

Las tipografías (Instrument Sans, Instrument Serif, IBM Plex Mono) tienen licencia SIL Open Font License 1.1. El logo de Dial Medio es una marca de Dial y solo se usa en piezas de Dial.
