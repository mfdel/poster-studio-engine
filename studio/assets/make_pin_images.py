"""
Generate Pinterest pin images (2:3, 1000x1500) for Hopscotch Maps.

Pinterest optimises for 2:3; the existing Etsy listing photos are 4:5. This script builds a
pin-native set from the room-context photos in `posters/fam001-playground-map/brand/ai-photos/`,
adding the keyword kicker + emotional headline that a pin needs to be readable at ~200px wide.

Layout: cream text band on the top third (keyword kicker + emotional headline) over a
full-bleed room photo. The 4:5 info graphics in `listing-photos/` are deliberately not reused —
their body type is unreadable at Pinterest feed size.

Run:  uv run python studio/assets/make_pin_images.py
Out:  posters/fam001-playground-map/brand/pinterest-pins/
"""
import os

from PIL import Image, ImageDraw, ImageFont, ImageOps

# ---------------------------------------------------------------- paths
AI = "posters/fam001-playground-map/brand/ai-photos"

OUT = "posters/fam001-playground-map/brand/pinterest-pins"
os.makedirs(OUT, exist_ok=True)

W, H = 1000, 1500

# ---------------------------------------------------------------- palette (shared with the mockups)
CREAM = "#FBF6EC"
BROWN = "#4A3B2A"

MUTED = "#9A8A72"

# ---------------------------------------------------------------- fonts
F_CHALK = "/System/Library/Fonts/Supplemental/ChalkboardSE.ttc"
F_TREB = "/System/Library/Fonts/Supplemental/Trebuchet MS.ttf"


def head(size):
    for idx in (1, 0):
        try:
            return ImageFont.truetype(F_CHALK, size, index=idx)
        except Exception:
            continue
    return ImageFont.truetype(F_TREB, size)


def body(size):
    return ImageFont.truetype(F_TREB, size)


def center(d, cx, y, txt, fnt, fill, tracking=0):
    if tracking:
        widths = [d.textlength(c, font=fnt) for c in txt]
        total = sum(widths) + tracking * (len(txt) - 1)
        x = cx - total / 2
        for c, w in zip(txt, widths):
            d.text((x, y), c, font=fnt, fill=fill)
            x += w + tracking
        return
    w = d.textlength(txt, font=fnt)
    d.text((cx - w / 2, y), txt, font=fnt, fill=fill)


# ---------------------------------------------------------------- layouts
BAND = 340          # cream text band on top
FOOT = 96           # brand strip at the bottom
PHOTO_H = H - BAND - FOOT


def pin_photo(src, kicker, lines, out_name, out_dir=None):
    out_dir = out_dir or OUT
    canvas = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(canvas)

    photo = Image.open(src).convert("RGB")
    photo = ImageOps.fit(photo, (W, PHOTO_H), Image.LANCZOS, centering=(0.5, 0.45))
    canvas.paste(photo, (0, BAND))

    center(d, W / 2, 74, kicker.upper(), body(26), MUTED, tracking=4.5)

    size = 74 if max(len(x) for x in lines) <= 22 else 62
    fnt = head(size)
    y = 138 if len(lines) > 1 else 172
    for line in lines:
        center(d, W / 2, y, line, fnt, BROWN)
        y += size + 16

    center(d, W / 2, H - FOOT + 30, "hopscotchmaps  ·  etsy", body(28), MUTED, tracking=2.5)

    os.makedirs(out_dir, exist_ok=True)
    path = f"{out_dir}/{out_name}"
    canvas.save(path, quality=92)
    print("wrote", path)
    return path


G =f"{AI}/watermark-removed-Gemini_Generated_Image"
G2 = f"{AI}/20260802/watermark-removed-Gemini_Generated_Image"

# Every kicker is a phrase measured in `studio/research/etsy_keyword_evidence_20260816.md`,
# with its monthly search volume in the comment. The pre-eRank kickers were replaced on
# 2026-08-16: `personalized playground map` and `custom neighborhood map print` both measure 0
# searches a month. The niche words now live in the headline and the pin description instead,
# where they cost no discovery.
PINS = [
    (f"{G}_zy0wbzy0wbzy0wbz.png", "New baby gift",                  # 1,310
     ["The new baby gift", "nobody else brings"], "p01-new-baby.jpg"),
    (f"{G}_cxhpqbcxhpqbcxhp.png", "Baby shower gift",               # 4,420
     ["A baby shower gift", "that isn't on the list"], "p02-baby-shower.jpg"),
    (f"{G}_f7zvjzf7zvjzf7zv.png", "Nursery wall art",               # 4,570
     ["Nursery art with", "an actual story"], "p03-nursery.jpg"),
    (f"{G}_5yjlka5yjlka5yjl.png", "Kids wall art",                  # 1,200
     ["Let them pick", "where you play"], "p04-screen-free.jpg"),
    (f"{G}_edeoskedeoskedeo.png", "Personalized wall art",          # 2,350
     ["Every playground", "you'll grow up loving"], "p05-dad.jpg"),
    (f"{G2}_5x0csm5x0csm5x0c.png", "First birthday gift",           # 1,200
     ["Year one,", "mapped"], "p06-first-birthday.jpg"),
    (f"{AI}/20260802/ChatGPT Image 2 Ağu 2026 07_08_10.png", "Personalized gift",   # 18,820
     ["From the grandkids,", "for the wall"], "p07-grandparents.jpg"),
    (f"{G2}_9zx0lu9zx0lu9zx0.png", "Playroom wall art",             # 1,200
     ["Turn Saturday into", "a small adventure"], "p08-adventure.jpg"),
    (f"{G2}_ca3b7wca3b7wca3b.png", "Custom map print",              # 1,200
     ["Print-ready file", "in 2-3 days"], "p09-what-you-get.jpg"),
    (f"{AI}/20260802/ChatGPT Image 2 Ağu 2026 07_06_07.png", "Map wall art",        # 1,200
     ["Your own streets,", "hand-illustrated"], "p10-living-room.jpg"),
    # p11 replaces the original hero pin, which Pinterest turned into a product pin with an
    # uneditable www.etsy.com link. The old pin stays up; this one carries the Share & Save URL.
    (f"{AI}/hero-framed-wall-textfixed.jpg", "City map print",      # 1,200
     ["Your streets, your", "playgrounds, framed"], "p11-hero-neighborhood.jpg"),
]

# ---------------------------------------------------------------- PRT-006 sun-year pins
# The sun poster is a dark 5:7 artwork, so `ImageOps.fit` would crop the city name off the
# top. These pins letterbox the whole poster onto its own background colour instead, and keep
# the cream band, the fonts and the footer identical so the two products read as one shop.
SUN = "posters/prt006-sun-year/brand"
SUN_OUT = f"{SUN}/pinterest-pins"

NIGHT = (27, 20, 36)        # the poster's own background


def pin_poster(src, kicker, lines, out_name):
    os.makedirs(SUN_OUT, exist_ok=True)
    canvas = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(canvas)

    panel = Image.new("RGB", (W, PHOTO_H), NIGHT)
    art = Image.open(src).convert("RGB")
    art = ImageOps.contain(art, (W, PHOTO_H), Image.LANCZOS)
    panel.paste(art, ((W - art.width) // 2, (PHOTO_H - art.height) // 2))
    canvas.paste(panel, (0, BAND))

    center(d, W / 2, 74, kicker.upper(), body(26), MUTED, tracking=4.5)

    size = 74 if max(len(x) for x in lines) <= 22 else 62
    fnt = head(size)
    y = 138 if len(lines) > 1 else 172
    for line in lines:
        center(d, W / 2, y, line, fnt, BROWN)
        y += size + 16

    center(d, W / 2, H - FOOT + 30, "hopscotchmaps  ·  etsy", body(28), MUTED, tracking=2.5)

    path = f"{SUN_OUT}/{out_name}"
    canvas.save(path, quality=92)
    print("wrote", path)
    return path


S = f"{SUN}/samples/sunyear"

# Deliberately five, not eleven. The plain-ring cities (Oslo, Copenhagen, Edinburgh,
# Stockholm) are near-identical at feed size, and a board of near-duplicates reads as spam.
# Only one plain ring ships; the rest are the notched high-latitude shapes.
# Kickers rebuilt on 2026-08-16 from `studio/research/etsy_keyword_evidence_20260816.md`, with
# monthly search volume in the comment. The originals were invented, not measured: `midnight sun
# poster` was never tested, and `nordic wall art`, `scandinavian print` and `custom coordinates
# print` all measure 10 searches a month. The niche words moved into the headline and the pin
# description, where they cost no discovery.
SUN_PINS = [
    (f"{S}_tromso_ring.png", "Scandinavian wall art",       # 1,200
     ["Two months", "without a sunrise"], "s02-tromso.jpg"),
    (f"{S}_reykjavik_ring.png", "Personalized wall art",    # 2,350
     ["Where the light", "never sits still"], "s03-reykjavik.jpg"),
    (f"{S}_kiruna_ring.png", "Housewarming gift",           # 3,670
     ["The sun that", "forgets to set"], "s04-kiruna.jpg"),
    (f"{S}_stockholm_ring.png", "New home gift",            # 2,720
     ["Your city, your", "year, in gold"], "s05-stockholm.jpg"),
]

if __name__ == "__main__":
    for src, kicker, lines, name in PINS:
        pin_photo(src, kicker, lines, name)
    # the hero is a room photo, so it crops rather than letterboxes
    # `sunrise sunset wall art` measured under 20 searches against 18,652 competitors, KD 100.
    pin_photo(f"{SUN}/listing-photos/01-hero-framed.jpg", "Sunset wall art",   # 1,150
              ["A year of light,", "at your address"], "s01-hero.jpg", out_dir=SUN_OUT)
    for src, kicker, lines, name in SUN_PINS:
        pin_poster(src, kicker, lines, name)
