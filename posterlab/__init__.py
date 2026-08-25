"""posterlab — the shared poster engine.

Everything in here is **poster-type agnostic**: page sizes, brand chrome (border,
title band, coordinates line, attribution), SVG primitives, geodesy/OSM plumbing,
theme loading, export, and the run store. One poster product never imports
another; anything two products need lives here.

Poster products live in ``posters/<slug>/`` and import this package:

    from posterlab.chrome import SIZES, render_border, title_block
    from posterlab.export import export_pdf, export_png
    from posterlab.themes import load_theme, available_themes

Data © OpenStreetMap contributors (ODbL) wherever OSM data is used —
attribution must be carried through to every rendered/printed/sold artifact.
"""
from __future__ import annotations

__all__ = ["paths", "text", "themes", "select", "export", "runstore", "geo", "svg",
           "chrome"]
