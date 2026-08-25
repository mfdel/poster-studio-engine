"""Canonical repo paths — one source of truth for every poster product.

Layout (see ``docs/architecture.md``)::

    posterlab/          shared engine (this package)
    posters/<slug>/     one poster product per directory
    studio/             shop-level assets: themes, brand, commerce, dashboard
    data/runs/<kind>/   immutable per-run data, partitioned by poster kind
    output/<kind>/       rendered posters, partitioned by poster kind
"""
from __future__ import annotations

from pathlib import Path

# posterlab/paths.py -> posterlab/ -> repo root
ROOT = Path(__file__).resolve().parents[1]

DATA = ROOT / "data"
OUTPUT = ROOT / "output"
POSTERS = ROOT / "posters"
STUDIO = ROOT / "studio"

# Themes are shared across every poster product on purpose: one art style across
# the whole shop is the moat, so a new product inherits the look instead of
# inventing one.
THEMES = STUDIO / "themes"
