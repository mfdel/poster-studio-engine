"""
Generate the Etsy listing images for FAM-002, the Halloween night sheet.

FAM-002 is NOT a poster. It is a plain print-at-home sheet on US Letter or A4
that a child carries on the trick-or-treat walk and writes on. Every image here
has to say that: printer paper, a marker, a clipboard, a doorstep at night --
never a framed print on a wall.

One version sells: the `band` map sheet plus the spotting sheet.

Every sheet in every image is a REAL render of a real address (Chestnut Street,
Salem, Massachusetts), so the mockups match what ships -- the shop compliance
rule.

Two sources are combined:
  - the rendered PDFs under output/halloween/_listing_demo_salem/ (220 DPI)
  - photoreal scenes from Gemini under brand/ai-photos/ (optional; a flat brand
    background is used for any scene that is missing)

Run:  uv run python studio/assets/make_halloween_listing_images.py
"""
from __future__ import annotations

from pathlib import Path

import fitz  # pymupdf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "output/halloween/_listing_demo_salem"
AI = ROOT / "posters/fam002-halloween-night/brand/ai-photos"
OUT = ROOT / "posters/fam002-halloween-night/brand/listing-photos"

W, H = 2000, 2500
DPI = 220

# ------------------------------------------------------------------ palette
# Straight from studio/themes/lantern.json -- the sheet and the card must read
# as one product.
PLUM = "#171220"
PLUM_2 = "#1e1829"
AMBER = "#eb8f3c"
CREAM = "#f4ece1"
MUTED = "#93849f"
LINE = "#413150"

F_SER = "/System/Library/Fonts/Supplemental/Iowan Old Style.ttc"
F_GEO = "/System/Library/Fonts/Supplemental/Georgia.ttf"
F_GEO_B = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"


def ser(size: int, bold: bool = False):
    try:
        return ImageFont.truetype(F_SER, size, index=1 if bold else 0)
    except Exception:
        return ImageFont.truetype(F_GEO_B if bold else F_GEO, size)


def geo(size: int, bold: bool = False):
    return ImageFont.truetype(F_GEO_B if bold else F_GEO, size)


# ------------------------------------------------------------------ sources
def sheet(theme: str, layout: str) -> Image.Image:
    """One rendered sheet, rasterised from its PDF at print resolution."""
    pdf = SRC / f"sofia_s_halloween_night_{theme}_Letter_{layout}_portrait.pdf"
    doc = fitz.open(pdf)
    pix = doc[0].get_pixmap(dpi=DPI)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    doc.close()
    return img


def scene(name: str) -> Image.Image | None:
    """A Gemini scene, cropped to fill 2000x2500. None when it was never made."""
    for ext in (".png", ".jpg", ".jpeg"):
        p = AI / f"{name}{ext}"
        if p.exists():
            im = Image.open(p).convert("RGB")
            s = max(W / im.width, H / im.height)
            im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
            x = (im.width - W) // 2
            y = (im.height - H) // 2
            return im.crop((x, y, x + W, y + H))
    return None


# ------------------------------------------------------------------ drawing
def fallback(dark: bool = True) -> Image.Image:
    """Brand background used when a Gemini scene is missing."""
    im = Image.new("RGB", (W, H), PLUM)
    d = ImageDraw.Draw(im)
    for i in range(0, H, 4):
        t = i / H
        d.rectangle([0, i, W, i + 4],
                    fill=(23 + int(14 * t), 18 + int(10 * t), 32 + int(16 * t)))
    return im


def drop(img: Image.Image, blur: int = 26, spread: int = 18,
         alpha: int = 150) -> Image.Image:
    """An RGBA sheet with a soft shadow baked behind it."""
    pad = blur * 3 + spread
    out = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle(
        [pad - spread // 3, pad + spread // 2,
         pad + img.width + spread // 3, pad + img.height + spread],
        fill=(0, 0, 0, alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(sh)
    out.alpha_composite(img.convert("RGBA"), (pad, pad))
    return out


def place(base: Image.Image, sh: Image.Image, cx: int, cy: int,
          width: int, angle: float = 0.0, edge: bool = False) -> None:
    """Paste a sheet, scaled to `width`, rotated, centred on (cx, cy).

    `edge` strokes a hairline around the paper. A full-bleed dark sheet on the
    dark brand ground has no visible outline without it.
    """
    s = width / sh.width
    sh = sh.resize((width, round(sh.height * s)), Image.LANCZOS)
    if edge:
        sh = sh.copy()
        ImageDraw.Draw(sh).rectangle([0, 0, sh.width - 1, sh.height - 1],
                                     outline=MUTED, width=3)
    sh = drop(sh)
    if angle:
        sh = sh.rotate(angle, resample=Image.BICUBIC, expand=True)
    base.paste(sh, (cx - sh.width // 2, cy - sh.height // 2), sh)


def text(d: ImageDraw.ImageDraw, xy, s: str, font, fill, anchor="la",
         tracking: float = 0.0):
    if not tracking:
        d.text(xy, s, font=font, fill=fill, anchor=anchor)
        return
    total = sum(d.textlength(ch, font=font) + tracking for ch in s) - tracking
    x, y = xy
    if anchor[0] == "m":
        x -= total / 2
    elif anchor[0] == "r":
        x -= total
    for ch in s:
        d.text((x, y), ch, font=font, fill=fill, anchor="l" + anchor[1])
        x += d.textlength(ch, font=font) + tracking


def wrap(d, s, font, max_w):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        t = f"{cur} {w_}".strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def eyebrow(d, y, s, fill=AMBER):
    text(d, (W // 2, y), s.upper(), geo(34, True), fill, "ma", tracking=8)


def veil(im: Image.Image, top: int, height: int, alpha: int = 170) -> None:
    """Darken a band of the photo so type stays readable on top of it."""
    band = im.crop((0, top, W, top + height)).convert("RGBA")
    band = Image.alpha_composite(band, Image.new("RGBA", (W, height),
                                                 (23, 18, 32, alpha)))
    im.paste(band.convert("RGB"), (0, top))


def save(im: Image.Image, name: str):
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / name
    im.convert("RGB").save(p, quality=95)
    print(f"  {p.relative_to(ROOT)}")


# ------------------------------------------------------------------ the cards
def c01_hero():
    im = scene("s1-table-flatlay") or fallback()
    place(im, sheet("lantern", "band"), W // 2, int(H * 0.53), 1120, angle=-2.5)
    veil(im, 0, 330, 165)
    d = ImageDraw.Draw(im)
    eyebrow(d, 88, "Print it at home · made for your street")
    text(d, (W // 2, 152), "Our Halloween Night", ser(118), CREAM, "ma")
    save(im, "01-hero.jpg")


def c02_two_sheets():
    im = fallback()
    d = ImageDraw.Draw(im)
    eyebrow(d, 120, "Two sheets in the pack")
    text(d, (W // 2, 250), "The map of your streets,", ser(88), CREAM, "ma")
    text(d, (W // 2, 356), "and the spotting game", ser(88), CREAM, "ma")
    place(im, sheet("lantern", "band"), 580, 1290, 820, angle=-3, edge=True)
    place(im, sheet("lantern", "bonus"), 1420, 1330, 820, angle=3, edge=True)
    text(d, (580, 2050), "YOUR STREETS", geo(40, True), AMBER, "ma", tracking=6)
    text(d, (1420, 2090), "16 THINGS TO SPOT", geo(40, True), AMBER, "ma", tracking=6)
    text(d, (W // 2, 2270),
         "Both sheets are in the pack. Neither one costs extra.",
         geo(44), MUTED, "ma")
    save(im, "02-two-sheets.jpg")


def c03_print_at_home():
    im = scene("s5-print-at-home") or fallback()
    place(im, sheet("ink", "band"), W // 2, int(H * 0.56), 1040, angle=2)
    veil(im, 0, 340, 170)
    d = ImageDraw.Draw(im)
    eyebrow(d, 92, "No frame, no shipping, no waiting")
    text(d, (W // 2, 158), "Plain paper. Your printer.", ser(96), CREAM, "ma")
    save(im, "03-print-at-home.jpg")


def c04_two_versions():
    im = fallback()
    d = ImageDraw.Draw(im)
    eyebrow(d, 110, "Both versions, one price")
    text(d, (W // 2, 190), "Print the light one.", ser(96), CREAM, "ma")
    text(d, (W // 2, 300), "Keep the dark one.", ser(96), AMBER, "ma")
    place(im, sheet("lantern", "band"), 545, 1300, 860, angle=-2, edge=True)
    place(im, sheet("ink", "band"), 1455, 1300, 860, angle=2, edge=True)
    text(d, (545, 1930), "LANTERN", geo(42, True), AMBER, "ma", tracking=7)
    text(d, (1455, 1930), "LIGHT", geo(42, True), AMBER, "ma", tracking=7)
    d.rounded_rectangle([150, 2050, W - 150, 2380], 26,
                        fill=PLUM_2, outline=LINE, width=3)
    for i, ln in enumerate([
            "A full dark page eats ink and wets plain paper.",
            "Print the light version. The dark one is for the screen."]):
        text(d, (W // 2, 2130 + i * 78), ln, geo(48), CREAM, "ma")
    save(im, "04-two-versions.jpg")


def c05_carry_it():
    im = scene("s7-clipboard") or fallback()
    place(im, sheet("ink", "band"), W // 2, int(H * 0.52), 940, angle=0.8)
    veil(im, H - 400, 400, 175)
    d = ImageDraw.Draw(im)
    text(d, (W // 2, H - 300), "Clip it on. Fold it.", ser(86), CREAM, "ma")
    text(d, (W // 2, H - 195), "Take it with you.", ser(86), AMBER, "ma")
    save(im, "05-carry-it.jpg")


def c06_night_street():
    im = scene("s6-night-street") or fallback()
    place(im, sheet("ink", "band"), W // 2, int(H * 0.50), 900, angle=-4)
    veil(im, H - 420, 420, 175)
    d = ImageDraw.Draw(im)
    text(d, (W // 2, H - 320), "Filled in on the doorstep,", ser(82), CREAM, "ma")
    text(d, (W // 2, H - 215), "not at a desk.", ser(82), AMBER, "ma")
    save(im, "06-night-street.jpg")


def c07_map_closeup():
    src = sheet("lantern", "band")
    # The band layout puts a title strip across the top and all the writing in a
    # footer band, so the clear map runs from about 0.08 to 0.66 of the page.
    cw = int(src.width * 0.55)
    ch = int(cw * H / W)
    x = (src.width - cw) // 2
    y = max(0, int(src.height * 0.3675) - ch // 2)
    im = src.crop((x, y, x + cw, y + ch)).resize((W, H), Image.LANCZOS)
    veil(im, 0, 430, 185)
    d = ImageDraw.Draw(im)
    eyebrow(d, 96, "Your actual streets and houses")
    text(d, (W // 2, 160), "Every house on your block,", ser(84), CREAM, "ma")
    # Not "marked in amber": the light file a buyer actually prints marks home in
    # ink, not amber, and the claim has to hold for both files in the pack.
    text(d, (W // 2, 262), "and yours marked at the door.", ser(84), AMBER, "ma")
    veil(im, H - 240, 240, 185)
    d = ImageDraw.Draw(im)
    text(d, (W // 2, H - 165), "Map data © OpenStreetMap contributors",
         geo(42), MUTED, "ma")
    save(im, "07-map-closeup.jpg")


def c08_what_you_get():
    im = fallback()
    d = ImageDraw.Draw(im)
    eyebrow(d, 130, "What lands in your inbox")
    text(d, (W // 2, 210), "8 print-ready files", ser(104), CREAM, "ma")
    rows = [
        ("Your street map sheet", "US Letter + A4, dark and light"),
        ("The spotting game sheet", "US Letter + A4, dark and light"),
        ("Print-ready PDF", "300+ DPI, sharp on any home printer"),
        ("A how-to-print note", "which file to use, and on what paper"),
        ("Your house marked", "plus your title and your date"),
        ("Nothing is posted to you", "this is a pack you print at home"),
    ]
    y = 500
    for title, sub in rows:
        d.rounded_rectangle([150, y, W - 150, y + 270], 26,
                            fill=PLUM_2, outline=LINE, width=3)
        d.ellipse([210, y + 108, 262, y + 160], fill=AMBER)
        text(d, (310, y + 72), title, ser(64), CREAM, "la")
        text(d, (310, y + 162), sub, geo(44), MUTED, "la")
        y += 310
    save(im, "08-what-you-get.jpg")


def c09_how_it_works():
    im = fallback()
    d = ImageDraw.Draw(im)
    eyebrow(d, 140, "Made to order, in three steps")
    text(d, (W // 2, 220), "How it works", ser(110), CREAM, "ma")
    steps = [
        ("1", "You order and send your address",
         "Plus the title you want and the date."),
        ("2", "We draw your map by hand",
         "Your streets, your houses, your front door marked. Usually 1-2 days."),
        ("3", "We send your files by Etsy message",
         "You print at home on US Letter or A4, and hand it over with a crayon."),
    ]
    y = 560
    for n, title, sub in steps:
        d.rounded_rectangle([150, y, W - 150, y + 460], 30,
                            fill=PLUM_2, outline=LINE, width=3)
        d.ellipse([225, y + 60, 375, y + 210], outline=AMBER, width=6)
        text(d, (300, y + 128), n, ser(86), AMBER, "mm")
        text(d, (430, y + 92), title, ser(62), CREAM, "la")
        for i, ln in enumerate(wrap(d, sub, geo(46), W - 620)):
            text(d, (430, y + 200 + i * 66), ln, geo(46), MUTED, "la")
        y += 530
    text(d, (W // 2, 2330),
         "Nothing is delivered automatically. Every map is drawn for one address.",
         geo(44), MUTED, "ma")
    save(im, "09-how-it-works.jpg")


def c10_honest_note():
    im = fallback()
    d = ImageDraw.Draw(im)
    eyebrow(d, 300, "Please read this before you buy")
    text(d, (W // 2, 400), "This sheet does NOT", ser(112), CREAM, "ma")
    text(d, (W // 2, 530), "show which houses", ser(112), AMBER, "ma")
    text(d, (W // 2, 660), "give out treats.", ser(112), AMBER, "ma")
    d.line([400, 850, W - 400, 850], fill=LINE, width=4)
    body = [
        "Nobody can know that before the evening.",
        "A porch light goes on when a neighbour decides it does.",
        "",
        "This is a keepsake of the night your child walked,",
        "not a promise about it.",
        "",
        "Please always walk with your child.",
    ]
    y = 960
    for ln in body:
        if ln:
            text(d, (W // 2, y), ln, geo(56),
                 AMBER if ln.startswith("Please") else CREAM, "ma")
        y += 96
    d.rounded_rectangle([300, 1780, W - 300, 2180], 30,
                        fill=PLUM_2, outline=AMBER, width=4)
    text(d, (W // 2, 1870), "What it DOES show", geo(44, True), AMBER, "ma", tracking=6)
    for i, ln in enumerate(["Your streets. Your houses. Your front door.",
                            "And room for your child to fill in the rest."]):
        text(d, (W // 2, 1970 + i * 78), ln, geo(50), CREAM, "ma")
    save(im, "10-honest-note.jpg")


# --- spares. Swap one of these in for a slot above; Etsy takes 10 photos. ---
def c11_fridge():
    sc = scene("s4-fridge")
    if sc is None:
        return
    place(sc, sheet("ink", "band"), W // 2, int(H * 0.50), 980, angle=-1.5)
    veil(sc, H - 330, 330, 165)
    d = ImageDraw.Draw(sc)
    text(d, (W // 2, H - 235), "Filled in, and up on the fridge", ser(80), CREAM, "ma")
    text(d, (W // 2, H - 130), "by the first of November.", ser(80), AMBER, "ma")
    save(sc, "11-fridge.jpg")


def c12_mood():
    sc = scene("s3-porch-mood")
    if sc is None:
        return
    veil(sc, H - 560, 560, 170)
    d = ImageDraw.Draw(sc)
    text(d, (W // 2, H - 440), "The walk is over in an hour.", ser(84), CREAM, "ma")
    text(d, (W // 2, H - 330), "The sheet is what is left.", ser(84), AMBER, "ma")
    text(d, (W // 2, H - 180),
         "Print a new one next year and put the two side by side.",
         geo(46), MUTED, "ma")
    save(sc, "12-mood.jpg")


def main():
    want = ("s1-table-flatlay", "s5-print-at-home", "s7-clipboard", "s6-night-street")
    missing = [n for n in want if scene(n) is None]
    if missing:
        print(f"NOTE: Gemini scenes missing, using the brand background: {missing}")
    print(f"Writing to {OUT.relative_to(ROOT)}")
    for fn in (c01_hero, c02_two_sheets, c03_print_at_home, c04_two_versions,
               c05_carry_it, c06_night_street, c07_map_closeup, c08_what_you_get,
               c09_how_it_works, c10_honest_note,
               c11_fridge, c12_mood):
        fn()


if __name__ == "__main__":
    main()
