"""PRT-006 Sun-Year Poster — the filled-ring composition (variant 1B), print-ready.

This is the composition that goes on sale: four nested twilight bands
(astronomical / nautical / civil / day) drawn as closed rings on a dark ground,
with the place name, its coordinates and one line of the buyer's own text.

The layout is the one proven in `drafts/sunyear_poster_1a_1b.py`; this module adds
what selling it needs:

* real print sizes — the figure is created at the poster's physical dimensions, so
  the PDF is a true 30x40 / 40x50 / 50x70 cm page (vector: crisp at any DPI),
* type that scales with the sheet instead of being pinned to the draft's 9 inches,
* correct hemisphere suffixes on the coordinate line (Reykjavík and Edinburgh are
  west of Greenwich; the draft hard-coded "E"),
* a sample/hero set of locations for the Etsy listing.

Usage
-----
    uv run python posters/prt006-sun-year/render_1b.py                  # every sample location
    uv run python posters/prt006-sun-year/render_1b.py --location malmo --size 50x70
    uv run python posters/prt006-sun-year/render_1b.py --sellable-only --no-pdf

Previews (PNG, ~2000 px wide) land in `brand/samples/`; print-ready PDFs land in
`output/sun/samples/` (gitignored — regenerate them with this script).
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
from zoneinfo import ZoneInfo

import matplotlib

matplotlib.use("Agg")
import astral.sun as asun
import matplotlib.pyplot as plt
import numpy as np
from astral import LocationInfo
from matplotlib import font_manager
from matplotlib.patches import Rectangle

from posterlab.text import pick_font
from posterlab.themes import chart_tokens, load_theme

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
PREVIEW_DIR = os.path.join(HERE, "brand", "samples")
PRINT_DIR = os.path.join(REPO, "output", "sun", "samples")

YEAR = 2026
SAMPLES = 288  # elevation samples per day (every 5 minutes)
PREVIEW_PX = 2000  # Etsy wants ~2000 px on the short edge

# The latitude gate from docs/sun_year_poster_plan.md §7: below ~35° the ring is a
# featureless donut and we do not sell it. Sub-gate places stay in the list because
# they are the honest comparison shots, but they are not listing heroes.
LAT_GATE_SELL = 48.0

LOCATIONS = [
    # The hero set (docs/sun_year_poster_plan.md §5) plus the draft's originals.
    dict(key="malmo", name="MALMÖ", lat=55.6050, lon=13.0038, tz="Europe/Stockholm",
         quote="the year we lived on Föreningsgatan"),
    dict(key="stockholm", name="STOCKHOLM", lat=59.3293, lon=18.0686, tz="Europe/Stockholm",
         quote="our first year in the city"),
    dict(key="kiruna", name="KIRUNA", lat=67.8558, lon=20.2253, tz="Europe/Stockholm",
         quote="the dark we got through"),
    dict(key="tromso", name="TROMSØ", lat=69.6492, lon=18.9553, tz="Europe/Oslo",
         quote="two months without a sunrise"),
    dict(key="reykjavik", name="REYKJAVÍK", lat=64.1466, lon=-21.9426, tz="Atlantic/Reykjavik",
         quote="the year the light came back"),
    dict(key="edinburgh", name="EDINBURGH", lat=55.9533, lon=-3.1883, tz="Europe/London",
         quote="the year we found the sea"),
    dict(key="oslo", name="OSLO", lat=59.9139, lon=10.7522, tz="Europe/Oslo",
         quote="a year under northern light"),
    dict(key="copenhagen", name="COPENHAGEN", lat=55.6761, lon=12.5683, tz="Europe/Copenhagen",
         quote="the year we moved in"),
    dict(key="helsinki", name="HELSINKI", lat=60.1699, lon=24.9384, tz="Europe/Helsinki",
         quote="a year of long winters"),
    # Below the latitude gate — kept for the comparison shot, never sold.
    dict(key="istanbul", name="ISTANBUL", lat=41.0082, lon=28.9784, tz="Europe/Istanbul",
         quote="a year between two continents"),
    dict(key="cairo", name="CAIRO", lat=30.0444, lon=31.2357, tz="Africa/Cairo",
         quote="a year by the river"),
]

SIZES_CM = {"30x40": (30, 40), "40x50": (40, 50), "50x70": (50, 70)}

THRESHOLDS = {  # solar elevation, degrees relative to the horizon
    "day": -0.833,
    "civil": -6.0,
    "naut": -12.0,
    "astro": -18.0,
}

# Radial mapping from the design doc (1000x1000 viewBox): r = R0 + (h/24)*(R1-R0)
R0, R1 = 64, 444

DEFAULT_THEME = "nocturne"
BAND_KEYS = ("astro", "naut", "civil", "day")  # drawn outermost-first, so day sits on top

# The draft's layout, expressed against a 9 x 12.6 inch sheet. Font sizes are scaled
# by the real sheet width so a 50x70 print is the draft blown up, not re-designed.
BASE_W_IN = 9.0
DISC_W_FRAC = 0.80  # ring diameter as a fraction of the sheet width
DISC_CENTER_Y = 0.495  # ring centre, fraction of sheet height from the bottom
TITLE_Y, COORDS_Y, QUOTE_Y = 0.900, 0.862, 0.058
TITLE_PT, COORDS_PT, QUOTE_PT = 62, 13, 19


def build_style(theme_name: str) -> dict:
    """Resolve a studio theme into the concrete values matplotlib needs.

    The ring's colours come from the theme's ``chart`` block and its type and border
    from the same ``type`` / ``border`` blocks the map renderer reads, so the two
    products share a frame while keeping their own artwork.
    """
    theme = load_theme(theme_name)
    pal, tok = theme["palette"], chart_tokens(theme)
    t = theme["type"]
    have = {f.name for f in font_manager.fontManager.ttflist}
    return dict(
        theme=theme,
        bg=pal["page"],
        disc=tok.get("plot_bg", tok["night"]),
        text=pal["text"],
        muted=pal["muted"],
        quote=tok.get("quote", pal["muted"]),
        bands=[tok[k] for k in BAND_KEYS],
        title_font=pick_font(t["title_font"], have),
        label_font=pick_font(t["label_font"], have),
        body_font=pick_font(t["body_font"], have),
        # matplotlib wants an int weight (0-1000) or a name; themes carry CSS strings.
        title_weight=int(w) if (w := str(t.get("title_weight", "700"))).isdigit() else w,
        title_tracking=float(t.get("title_tracking", 0)),
        title_uppercase=bool(t.get("title_uppercase")),
        border=theme.get("border", {}),
        border_color=pal["border"],
    )


def tracked(s: str, tracking: float) -> str:
    """Approximate CSS letter-spacing, which matplotlib has no property for.

    A thin space is roughly 0.2 em, so themes that track their titles at least a
    fifth of an em get one between each glyph. Coarse on purpose — it keeps the
    airy Ink & Play title without a per-character text-layout pass.
    """
    return " ".join(s) if tracking >= 2.0 else s


def draw_border(fig, size_cm: tuple[float, float], st: dict) -> None:
    """The studio's page border, inset by the theme's millimetres.

    Same rectangle `posterlab.chrome.furniture.render_border` draws on the map — it
    is the piece of chrome that makes two unrelated artworks read as one shop.
    """
    b = st["border"]
    if b.get("style", "thin") == "none":
        return
    inset = b.get("inset", 7.0)  # mm, like every studio theme
    x, y = inset / (size_cm[0] * 10), inset / (size_cm[1] * 10)
    fig.add_artist(Rectangle(
        (x, y), 1 - 2 * x, 1 - 2 * y, transform=fig.transFigure, facecolor="none",
        edgecolor=st["border_color"], linewidth=b.get("weight", 0.7) * 72 / 25.4,
        zorder=10))


def fit_text(fig, txt, max_width_frac: float) -> None:
    """Shrink a text artist until it fits ``max_width_frac`` of the sheet width.

    The map's title block does the same auto-fit; without it a tracked COPENHAGEN
    runs past the border that a tracked OSLO sits comfortably inside.
    """
    renderer = fig.canvas.get_renderer()
    for _ in range(24):
        width = txt.get_window_extent(renderer=renderer).width
        if width <= max_width_frac * fig.bbox.width:
            return
        txt.set_fontsize(txt.get_fontsize() * 0.94)


def rad(h):
    """Hour-of-day (0-24, may be NaN) -> polar radius in design units (R0-R1)."""
    return R0 + (np.asarray(h) / 24.0) * (R1 - R0)


def coords_line(lat: float, lon: float) -> str:
    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"
    return f"{abs(lat):.4f}° {ns}  /  {abs(lon):.4f}° {ew}"


def day_series(lat: float, lon: float, tzname: str, year: int = YEAR) -> dict:
    """Per-day start/end hour of each twilight band, in standard (non-DST) local time.

    Standard time keeps the ring smooth: wall-clock hours would put a visible
    one-hour step at each DST boundary. NaN marks a band that never happens that
    day (polar night); a full [0, 24] span marks one that holds all day.
    """
    tz = ZoneInfo(tzname)
    loc = LocationInfo("", "", tzname, lat, lon)
    std_off = dt.datetime(year, 1, 15, tzinfo=tz).utcoffset()

    rows = []
    d = dt.date(year, 1, 1)
    while d.year == year:
        base = dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc) - std_off
        rows.append([asun.elevation(loc.observer,
                                    base + dt.timedelta(hours=24 * j / SAMPLES),
                                    with_refraction=False)
                     for j in range(SAMPLES + 1)])
        d += dt.timedelta(days=1)
    E = np.array(rows)

    def spans(thr):
        lo = np.full(len(E), np.nan)
        hi = np.full(len(E), np.nan)
        for i, e in enumerate(E):
            idx = np.flatnonzero(e > thr)
            if not idx.size:
                continue
            a, b = idx[0], idx[-1]
            ta = a - 1 + (thr - e[a - 1]) / (e[a] - e[a - 1]) if a > 0 else 0.0
            tb = b + (thr - e[b]) / (e[b + 1] - e[b]) if b < len(e) - 1 else len(e) - 1
            lo[i], hi[i] = ta * 24 / SAMPLES, tb * 24 / SAMPLES
        return lo, hi

    bands = {key: spans(thr) for key, thr in THRESHOLDS.items()}
    day_mask = E > THRESHOLDS["day"]
    flag = ["midnight_sun" if r.all() else "polar_night" if not r.any() else "normal"
            for r in day_mask]
    return dict(bands=bands, flag=flag, n=len(flag))


def polar_night_days(s: dict) -> int:
    return sum(1 for f in s["flag"] if f == "polar_night")


def midnight_sun_days(s: dict) -> int:
    return sum(1 for f in s["flag"] if f == "midnight_sun")


def build_figure(place: dict, s: dict, size_cm: tuple[float, float], st: dict):
    """Render the filled ring onto a sheet of the given physical size, in cm."""
    w_in, h_in = size_cm[0] / 2.54, size_cm[1] / 2.54
    scale = w_in / BASE_W_IN

    fig = plt.figure(figsize=(w_in, h_in), facecolor=st["bg"])

    # A square axes box the ring exactly fills, centred on DISC_CENTER_Y. Working in
    # inches first is what keeps the ring the same relative size on all three
    # aspect ratios (30x40 is 1:1.33, 50x70 is 1:1.40).
    disc_in = DISC_W_FRAC * w_in
    ax_h = disc_in / h_in
    ax = fig.add_axes([(1 - DISC_W_FRAC) / 2, DISC_CENTER_Y - ax_h / 2, DISC_W_FRAC, ax_h],
                      projection="polar")
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)  # 1 January at the top, running clockwise
    ax.set_facecolor(st["disc"])
    ax.set_ylim(0, R1)
    ax.grid(False)
    ax.spines["polar"].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])

    n = s["n"]
    theta = np.append(np.linspace(0, 2 * np.pi, n, endpoint=False), 2 * np.pi)
    wrap = lambda arr: np.append(arr, arr[0])  # noqa: E731 — close the year onto itself

    for z, (key, color) in enumerate(zip(BAND_KEYS, st["bands"])):
        lo, hi = s["bands"][key]
        ax.fill_between(theta, rad(wrap(lo)), rad(wrap(hi)),
                        color=color, linewidth=0, zorder=3 + z)

    title = place["name"].upper() if st["title_uppercase"] else place["name"]
    txt = fig.text(0.5, TITLE_Y, tracked(title, st["title_tracking"]), ha="center",
                   va="center", fontsize=TITLE_PT * scale, color=st["text"],
                   family=st["title_font"], weight=st["title_weight"])
    inset_frac = st["border"].get("inset", 7.0) / (size_cm[0] * 10)
    fit_text(fig, txt, 1 - 2 * inset_frac - 0.08)
    fig.text(0.5, COORDS_Y, coords_line(place["lat"], place["lon"]), ha="center", va="center",
             fontsize=COORDS_PT * scale, color=st["muted"], family=st["label_font"])
    fig.text(0.5, QUOTE_Y, place["quote"], ha="center", va="center",
             fontsize=QUOTE_PT * scale, color=st["quote"],
             family=st["body_font"], style="italic")
    draw_border(fig, size_cm, st)
    return fig


def render(place: dict, s: dict, sizes: list[str], preview: bool, pdf: bool, st: dict,
           preview_dir: str = PREVIEW_DIR, print_dir: str = PRINT_DIR) -> list[str]:
    written = []
    if preview:
        # The preview is the 50x70 sheet rasterised — same artwork, listing-photo sized.
        fig = build_figure(place, s, SIZES_CM["50x70"], st)
        out = os.path.join(preview_dir, f"sunyear_{place['key']}_ring.png")
        fig.savefig(out, dpi=PREVIEW_PX / (SIZES_CM["50x70"][0] / 2.54), facecolor=st["bg"])
        plt.close(fig)
        written.append(out)
    if pdf:
        for size in sizes:
            fig = build_figure(place, s, SIZES_CM[size], st)
            out = os.path.join(print_dir, f"sunyear_{place['key']}_ring_{size}.pdf")
            fig.savefig(out, format="pdf", facecolor=st["bg"])
            plt.close(fig)
            written.append(out)
    return written


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--location", action="append",
                    help="location key (repeatable); default: all sample locations")
    ap.add_argument("--size", action="append", choices=sorted(SIZES_CM),
                    help="print size (repeatable); default: all three")
    ap.add_argument("--sellable-only", action="store_true",
                    help=f"skip locations below {LAT_GATE_SELL:g}° — the ones we don't sell")
    ap.add_argument("--no-pdf", action="store_true", help="previews only, no print PDFs")
    ap.add_argument("--no-preview", action="store_true", help="print PDFs only")
    ap.add_argument("--year", type=int, default=YEAR)
    ap.add_argument("--theme", default=DEFAULT_THEME,
                    help=f"studio theme name or path (default: {DEFAULT_THEME})")
    ap.add_argument("--preview-dir", default=PREVIEW_DIR,
                    help="where preview PNGs go (default: brand/samples)")
    ap.add_argument("--print-dir", default=PRINT_DIR,
                    help="where print PDFs go (default: output/sun/samples)")
    args = ap.parse_args()
    st = build_style(args.theme)

    by_key = {p["key"]: p for p in LOCATIONS}
    if args.location:
        unknown = [k for k in args.location if k not in by_key]
        if unknown:
            ap.error(f"unknown location(s): {', '.join(unknown)}. "
                     f"known: {', '.join(by_key)}")
        places = [by_key[k] for k in args.location]
    else:
        places = list(LOCATIONS)
    if args.sellable_only:
        places = [p for p in places if abs(p["lat"]) >= LAT_GATE_SELL]

    sizes = args.size or sorted(SIZES_CM)
    os.makedirs(args.preview_dir, exist_ok=True)
    os.makedirs(args.print_dir, exist_ok=True)

    for place in places:
        s = day_series(place["lat"], place["lon"], place["tz"], args.year)
        gate = "sellable" if abs(place["lat"]) >= LAT_GATE_SELL else "below latitude gate"
        print(f"{place['name']:<11} {place['lat']:>7.4f}°  "
              f"polar night {polar_night_days(s):>3}d  midnight sun {midnight_sun_days(s):>3}d  "
              f"({gate})")
        for out in render(place, s, sizes, not args.no_preview, not args.no_pdf, st,
                          args.preview_dir, args.print_dir):
            print("  wrote", os.path.relpath(out, REPO))


if __name__ == "__main__":
    main()
