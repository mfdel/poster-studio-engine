"""PRT-006 Sun-Year Poster - Turn 1 final render, variants 1A and 1B only.

Recreates https://claude.ai/design/p/c55a58b9-04bb-46d7-b1c8-027878280105
("Sun Year Poster.dc.html") in matplotlib for all four places:

  1A  365 rays   - one stroke per day per twilight band, drawn from that
                   band's start to its end, radius = hour-of-day
                   (0-24h -> R0-R1px). Same four nested bands as 1B
                   (astronomical / nautical / civil / day), so the ray
                   variant carries the same shading as the filled ring.
  1B  filled ring - same radial mapping, but four nested twilight bands
                   (astronomical / nautical / civil / day) as closed rings.

1C (spiral) is not implemented - out of scope for this pass.

Palette, type sizes and copy ("the dark we got through", stat phrasing)
are pulled directly from the design doc's support.js, not re-derived.
"""
import datetime as dt
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import astral.sun as asun
from astral import LocationInfo
from zoneinfo import ZoneInfo

YEAR = 2026
OUTDIR = os.path.dirname(os.path.abspath(__file__))

PLACES = [
    dict(key="malmo", name="MALMÖ", lat=55.6050, lon=13.0038, tz="Europe/Stockholm",
         quote="the year we lived on Föreningsgatan"),
    dict(key="kiruna", name="KIRUNA", lat=67.8558, lon=20.2253, tz="Europe/Stockholm",
         quote="the dark we got through"),
    dict(key="istanbul", name="ISTANBUL", lat=41.0082, lon=28.9784, tz="Europe/Istanbul",
         quote="a year between two continents"),
    dict(key="cairo", name="CAIRO", lat=30.0444, lon=31.2357, tz="Africa/Cairo",
         quote="a year by the river"),
]

SAMPLES = 288                 # every 5 minutes
THRESHOLDS = {                # elevation, degrees below horizon
    "day": -0.833,
    "civil": -6.0,
    "naut": -12.0,
    "astro": -18.0,
}

# design doc's SVG radius mapping (1000x1000 viewBox): r = R0 + (h/24)*(R1-R0)
R0, R1 = 64, 444

# ---- palette (support.js) ----
BG = "#1B1424"          # poster panel background
DISC = "#150F1E"        # the r=444 background circle
CREAM = "#F3ECE2"       # title
MUTED = "#8A7C93"       # coordinates
STATS = "#B9743C"       # stat line
QUOTE_COLOR = "#9A8DA3"
ASTRO = "#271C2E"
NAUT = "#4E2C3C"
CIVIL = "#A4552F"
DAY = "#E9B949"

RAY_LW = 1.15            # hairline stroke for the 365-ray variant

# nested twilight bands, outermost (dimmest) first - shared by 1A and 1B
BANDS = (("astro", ASTRO), ("naut", NAUT), ("civil", CIVIL), ("day", DAY))


def rad(h):
    """Hour-of-day (0-24, may be NaN) -> polar radius in design px (R0-R1)."""
    return R0 + (np.asarray(h) / 24.0) * (R1 - R0)


def day_series(lat, lon, tzname, year=YEAR):
    """Per-day start/end hour for each threshold band, standard-time hours.

    NaN where the band never exists that day (permanent dark for that
    threshold); [0, 24] where it holds all day (permanent light).
    """
    tz = ZoneInfo(tzname)
    loc = LocationInfo("", "", tzname, lat, lon)
    std_off = dt.datetime(year, 1, 15, tzinfo=tz).utcoffset()

    rows = []
    d = dt.date(year, 1, 1)
    while d.year == year:
        base = dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc) - std_off
        rows.append([asun.elevation(loc.observer, base + dt.timedelta(hours=24 * j / SAMPLES),
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


def stat_line(s):
    pn = sum(1 for f in s["flag"] if f == "polar_night")
    ms = sum(1 for f in s["flag"] if f == "midnight_sun")
    return pn, ms


def chrome(fig, place, s):
    fig.text(0.5, 0.900, place["name"], ha="center", va="center",
              fontsize=62, color=CREAM, family="serif", weight="bold")
    fig.text(0.5, 0.862, f"{place['lat']}° N  /  {place['lon']}° E", ha="center", va="center",
              fontsize=13, color=MUTED, family="monospace")

    # pn, ms = stat_line(s)
    # if pn:
    #     fig.text(0.30, 0.115, f"{pn} DAYS WITHOUT SUNRISE", ha="center", va="center",
    #               fontsize=11.5, color=STATS, family="monospace")
    # if ms:
    #     fig.text(0.70, 0.115, f"{ms} DAYS WITHOUT NIGHTFALL", ha="center", va="center",
    #               fontsize=11.5, color=STATS, family="monospace")

    fig.text(0.5, 0.058, place["quote"], ha="center", va="center",
              fontsize=19, color=QUOTE_COLOR, family="serif", style="italic")


def new_fig_ax():
    fig = plt.figure(figsize=(9, 12.6), facecolor=BG)
    ax = fig.add_axes([0.10, 0.155, 0.80, 0.68], projection="polar")
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_facecolor(DISC)
    ax.set_ylim(0, R1)
    ax.grid(False)
    ax.spines["polar"].set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    return fig, ax


# --------------------------------------------------------- 1A, 365 rays
def render_1a(place, s, out):
    n = s["n"]
    theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
    fig, ax = new_fig_ax()

    for z, (key, color) in enumerate(BANDS):
        lo, hi = s["bands"][key]
        for i in range(n):
            if np.isnan(lo[i]):
                continue
            ax.plot([theta[i], theta[i]], [rad(lo[i]), rad(hi[i])],
                    color=color, linewidth=RAY_LW, solid_capstyle="butt", zorder=3 + z)

    chrome(fig, place, s)
    fig.savefig(out, dpi=150, facecolor=BG)
    plt.close(fig)
    print("wrote", out)


# ------------------------------------------------- 1B, nested filled ring
def render_1b(place, s, out):
    n = s["n"]
    theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
    theta_c = np.append(theta, 2 * np.pi)
    fig, ax = new_fig_ax()

    def wrap(arr):
        return np.append(arr, arr[0])

    for z, (key, color) in enumerate(BANDS):
        lo, hi = s["bands"][key]
        ax.fill_between(theta_c, rad(wrap(lo)), rad(wrap(hi)),
                         color=color, linewidth=0, zorder=3 + z)

    chrome(fig, place, s)
    fig.savefig(out, dpi=150, facecolor=BG)
    plt.close(fig)
    print("wrote", out)


for place in PLACES:
    s = day_series(place["lat"], place["lon"], place["tz"])
    pn, ms = stat_line(s)
    print(place["name"], pn, ms)
    render_1a(place, s, f"{OUTDIR}/sun_year_{place['key']}_1a_rays.png")
    render_1b(place, s, f"{OUTDIR}/sun_year_{place['key']}_1b_filled_ring.png")
