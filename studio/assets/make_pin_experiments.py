"""
Pin-image experiments — BL-010 (sun pin rebuild) and BL-007 (Christmas set).

This is deliberately a SEPARATE file from `make_pin_images.py`. That file generates the pins that
are already live, and a shop run must not change live output as a side effect. Anything here that
the founder approves folds back into `make_pin_images.py` later.

Both experiments reuse the shipped pin furniture — the cream band, Chalkboard headline, Trebuchet
kicker, the `hopscotchmaps · etsy` footer — so a new pin still reads as the same shop.

BL-010, the diagnosis this implements
-------------------------------------
`fam-nursery` (p03) holds the account's only outbound click, at a 20.0% click rate. Every
`sun2-*` pin sits at 0. Measured differences, at Pinterest feed width:

1. p03 shows a ROOM — nursery, wooden toys, window light. The sun pins show a bare specimen.
2. p03 is bright and warm. Three of four sun pins are about 70% near-black, which reads as a
   dark blob in a white feed.
3. The four sun pins share one silhouette: a gold ring, centred, on near-black. At feed size
   Tromso and Kiruna are the same picture.
4. `pin_poster` letterboxes a 5:7 ring into a 1000x1064 panel. The art lands at 760x1064, so
   240px of flat dark bar, and the art covers 54% of the pin against 71% for a room photo.

The fix below attacks 2 and 4 directly, and 3 by giving the sun set a second silhouette. It only
approximates 1: a warm wall with a framed print is not a photographed room. A real room scene needs
a generated photo, which is the follow-up.

Run:  uv run python studio/assets/make_pin_experiments.py
Out:  posters/prt006-sun-year/brand/pinterest-pins/   (s06-*)
      posters/fam001-playground-map/brand/pinterest-pins/  (x01-*, x02-*)
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageOps

from make_pin_images import (BAND, FOOT, FOOT as _FOOT, H, MUTED, PHOTO_H, W,
                             BROWN, CREAM, body, center, head)

# ---------------------------------------------------------------- palette
MATCOL = "#FBFAF6"
WOOD = "#CBA97A"          # the only frame the shop sells
WALL_TOP = "#EFE7DA"      # warm light wall, same family as CREAM
WALL_BOT = "#DCD0BD"

SUN_OUT = "posters/prt006-sun-year/brand/pinterest-pins"
FAM_OUT = "posters/fam001-playground-map/brand/pinterest-pins"
SUN_SAMPLES = "posters/prt006-sun-year/brand/samples"
FAM_AI = "posters/fam001-playground-map/brand/ai-photos"


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def wall_panel(w, h, top=WALL_TOP, bottom=WALL_BOT, floor_frac=0.17):
    """A lit wall meeting a surface.

    A plain vertical gradient reads as a cream card, not a room. Three cues fix that cheaply: a
    floor band at the foot, a slightly darker seam where wall meets floor, and a soft light wash
    from the upper left so the wall is not evenly lit.
    """
    img = Image.new("RGB", (w, h), top)
    d = ImageDraw.Draw(img)
    tr, br = _hex(top), _hex(bottom)
    wall_h = int(h * (1 - floor_frac))
    for y in range(wall_h):
        t = y / max(wall_h - 1, 1)
        d.line([(0, y), (w, y)],
               fill=tuple(int(tr[i] + (br[i] - tr[i]) * t) for i in range(3)))

    # floor: warmer and darker than the wall, so the seam reads as a corner
    fl_top, fl_bot = _hex("#C9B698"), _hex("#B7A181")
    for y in range(wall_h, h):
        t = (y - wall_h) / max(h - wall_h - 1, 1)
        d.line([(0, y), (w, y)],
               fill=tuple(int(fl_top[i] + (fl_bot[i] - fl_top[i]) * t) for i in range(3)))
    d.line([(0, wall_h), (w, wall_h)], fill="#A8926F", width=3)

    # light wash from the upper left
    wash = Image.new("L", (w, h), 0)
    wd = ImageDraw.Draw(wash)
    wd.polygon([(0, 0), (int(w * 0.72), 0), (0, int(h * 0.66))], fill=64)
    img = Image.composite(Image.new("RGB", (w, h), "#FFFDF6"), img,
                          wash.filter(ImageFilter.GaussianBlur(120)))
    return img


def framed_panel(poster_path, poster_h_frac=0.95, mat_w=16, frame_w=22):
    """A framed poster on a warm wall, sized to the pin's photo panel.

    Unlike `pin_poster`, nothing is letterboxed onto the poster's own dark background, so the
    pin carries no flat black bars and the frame reads as an object on a wall.
    """
    floor_frac = 0.12
    panel = wall_panel(W, PHOTO_H, floor_frac=floor_frac)
    wall_h = int(PHOTO_H * (1 - floor_frac))
    poster = Image.open(poster_path).convert("RGB")
    pw, ph = poster.size

    th = int(wall_h * poster_h_frac)
    tw = int(pw * th / ph)
    # keep the whole frame inside the panel width
    max_tw = W - 2 * (mat_w + frame_w) - 40
    if tw > max_tw:
        tw = max_tw
        th = int(ph * tw / pw)
    poster = poster.resize((tw, th), Image.LANCZOS)

    fw = tw + 2 * mat_w + 2 * frame_w
    fh = th + 2 * mat_w + 2 * frame_w
    fx = (W - fw) // 2
    # hang it on the wall, clear of the floor seam
    fy = max(int(PHOTO_H * 0.03), (wall_h - fh) // 2)

    canvas = panel.convert("RGBA")
    shadow = Image.new("RGBA", (W, PHOTO_H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rectangle(
        [fx + 16, fy + 26, fx + fw + 16, fy + fh + 30], fill=(60, 50, 40, 105))
    canvas = Image.alpha_composite(canvas, shadow.filter(ImageFilter.GaussianBlur(24)))

    d = ImageDraw.Draw(canvas)
    d.rectangle([fx, fy, fx + fw, fy + fh], fill=WOOD)
    d.line([(fx, fy), (fx + fw, fy)], fill="#E2C79B", width=3)
    d.line([(fx, fy), (fx, fy + fh)], fill="#E2C79B", width=3)
    d.line([(fx, fy + fh), (fx + fw, fy + fh)], fill="#A98A5F", width=3)
    d.line([(fx + fw, fy), (fx + fw, fy + fh)], fill="#A98A5F", width=3)

    mx, my = fx + frame_w, fy + frame_w
    d.rectangle([mx, my, fx + fw - frame_w, fy + fh - frame_w], fill=MATCOL)
    px, py = mx + mat_w, my + mat_w
    d.rectangle([px - 2, py - 2, px + tw + 2, py + th + 2], outline="#D8D2C4", width=2)
    canvas = canvas.convert("RGB")
    canvas.paste(poster, (px, py))
    return canvas, (tw * th) / (W * H)


def compose(panel, kicker, lines, out_dir, out_name):
    """Drop a finished photo panel into the shop's standard pin furniture."""
    canvas = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(canvas)
    canvas.paste(panel, (0, BAND))

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
    return path


def photo_panel(src):
    """Full-bleed room photo, the p03 pattern."""
    photo = Image.open(src).convert("RGB")
    return ImageOps.fit(photo, (W, PHOTO_H), Image.LANCZOS, centering=(0.5, 0.45))


# ---------------------------------------------------------------- BL-010
# One new sun pin, on the light-wall pattern. `minimalist wall art` measures 2,210 a month, the
# highest-volume phrase measured for either product, and no pin uses it yet. Evidence:
# studio/research/etsy_keyword_evidence_20260816.md, Run 3.
BL010 = [
    (f"{SUN_SAMPLES}/sunyear_kiruna_ring.png", "Minimalist wall art",   # 2,210
     ["The sun that", "forgets to set"], "s06-kiruna-light.jpg"),
]

# ---------------------------------------------------------------- BL-007
# Christmas set. Every kicker is already measured; the Christmas hook lives in the headline,
# where it costs no discovery. Christmas-specific phrases are NOT yet measured in eRank, so no
# Christmas phrase is used as a kicker. Publish from 2026-10-01, never before.
XMAS_FAM = [
    (f"{FAM_AI}/20260802/ChatGPT Image 2 Ağu 2026 07_08_10.png", "Personalized gift",   # 18,820
     ["The gift they", "unwrap slowly"], "x01-xmas-grandparents.jpg"),
    # NOT the f7zvjz nursery photo: the live p03 pin already uses it, and two pins with one photo
    # on one board read as spam. w3tls5 is unused by any live pin — hands holding the print in
    # window light, which is the most giftable image in the bank.
    (f"{FAM_AI}/watermark-removed-Gemini_Generated_Image_w3tls5w3tls5w3tl.png",
     "Baby gift",                                                                       # 1,710
     ["Under the tree,", "then on the wall"], "x02-xmas-in-hands.jpg"),
]
XMAS_SUN = [
    (f"{SUN_SAMPLES}/sunyear_tromso_ring.png", "New home gift",                         # 2,720
     ["A year of light,", "wrapped"], "x03-xmas-tromso.jpg"),
]


if __name__ == "__main__":
    print("BL-010 — sun pin on the light-wall pattern")
    for src, kicker, lines, name in BL010:
        panel, frac = framed_panel(src)
        print(f"  {name}: art covers {frac * 100:.0f}% of the pin "
              f"(pin_poster letterbox = 54%)")
        print("  wrote", compose(panel, kicker, lines, SUN_OUT, name))

    print("BL-007 — Christmas set, DRAFT, do not publish before 2026-10-01")
    for src, kicker, lines, name in XMAS_FAM:
        print("  wrote", compose(photo_panel(src), kicker, lines, FAM_OUT, name))
    for src, kicker, lines, name in XMAS_SUN:
        panel, _ = framed_panel(src)
        print("  wrote", compose(panel, kicker, lines, SUN_OUT, name))
