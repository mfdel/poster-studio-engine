"""PRT-006 Sun-Year Poster - draft renders.

Two layouts, so they can be compared side by side:
  ring    - polar. Year around the circle (1 Jan at top, clockwise),
            24h clock on the radius (midnight centre, midnight rim).
  linear  - cartesian. Date down the y axis (Jan top, Dec bottom),
            24h clock across the x axis (midnight -> noon -> midnight).

Two places: Malmo (55.6N, the founder's own) and Kiruna (67.9N, above
the Arctic Circle - polar night + midnight sun are the hero content).

Bands are derived by sampling solar elevation across each day rather
than by calling astral.sun(), which raises above the Arctic Circle on
any day where civil twilight never ends - including ordinary summer
days when the sun does rise and set normally. Sampling has no special
cases and stays smooth at every latitude.

This is matplotlib, not the print-ready SVG->PDF pipeline the plan
specs for production. Good enough to judge layout, palette, typography.
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

SAMPLES = 288                # every 5 minutes
HORIZON = -0.833             # upper limb + refraction: the sunrise/sunset definition
CIVIL = -6.0                 # civil twilight

# ---- palette ----
BG = "#1D1526"
CHART_BG = "#000000"        # pitch black, chart area only - makes the day/night edge read clearly
GOLD = "#F2C14E"
TWILIGHT = "#C97A3A"
CREAM = "#F4E9D8"
MUTED = "#8A8378"

# The solstices - the emotional anchors of the year, and what makes the
# shape self-explaining: the band is visibly fattest at the June solstice
# and pinched at the December one. They fall 180.6 deg apart on the ring,
# so a single diameter line joins them.
SOLSTICES = [
    dt.date(YEAR, 6, 21),
    dt.date(YEAR, 12, 21),
]


def doy(d):
    return d.timetuple().tm_yday - 1


def day_series(lat, lon, tzname, year=YEAR):
    """Per-day daylight and civil-twilight spans, in fractional standard-time hours.

    Returns NaN spans for days the band does not exist (polar night), which
    matplotlib renders as a true gap rather than a collapsed sliver.
    """
    tz = ZoneInfo(tzname)
    loc = LocationInfo("", "", tzname, lat, lon)

    # Render in standard (non-DST) time so the shape stays smooth instead of
    # stepping an hour at the DST boundaries (plan sec.7).
    std_off = dt.datetime(year, 1, 15, tzinfo=tz).utcoffset()

    rows = []
    d = dt.date(year, 1, 1)
    while d.year == year:
        base = dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc) - std_off
        # Geometric, not refracted: the -0.833 horizon already accounts for
        # refraction plus the solar semi-diameter. Using the refracted
        # elevation here would count refraction twice.
        rows.append([asun.elevation(loc.observer, base + dt.timedelta(hours=24 * j / SAMPLES),
                                    with_refraction=False)
                     for j in range(SAMPLES + 1)])
        d += dt.timedelta(days=1)
    E = np.array(rows)

    def spans(thr):
        """First and last crossing of `thr`, linearly interpolated between
        samples so the drawn edge is smooth rather than stepping in 5-minute
        quanta."""
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

    day_mask = E > HORIZON
    rise, sett = spans(HORIZON)
    dawn, dusk = spans(CIVIL)
    # spans() only returns NaN when a threshold is never crossed in either
    # direction, i.e. when the whole day sits on one side of it - so the
    # "always dark" and "always bright" extremes need their own checks:
    # spans(CIVIL) degrades to (0, 24) rather than NaN when every sample
    # is brighter than civil twilight, which reads as a real span if you
    # don't check for it separately.
    void_all = (E <= CIVIL).all(axis=1)     # true blackout: not even civil twilight
    bright_all = (E > CIVIL).all(axis=1)    # never dark enough for any void at all

    flag = ["midnight_sun" if r.all() else "polar_night" if not r.any() else "normal"
            for r in day_mask]

    return dict(rise=rise, sett=sett, dawn=dawn, dusk=dusk,
                void_all=void_all, bright_all=bright_all,
                flag=flag, n=len(flag), tz=tz, loc=loc)


def polar_stats(s):
    """Describe the polar extremes as *conditions*, not as sunrise/sunset events.

    "N days without a sunrise" would be wrong: during midnight sun there is no
    sunrise either, so the two counts would overlap. Sunlight and darkness are
    genuinely disjoint, so those are what we state.
    """
    pn = sum(1 for f in s["flag"] if f == "polar_night")
    ms = sum(1 for f in s["flag"] if f == "midnight_sun")
    bits = []
    if pn:
        bits.append(f"{pn} DAYS WITHOUT SUNLIGHT")
    if ms:
        bits.append(f"{ms} DAYS WITHOUT DARKNESS")
    return "     ".join(bits)


def radial_text_angle(t):
    """Screen-space rotation (degrees) for text at polar data-angle `t`, so it
    reads along the same line drawn at that angle - not upright/horizontal.

    Data angle -> screen angle needs the axes' own convention undone first
    (theta_zero_location="N", theta_direction=-1: 0 points up, increasing
    clockwise), then flipped 180 deg whenever that would print upside down.
    """
    screen = (90 - np.degrees(t)) % 360
    if 90 < screen < 270:
        screen += 180
    return screen % 360


def chrome(fig, p, s):
    """Shared typography: title, coordinates, polar stats, footer."""
    fig.text(0.5, 0.900, p["name"], ha="center", va="center",
             fontsize=62, color=CREAM, family="serif", weight="bold")
    fig.text(0.5, 0.862, f"{abs(p['lat']):.4f}° N  /  {abs(p['lon']):.4f}° E",
             ha="center", va="center", fontsize=13, color=MUTED, family="monospace")

    stats = polar_stats(s)
    if stats:
        fig.text(0.5, 0.090, stats, ha="center", va="center",
                 fontsize=10, color=TWILIGHT, family="monospace")

    fig.text(0.5, 0.046, p["footer"], ha="center", va="center",
             fontsize=13, color=MUTED, family="serif", style="italic")


# ---------------------------------------------------------------- ring
def render_ring(p, s, out, r_inner=0.0):
    """r_inner=0 draws a filled disc; r_inner>0 leaves a hollow centre and
    draws the same 24h band as an actual ring instead."""
    n = s["n"]
    theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
    # Close the Dec-31 -> Jan-1 seam: without repeating the first sample at
    # theta=2pi, fill_between stops one step short of wrapping back to its
    # own start, leaving a one-day gap where the band should be continuous.
    theta_c = np.append(theta, 2 * np.pi)

    def wrap(key):
        return np.append(s[key], s[key][0])

    r_max = r_inner + 24

    fig = plt.figure(figsize=(9, 12), facecolor=BG)
    ax = fig.add_axes([0.15, 0.17, 0.70, 0.63], projection="polar")
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_facecolor(CHART_BG)
    ax.set_ylim(0, r_max)
    ax.grid(False)
    ax.spines["polar"].set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])

    if r_inner > 0:
        # The hole reads as an opening onto the poster, not as leftover
        # chart-black, so it's filled with the poster background rather
        # than left as the pitch-black chart facecolor. No rim line around
        # it - the black-to-poster color change is edge enough on its own.
        hole = np.linspace(0, 2 * np.pi, 400)
        ax.fill_between(hole, 0, r_inner, color=BG, zorder=1)

    ax.fill_between(theta_c, wrap("dawn") + r_inner, wrap("dusk") + r_inner,
                    color=TWILIGHT, linewidth=0, zorder=3)
    ax.fill_between(theta_c, wrap("rise") + r_inner, wrap("sett") + r_inner,
                    color=GOLD, linewidth=0, zorder=4)

    # Both solstices get a diameter-ish line (they're ~180.6 deg apart, not
    # exactly opposite), but only one needs the "SOLSTICE" word - once
    # you've read it on one line, the other is self-explanatory. The label
    # always sits just outside the rim, rotated to the line's own angle
    # rather than upright, so its position and orientation are consistent
    # across every place instead of jumping inside the band wherever a
    # solstice happens to land in daylight or void.
    for idx, d in enumerate(SOLSTICES):
        i = doy(d)
        t = 2 * np.pi * i / n
        ax.plot([t, t], [r_inner, r_max], color=CREAM, linewidth=0.7, alpha=0.5, zorder=6)

        if idx != 0:
            continue

        ax.text(t, r_max + 3.4, "SOLSTICE", rotation=radial_text_angle(t), rotation_mode="anchor",
                ha="center", va="center", fontsize=8.5, color=CREAM, family="monospace",
                zorder=7, clip_on=False)

    chrome(fig, p, s)
    fig.savefig(out, dpi=150, facecolor=BG)
    plt.close(fig)
    print("wrote", out)


# -------------------------------------------------------------- linear
def render_linear(p, s, out):
    n = s["n"]
    y = np.arange(n)

    fig = plt.figure(figsize=(9, 12), facecolor=BG)
    ax = fig.add_axes([0.15, 0.15, 0.74, 0.68])
    ax.set_facecolor(CHART_BG)

    ax.fill_betweenx(y, s["dawn"], s["dusk"], color=TWILIGHT, linewidth=0, zorder=3)
    ax.fill_betweenx(y, s["rise"], s["sett"], color=GOLD, linewidth=0, zorder=4)

    ax.set_xlim(0, 24)
    ax.set_ylim(n + 9, -10)        # January at top, with breathing room
    for sp in ax.spines.values():
        sp.set_visible(False)

    ax.set_xticks([]); ax.set_yticks([])

    for d in SOLSTICES:
        i = doy(d)
        ax.axhline(i, color=CREAM, linewidth=0.7, alpha=0.5, zorder=5)
        ax.text(24, i - 3, "SOLSTICE", ha="right", va="bottom", fontsize=8.5,
                color=CREAM, family="monospace", zorder=6)

    chrome(fig, p, s)
    fig.savefig(out, dpi=150, facecolor=BG)
    plt.close(fig)
    print("wrote", out)


# No marked date in this draft - the dated variant is a separate design pass.
# Footers for Istanbul/Cairo are placeholders (no personal line to draw on).
PLACES = [
    dict(key="malmo", name="MALMÖ", lat=55.6050, lon=13.0038, tz="Europe/Stockholm",
         footer="the year we lived on Föreningsgatan"),
    dict(key="kiruna", name="KIRUNA", lat=67.8558, lon=20.2253, tz="Europe/Stockholm",
         footer="the dark we got through"),
    dict(key="istanbul", name="ISTANBUL", lat=41.0082, lon=28.9784, tz="Europe/Istanbul",
         footer="a year between two continents"),
    dict(key="cairo", name="CAIRO", lat=30.0444, lon=31.2357, tz="Africa/Cairo",
         footer="a year by the river"),
]

RING_HOLE = 3.0     # inner radius for the hollow-ring style, out of a 24h band

for p in PLACES:
    s = day_series(p["lat"], p["lon"], p["tz"])
    print(f"{p['name']:<8} {polar_stats(s) or 'no polar days'}")
    render_ring(p, s, f"{OUTDIR}/sun_year_draft_{p['key']}_ring.png")
    render_ring(p, s, f"{OUTDIR}/sun_year_draft_{p['key']}_ring_hollow.png", r_inner=RING_HOLE)
    render_linear(p, s, f"{OUTDIR}/sun_year_draft_{p['key']}_linear.png")
