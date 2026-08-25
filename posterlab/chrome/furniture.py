"""Page furniture: border, title band, coordinates line, attribution.

These are the parts of a poster that must look identical across products. They
read the theme's ``palette``, ``type`` and ``border`` blocks only — no product
knowledge (no maps, no charts) leaks in here.
"""
from __future__ import annotations

from html import escape

from posterlab.svg.primitives import num

# Credit rendered on anything derived from OpenStreetMap data (ODbL). The OSMF
# attribution guidelines name this exact wording — "© OpenStreetMap" alone drops
# the contributors, who are the licensors. The label is right-anchored, so a
# longer string grows away from the frame edge and no layout has to move.
ATTRIBUTION_OSM = "© OpenStreetMap contributors"


def render_border(W: float, H: float, theme: dict) -> str:
    b = theme.get("border", {})
    style = b.get("style", "thin")
    if style == "none":
        return ""
    color = theme["palette"]["border"]
    inset = b.get("inset", 7.0)
    w = b.get("weight", 0.7)
    x, y, ww, hh = inset, inset, W - 2 * inset, H - 2 * inset
    rect = (f'<rect x="{num(x)}" y="{num(y)}" width="{num(ww)}" height="{num(hh)}" '
            f'fill="none" stroke="{color}" stroke-width="{num(w)}"/>')
    if style == "double":
        gap = 1.6
        rect += (f'<rect x="{num(x + gap)}" y="{num(y + gap)}" '
                 f'width="{num(ww - 2 * gap)}" height="{num(hh - 2 * gap)}" '
                 f'fill="none" stroke="{color}" stroke-width="{num(w * 0.6)}"/>')
    return rect


def title_block(W: float, top: float, title: str, subtitle: str, coords: str,
                theme: dict, cx: float, avail: float) -> str:
    """Title + one secondary line ("subtitle · coordinates"), centred on ``cx``."""
    t = theme["type"]
    pal = theme["palette"]
    title_txt = title.upper() if t.get("title_uppercase") else title
    sub_txt = subtitle.upper() if t.get("subtitle_uppercase") else subtitle
    # Auto-fit the title to the content width so long / uppercase titles never
    # bleed past the margins. Estimate advance width from a conservative average
    # glyph ratio + the theme's letter-spacing, then shrink to fit.
    tracking = t.get("title_tracking", 0)
    n = max(len(title_txt), 1)
    ratio = 0.63 if t.get("title_uppercase") else 0.56
    fit = (avail * 0.96 - tracking * (n - 1)) / (ratio * n)
    title_size = max(5.0, min(W * 0.046, fit))
    sub_size = W * 0.018
    out = [
        f'<text x="{num(cx)}" y="{num(top)}" text-anchor="middle" '
        f'font-family="{escape(t["title_font"])}" font-size="{num(title_size)}" '
        f'font-weight="{t.get("title_weight", "700")}" '
        f'letter-spacing="{num(t.get("title_tracking", 0))}" '
        f'fill="{pal["text"]}">{escape(title_txt)}</text>'
    ]
    # Address and coordinates share one line — the coords sit right after the
    # address rather than on a separate row that eats vertical space.
    line = sub_txt
    if coords:
        line = f"{sub_txt}    ·    {coords}" if sub_txt else coords
    if line:
        out.append(
            f'<text x="{num(cx)}" y="{num(top + sub_size * 1.9)}" text-anchor="middle" '
            f'font-family="{escape(t["label_font"])}" font-size="{num(sub_size)}" '
            f'letter-spacing="{num(sub_size * 0.12)}" fill="{pal["muted"]}">'
            f'{escape(line)}</text>'
        )
    return "".join(out)


def attribution(rect: tuple[float, float, float, float], theme: dict,
                text: str = ATTRIBUTION_OSM) -> str:
    """Data credit, tucked into the bottom-right corner of ``rect``: small and
    faint (mostly transparent) so it never competes with the artwork but always
    ships. ``rect`` is the artwork area — the map frame, chart frame, etc.
    """
    mx, my, mw, mh = rect
    pal = theme["palette"]
    size = max(1.8, mw * 0.0085)
    pad = size * 1.1
    return (f'<text x="{num(mx + mw - pad)}" y="{num(my + mh - pad)}" text-anchor="end" '
            f'font-family="{escape(theme["type"]["body_font"])}" font-size="{num(size)}" '
            f'fill="{pal["muted"]}" opacity="0.25">{escape(text)}</text>')


def coords_label(home: dict) -> str:
    """``"55.5678°N  ·  13.0123°E"`` from a dict with ``lat``/``lon``."""
    lat, lon = home["lat"], home["lon"]
    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"
    return f"{abs(lat):.4f}°{ns}  ·  {abs(lon):.4f}°{ew}"
