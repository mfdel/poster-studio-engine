"""PRT-006 Sun-Year Poster - Phase 2 build feasibility check.

Questions to answer:
 1. Can `astral` give sunrise/sunset for 365 days at any lat/lon, fast?
 2. What happens above the Arctic Circle (polar night / midnight sun)?
 3. Does the shape actually differ enough between latitudes to be "art"?
 4. Does a polar (spiral/ring) render read as an object, or as a chart?
"""
import datetime as dt
import os
import time
import math

from astral import LocationInfo
from astral.sun import sun
from zoneinfo import ZoneInfo

PLACES = [
    ("Malmo, SE",      55.6050, 13.0038,  "Europe/Stockholm"),
    ("Kiruna, SE",     67.8558, 20.2253,  "Europe/Stockholm"),  # above Arctic Circle
    ("Longyearbyen",   78.2232, 15.6469,  "Arctic/Longyearbyen"),
    ("London, UK",     51.5072, -0.1276,  "Europe/London"),
    ("Berlin, DE",     52.5200, 13.4050,  "Europe/Berlin"),
    ("New York, US",   40.7128, -74.0060, "America/New_York"),
    ("Singapore",       1.3521, 103.8198, "Asia/Singapore"),
    ("Sydney, AU",    -33.8688, 151.2093, "Australia/Sydney"),
]

YEAR = 2026


def frac_hours(t, tz):
    t = t.astimezone(tz)
    return t.hour + t.minute / 60 + t.second / 3600


def series(lat, lon, tzname, year=YEAR):
    """Return list of (date, sunrise_h, sunset_h, daylen_h, flag)."""
    tz = ZoneInfo(tzname)
    loc = LocationInfo("x", "y", tzname, lat, lon)
    out = []
    d = dt.date(year, 1, 1)
    while d.year == year:
        try:
            s = sun(loc.observer, date=d, tzinfo=tz)
            sr, ss = frac_hours(s["sunrise"], tz), frac_hours(s["sunset"], tz)
            daylen = (s["sunset"] - s["sunrise"]).total_seconds() / 3600
            out.append((d, sr, ss, daylen, "normal"))
        except ValueError as e:
            # astral raises for polar day/night
            msg = str(e).lower()
            flag = "midnight_sun" if "always above" in msg or "never sets" in msg else "polar_night"
            # crude: decide by solar declination vs latitude
            n = d.timetuple().tm_yday
            decl = -23.44 * math.cos(math.radians(360 / 365 * (n + 10)))
            flag = "midnight_sun" if (lat > 0) == (decl > 0) else "polar_night"
            out.append((d, None, None, 24.0 if flag == "midnight_sun" else 0.0, flag))
        d += dt.timedelta(days=1)
    return out


print(f"{'place':<16}{'days':>6}{'min_day':>9}{'max_day':>9}{'range':>8}{'polarN':>8}{'midSun':>8}{'secs':>8}")
print("-" * 72)
for name, lat, lon, tzn in PLACES:
    t0 = time.perf_counter()
    s = series(lat, lon, tzn)
    el = time.perf_counter() - t0
    dl = [r[3] for r in s]
    pn = sum(1 for r in s if r[4] == "polar_night")
    ms = sum(1 for r in s if r[4] == "midnight_sun")
    print(f"{name:<16}{len(s):>6}{min(dl):>9.2f}{max(dl):>9.2f}{max(dl)-min(dl):>8.2f}{pn:>8}{ms:>8}{el:>8.3f}")

# ---- visual test: does a polar ribbon read as art? ----
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

fig, axes = plt.subplots(1, 4, figsize=(20, 5.5), subplot_kw={"projection": "polar"})
for ax, (name, lat, lon, tzn) in zip(axes, [PLACES[0], PLACES[1], PLACES[6], PLACES[7]]):
    s = series(lat, lon, tzn)
    theta = np.linspace(0, 2 * np.pi, len(s), endpoint=False)
    # ring: inner radius = sunrise hour, outer radius = sunset hour, on a 0..24 radial axis
    rise = np.array([r[1] if r[1] is not None else (0.0 if r[4] == "midnight_sun" else 12.0) for r in s])
    setx = np.array([r[2] if r[2] is not None else (24.0 if r[4] == "midnight_sun" else 12.0) for r in s])
    ax.fill_between(theta, rise, setx, color="#F2C14E", linewidth=0)
    ax.set_facecolor("#12121A")
    ax.set_ylim(0, 24)
    ax.set_yticklabels([]); ax.set_xticklabels([])
    ax.grid(False); ax.spines["polar"].set_visible(False)
    ax.set_title(f"{name}  (lat {lat:.1f})", color="#333")
fig.patch.set_facecolor("white")
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sunyear_ring_test.png")
fig.savefig(out, dpi=110, bbox_inches="tight")
print("\nwrote", out)
