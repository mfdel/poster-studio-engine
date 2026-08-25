"""Generate the Etsy listing images for PRT-006 — the Sun-Year Poster.

Same recipe as `make_listing_mockups.py` (FAM-001): 2000x2500 (4:5) PIL images on the
product's own palette, no external service. The framed-on-wall helper is reused from
that module so both products' mockups share one frame/shadow treatment.

Inputs are the ring previews written by
`posters/prt006-sun-year/render_1b.py` into `posters/prt006-sun-year/brand/samples/`.

Run:  uv run python studio/assets/make_sunyear_listing_images.py
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_listing_mockups import W, H, framed, paste_with_shadow  # noqa: E402

SAMPLES = "posters/prt006-sun-year/brand/samples"
OUT = "posters/prt006-sun-year/brand/listing-photos"
os.makedirs(OUT, exist_ok=True)

# Palette — the poster's own (drafts/support.js), so the listing card and the artwork
# are unmistakably the same object.
BG = "#1B1424"
PANEL = "#231A2E"
CREAM = "#F3ECE2"
MUTED = "#8A7C93"
GOLD = "#E9B949"
EMBER = "#A4552F"
WOOD = "#CBA97A"

F_SERIF = "/System/Library/Fonts/Supplemental/Georgia.ttf"
F_SERIF_B = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
F_SERIF_I = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
F_MONO = "/System/Library/Fonts/Menlo.ttc"


def serif(size, bold=False, italic=False):
    return ImageFont.truetype(F_SERIF_B if bold else F_SERIF_I if italic else F_SERIF, size)


def mono(size):
    return ImageFont.truetype(F_MONO, size)


def ring(key, height):
    """A ring preview, scaled to `height` px."""
    img = Image.open(f"{SAMPLES}/sunyear_{key}_ring.png").convert("RGB")
    w = int(img.width * height / img.height)
    return img.resize((w, height), Image.LANCZOS)


def panel():
    c = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(c)
    m = 70
    d.rectangle([m, m, W - m, H - m], outline=EMBER, width=5)
    d.rectangle([m + 16, m + 16, W - m - 16, H - m - 16], outline=EMBER, width=2)
    return c, d


def center(d, cx, y, txt, fnt, fill, tracking=0):
    if tracking:
        widths = [d.textlength(ch, font=fnt) for ch in txt]
        x = cx - (sum(widths) + tracking * (len(txt) - 1)) / 2
        for ch, cw in zip(txt, widths):
            d.text((x, y), ch, font=fnt, fill=fill)
            x += cw + tracking
    else:
        d.text((cx - d.textlength(txt, font=fnt) / 2, y), txt, font=fnt, fill=fill)
    return y + fnt.size * 1.25


def block(d, cx, y, lines, fnt, fill, lead=1.5):
    for line in lines:
        y = center(d, cx, y, line, fnt, fill)
        y += fnt.size * (lead - 1.25)
    return y


# ------------------------------------------------------------------ 1. hero
def hero():
    framed(f"{SAMPLES}/sunyear_malmo_ring.png",
           "#2A2233", "#150F1E", WOOD, f"{OUT}/01-hero-framed.jpg",
           mat_w=52, frame_w=44, poster_h_frac=0.70)


# ------------------------------------------- 2. one shape per latitude (the proof)
def latitudes():
    c, d = panel()
    center(d, W / 2, 150, "YOUR LATITUDE, YOUR SHAPE", serif(66, bold=True), CREAM, tracking=6)
    center(d, W / 2, 250, "the higher you live, the wilder the year of light",
           serif(44, italic=True), MUTED)

    trio = [("malmo", "MALMÖ", "55.6° N"), ("reykjavik", "REYKJAVÍK", "64.1° N"),
            ("tromso", "TROMSØ", "69.6° N")]
    gap = 56
    row_w = 1720
    rh = int(((row_w - gap * (len(trio) - 1)) / len(trio)) * 1.4)  # sheets are 1:1.4
    imgs = [ring(k, rh) for k, _, _ in trio]
    total = sum(i.width for i in imgs) + gap * (len(imgs) - 1)
    x = (W - total) // 2
    top = 700
    for img, (_, name, lat) in zip(imgs, trio):
        paste_with_shadow(c, img, x, top, off=8, blur=18, alpha=90)
        d = ImageDraw.Draw(c)
        center(d, x + img.width / 2, top + rh + 50, name, serif(46, bold=True), CREAM)
        center(d, x + img.width / 2, top + rh + 120, lat, mono(34), GOLD)
        x += img.width + gap

    d = ImageDraw.Draw(c)
    block(d, W / 2, top + rh + 280, [
        "Every ring is computed from the real sunrises and sunsets",
        "at your coordinates — nothing here is decoration.",
    ], serif(40), MUTED)
    c.save(f"{OUT}/02-latitudes.jpg")
    print("saved", f"{OUT}/02-latitudes.jpg")


# ------------------------------------------------------------ 3. what you get
def what_you_get():
    c, d = panel()
    center(d, W / 2, 170, "WHAT YOU GET", serif(72, bold=True), CREAM, tracking=6)

    img = ring("kiruna", 1120)
    paste_with_shadow(c, img, (W - img.width) // 2, 330, off=10, blur=20, alpha=90)
    d = ImageDraw.Draw(c)

    rows = [
        ("Your place", "the city or address you choose, named in full"),
        ("Your coordinates", "printed to four decimals, the way a keepsake should be"),
        ("Your line", "one line of your own words along the foot of the print"),
        ("Your year of light", "365 real sunrises and sunsets, drawn as one ring"),
    ]
    y = 1590
    for title, sub in rows:
        d.ellipse([300, y + 14, 336, y + 50], fill=GOLD)
        d.text((380, y), title, font=serif(46, bold=True), fill=CREAM)
        d.text((380, y + 62), sub, font=serif(38), fill=MUTED)
        y += 155
    c.save(f"{OUT}/03-what-you-get.jpg")
    print("saved", f"{OUT}/03-what-you-get.jpg")


# ------------------------------------------------------------- 4. how it works
def how_it_works():
    c, d = panel()
    center(d, W / 2, 200, "HOW IT WORKS", serif(72, bold=True), CREAM, tracking=6)

    steps = [
        ("1", "You order", "Pick digital, poster or framed, and tell us your place,\n"
                           "the year you want, and your one line of text."),
        ("2", "We draw your year", "We compute every sunrise and sunset at your\n"
                                   "coordinates and hand-set the type around it."),
        ("3", "You approve", "We send you a preview by Etsy message.\n"
                             "Change anything you like before it prints."),
        ("4", "It arrives", "Digital files come by message; posters and frames are\n"
                            "printed near you and shipped to your door."),
    ]
    y = 430
    for num, title, body in steps:
        d.ellipse([250, y, 250 + 96, y + 96], fill=EMBER)
        d.text((250 + 48 - d.textlength(num, font=serif(52, bold=True)) / 2, y + 20),
               num, font=serif(52, bold=True), fill=CREAM)
        d.text((400, y + 4), title, font=serif(52, bold=True), fill=GOLD)
        for i, line in enumerate(body.split("\n")):
            d.text((400, y + 78 + i * 56), line, font=serif(38), fill=MUTED)
        y += 250

    center(d, W / 2, 1500, "Made to order — never an automatic download.",
           serif(40, italic=True), CREAM)

    img = ring("stockholm", 700)
    paste_with_shadow(c, img, (W - img.width) // 2, 1640, off=8, blur=18, alpha=90)
    c.save(f"{OUT}/04-how-it-works.jpg")
    print("saved", f"{OUT}/04-how-it-works.jpg")


# --------------------------------------------------------------- 5. size guide
def size_guide():
    c, d = panel()
    center(d, W / 2, 170, "THREE SIZES", serif(72, bold=True), CREAM, tracking=6)
    center(d, W / 2, 280, "printed near you, ready for the wall", serif(42, italic=True), MUTED)

    # Sheets drawn to true relative proportion, sitting on one baseline.
    sizes = [("30 x 40 cm", 30, 40), ("40 x 50 cm", 40, 50), ("50 x 70 cm", 50, 70)]
    gap = 80
    unit = (1560 - gap * (len(sizes) - 1)) / sum(s[1] for s in sizes)  # px per cm
    base_y = 1340
    x = (W - (sum(s[1] * unit for s in sizes) + gap * (len(sizes) - 1))) / 2
    for label, w_cm, h_cm in sizes:
        w, h = w_cm * unit, h_cm * unit
        d.rectangle([x, base_y - h, x + w, base_y], fill=PANEL, outline=GOLD, width=4)
        r = w * 0.30
        cy = base_y - h * 0.52
        d.ellipse([x + w / 2 - r, cy - r, x + w / 2 + r, cy + r], fill=GOLD)
        d.ellipse([x + w / 2 - r * 0.30, cy - r * 0.30,
                   x + w / 2 + r * 0.30, cy + r * 0.30], fill=PANEL)
        center(d, x + w / 2, base_y + 34, label, serif(38, bold=True), CREAM)
        x += w + gap

    block(d, W / 2, 1560, [
        "Digital: one purchase, print-ready files for all three sizes",
        "(300+ DPI PDF, plus 12x16, 16x20 and 20x28 inch).",
        "",
        "Poster & framed: printed on 170gsm silk paper by our",
        "print partner and shipped from within your region.",
    ], serif(40), MUTED)
    c.save(f"{OUT}/05-size-guide.jpg")
    print("saved", f"{OUT}/05-size-guide.jpg")


# -------------------------------------------------------------- 6. honest note
def honest_note():
    c, d = panel()
    center(d, W / 2, 200, "AN HONEST NOTE", serif(72, bold=True), CREAM, tracking=6)

    notes = [
        ("Made to order, not an automatic download.",
         "We draw your poster after you order and send it by Etsy message."),
        ("The digital option ships nothing.",
         "You get files to print at home or at a local print shop."),
        ("Colours shift a little in print.",
         "Screens glow; paper does not. Golds print slightly warmer."),
        ("It only works far from the equator.",
         "Below about 35° the year barely changes and your ring would be a\n"
         "plain circle — we would rather tell you than sell you that."),
    ]
    y = 430
    for title, body in notes:
        d.text((250, y), title, font=serif(46, bold=True), fill=GOLD)
        for i, line in enumerate(body.split("\n")):
            d.text((250, y + 66 + i * 54), line, font=serif(38), fill=MUTED)
        y += 250 if "\n" not in body else 300

    img = ring("edinburgh", 620)
    paste_with_shadow(c, img, (W - img.width) // 2, 1720, off=8, blur=18, alpha=90)
    c.save(f"{OUT}/06-honest-note.jpg")
    print("saved", f"{OUT}/06-honest-note.jpg")


# ------------------------------------------------------- 7. the poster, flat
def flat(key, index):
    """A single ring on its own ground — the closest thing to 'the product itself'."""
    c = Image.new("RGB", (W, H), BG)
    img = ring(key, int(H * 0.86))
    paste_with_shadow(c, img, (W - img.width) // 2, int(H * 0.07), off=10, blur=24, alpha=100)
    out = f"{OUT}/{index:02d}-flat-{key}.jpg"
    c.save(out)
    print("saved", out)


if __name__ == "__main__":
    hero()
    latitudes()
    what_you_get()
    how_it_works()
    size_guide()
    honest_note()
    flat("malmo", 7)
    flat("tromso", 8)
    flat("reykjavik", 9)
