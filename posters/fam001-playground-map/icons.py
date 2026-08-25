#!/usr/bin/env python3
"""
Icon playground markers for the poster renderer (FAM-001).

Drop-in glyph library that replaces the numbered dots with small playground
pictograms — swing, slide, seesaw, roundabout, ball — plus a few "home" glyphs
(compass, sun) to complement the star / heart / house already in
`render.py`.

A theme opts in via its ``markers`` block:

    "markers": {
      "style": "icon",                 # <- turns these on (absent/other = legacy numbered dots)
      "playground_radius": 4.2,        # badge radius, poster mm
      "icon_color": "#ffffff",         # pictogram stroke colour
      "icon_cycle": ["swing","slide","seesaw","spinner","ball"],
      "badge": "disc",                 # disc | ring | squircle | balloon
      "trail": true,                   # optional dashed path linking markers in order
      "trail_dash": "0.6 3.4",         # optional dash pattern (poster mm)
      "home_style": "compass"          # pin | star | heart | house | compass | sun
    }

Coordinates are in the poster's mm space (same units render.py projects
into), so radii/weights here are on the same scale as the JSON themes.

Wired into ``render.render_map_body`` when a theme sets ``markers.style = "icon"``.
"""
from __future__ import annotations

import math

from posterlab.svg.primitives import num as _num


# --------------------------------------------------------------------------- #
# Playground pictograms — each returns an SVG fragment centred on (x, y),
# drawn within roughly ±s of the centre, stroked in `c`.
# --------------------------------------------------------------------------- #

def _stroke(c: str, sw: float) -> str:
    return (f'fill="none" stroke="{c}" stroke-width="{_num(sw)}" '
            f'stroke-linecap="round" stroke-linejoin="round"')


def icon_swing(x: float, y: float, s: float, c: str, sw: float) -> str:
    d = (f'M{_num(x-s)} {_num(y+s)} L{_num(x-s*0.28)} {_num(y-s)} '
         f'M{_num(x+s)} {_num(y+s)} L{_num(x+s*0.28)} {_num(y-s)} '
         f'M{_num(x-s*0.6)} {_num(y-s)} L{_num(x+s*0.6)} {_num(y-s)} '
         f'M{_num(x-s*0.18)} {_num(y-s)} L{_num(x-s*0.18)} {_num(y+s*0.32)} '
         f'M{_num(x+s*0.18)} {_num(y-s)} L{_num(x+s*0.18)} {_num(y+s*0.32)} '
         f'M{_num(x-s*0.34)} {_num(y+s*0.32)} L{_num(x+s*0.34)} {_num(y+s*0.32)}')
    return f'<path d="{d}" {_stroke(c, sw)}/>'


def icon_slide(x: float, y: float, s: float, c: str, sw: float) -> str:
    d = (f'M{_num(x-s)} {_num(y+s)} Q{_num(x+s*0.05)} {_num(y+s)} '
         f'{_num(x+s*0.22)} {_num(y-s*0.45)} L{_num(x+s*0.6)} {_num(y-s*0.95)} '
         f'M{_num(x+s*0.6)} {_num(y-s*0.95)} L{_num(x+s*0.6)} {_num(y+s)} '
         f'M{_num(x+s*0.18)} {_num(y-s*0.08)} L{_num(x+s*0.6)} {_num(y-s*0.32)}')
    return f'<path d="{d}" {_stroke(c, sw)}/>'


def icon_seesaw(x: float, y: float, s: float, c: str, sw: float) -> str:
    d = (f'M{_num(x-s*0.45)} {_num(y+s)} L{_num(x)} {_num(y+s*0.05)} '
         f'L{_num(x+s*0.45)} {_num(y+s)} Z '
         f'M{_num(x-s)} {_num(y+s*0.5)} L{_num(x+s)} {_num(y-s*0.4)}')
    return (f'<path d="{d}" {_stroke(c, sw)}/>'
            f'<circle cx="{_num(x-s)}" cy="{_num(y+s*0.5)}" r="{_num(s*0.17)}" fill="{c}"/>'
            f'<circle cx="{_num(x+s)}" cy="{_num(y-s*0.4)}" r="{_num(s*0.17)}" fill="{c}"/>')


def icon_spinner(x: float, y: float, s: float, c: str, sw: float) -> str:
    d = (f'M{_num(x-s*0.9)} {_num(y)} L{_num(x+s*0.9)} {_num(y)} '
         f'M{_num(x)} {_num(y-s*0.9)} L{_num(x)} {_num(y+s*0.9)} '
         f'M{_num(x-s*0.64)} {_num(y-s*0.64)} L{_num(x+s*0.64)} {_num(y+s*0.64)} '
         f'M{_num(x-s*0.64)} {_num(y+s*0.64)} L{_num(x+s*0.64)} {_num(y-s*0.64)}')
    return (f'<circle cx="{_num(x)}" cy="{_num(y)}" r="{_num(s*0.9)}" {_stroke(c, sw)}/>'
            f'<path d="{d}" {_stroke(c, sw)}/>'
            f'<circle cx="{_num(x)}" cy="{_num(y)}" r="{_num(s*0.2)}" fill="{c}"/>')


def icon_ball(x: float, y: float, s: float, c: str, sw: float) -> str:
    d = (f'M{_num(x-s*0.86)} {_num(y)} Q{_num(x)} {_num(y-s*0.55)} {_num(x+s*0.86)} {_num(y)} '
         f'M{_num(x-s*0.55)} {_num(y-s*0.66)} Q{_num(x+s*0.15)} {_num(y)} '
         f'{_num(x-s*0.1)} {_num(y+s*0.82)}')
    return (f'<circle cx="{_num(x)}" cy="{_num(y)}" r="{_num(s*0.86)}" {_stroke(c, sw)}/>'
            f'<path d="{d}" {_stroke(c, sw)}/>')


ICONS = {
    "swing": icon_swing,
    "slide": icon_slide,
    "seesaw": icon_seesaw,
    "spinner": icon_spinner,
    "ball": icon_ball,
}


# --------------------------------------------------------------------------- #
# Badges (the coloured shape the pictogram sits on)
# --------------------------------------------------------------------------- #

def _badge(x: float, y: float, R: float, badge: str, fill: str,
           icon_color: str, page: str, stroke_w: float,
           outline_color: str | None = None, outline_w: float | None = None) -> tuple[str, float]:
    """Return (svg, icon_y).

    Default (no theme override): a thick `page`-coloured halo separates the
    badge from busy map detail underneath. A theme can opt into a thin
    accent-coloured ring instead via ``markers.badge_outline_color`` (+
    optional ``badge_outline_width``) — e.g. a slim contrasting border instead
    of a broad paper-coloured halo.
    """
    if outline_color:
        halo = (f'stroke="{outline_color}" '
                f'stroke-width="{_num(outline_w if outline_w is not None else stroke_w * 0.5)}" '
                f'paint-order="stroke"')
    else:
        halo = f'stroke="{page}" stroke-width="{_num(stroke_w*2)}" paint-order="stroke"'
    if badge == "ring":
        svg = (f'<circle cx="{_num(x)}" cy="{_num(y)}" r="{_num(R)}" fill="{fill}" {halo}/>'
               f'<circle cx="{_num(x)}" cy="{_num(y)}" r="{_num(R-R*0.19)}" fill="none" '
               f'stroke="{icon_color}" stroke-width="{_num(R*0.07)}" opacity="0.55"/>')
        return svg, y
    if badge == "squircle":
        svg = (f'<rect x="{_num(x-R)}" y="{_num(y-R)}" width="{_num(2*R)}" '
               f'height="{_num(2*R)}" rx="{_num(R*0.42)}" fill="{fill}" {halo}/>')
        return svg, y
    if badge == "balloon":
        iy = y - R * 0.08
        svg = (f'<path d="M{_num(x)} {_num(y+R)} L{_num(x-R*0.14)} {_num(y+R-R*0.11)} '
               f'L{_num(x+R*0.14)} {_num(y+R-R*0.11)} Z" fill="{fill}"/>'
               f'<ellipse cx="{_num(x)}" cy="{_num(iy)}" rx="{_num(R*0.9)}" ry="{_num(R)}" '
               f'fill="{fill}" {halo}/>')
        return svg, iy
    # disc
    svg = f'<circle cx="{_num(x)}" cy="{_num(y)}" r="{_num(R)}" fill="{fill}" {halo}/>'
    return svg, y


# --------------------------------------------------------------------------- #
# Home glyphs not already covered by render.home_marker_svg
# --------------------------------------------------------------------------- #

def home_compass(x: float, y: float, s: float, color: str, page: str) -> str:
    return (f'<g paint-order="stroke">'
            f'<circle cx="{_num(x)}" cy="{_num(y)}" r="{_num(s*0.95)}" fill="{page}" '
            f'stroke="{color}" stroke-width="{_num(s*0.16)}"/>'
            f'<path d="M{_num(x)} {_num(y-s*0.75)} L{_num(x+s*0.34)} {_num(y)} '
            f'L{_num(x)} {_num(y+s*0.75)} L{_num(x-s*0.34)} {_num(y)} Z" fill="{color}"/>'
            f'<circle cx="{_num(x)}" cy="{_num(y)}" r="{_num(s*0.12)}" fill="{page}"/></g>')


def home_sun(x: float, y: float, s: float, color: str, page: str) -> str:
    rays = ""
    for i in range(8):
        a = i * math.pi / 4
        rays += (f'M{_num(x+math.cos(a)*s*0.72)} {_num(y+math.sin(a)*s*0.72)} '
                 f'L{_num(x+math.cos(a)*s*1.1)} {_num(y+math.sin(a)*s*1.1)} ')
    return (f'<g paint-order="stroke">'
            f'<circle cx="{_num(x)}" cy="{_num(y)}" r="{_num(s*0.52)}" fill="{color}" '
            f'stroke="{page}" stroke-width="{_num(s*0.2)}"/>'
            f'<path d="{rays}" fill="none" stroke="{color}" stroke-width="{_num(s*0.2)}" '
            f'stroke-linecap="round"/></g>')


HOME_EXTRA = {"compass": home_compass, "sun": home_sun}


# --------------------------------------------------------------------------- #
# Public entry point
# --------------------------------------------------------------------------- #

def render_icon_markers(numbered, home, proj, theme, home_marker_svg) -> str:
    """Full markers layer: optional trail, icon badges, and the home glyph.

    `proj`             the posterlab.geo Projector (lon,lat -> poster point)
    `home_marker_svg`  render.home_marker_svg (used for star/heart/house/pin)
    """
    mk = theme["markers"]
    pal = theme["palette"]
    R = mk["playground_radius"]
    icon_color = mk.get("icon_color", pal.get("playground_marker_text", "#ffffff"))
    cycle = mk.get("icon_cycle", ["swing", "slide", "seesaw", "spinner", "ball"])
    badge = mk.get("badge", "disc")
    stroke_w = mk.get("playground_stroke_w", 1.4)
    outline_color = mk.get("badge_outline_color")
    outline_w = mk.get("badge_outline_width")
    out = []

    pts = [proj(p["lon"], p["lat"]) for p in numbered]

    if mk.get("trail") and len(pts) > 1:
        dash = mk.get("trail_dash", "0.6 3.4")
        d = "M" + "L".join(f"{_num(px)} {_num(py)}" for px, py in pts)
        out.append(f'<path d="{d}" fill="none" stroke="{pal["playground_marker"]}" '
                   f'stroke-width="{_num(R*0.28)}" stroke-dasharray="{dash}" '
                   f'stroke-linecap="round" opacity="0.55"/>')

    s = R * 0.56
    isw = max(0.35, s * 0.24)
    for i, (px, py) in enumerate(pts):
        svg, iy = _badge(px, py, R, badge, pal["playground_marker"],
                         icon_color, pal["page"], stroke_w,
                         outline_color=outline_color, outline_w=outline_w)
        glyph = ICONS.get(cycle[i % len(cycle)], icon_swing)(px, iy, s, icon_color, isw)
        out.append(f"<g>{svg}{glyph}</g>")

    hx, hy = proj(home["lon"], home["lat"])
    style = mk.get("home_style", "pin")
    if style in HOME_EXTRA:
        home_scale = mk.get("home_scale", 1.05)
        out.append(HOME_EXTRA[style](hx, hy, R * home_scale, pal["home_marker"], pal["page"]))
    else:
        home_scale = mk.get("home_scale", 1.0)
        out.append(home_marker_svg(hx, hy, style, pal["home_marker"], pal["page"], R * home_scale))

    return "".join(out)
