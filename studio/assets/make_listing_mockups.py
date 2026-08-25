"""
Generate Etsy listing images for Hopscotch Maps from the current rendered posters.

Two kinds of image, all 2000x2500 (4:5, Etsy-friendly), on-brand palette + fonts:
  - Framed-on-wall mockups (whimsy / ink / minimal)  -> hero + style-in-context
  - Info graphics (3-style showcase, what-you-get, how-it-works, size guide, honest note)

Photoreal room scenes are done separately via the Gemini image tool (needs API credits).
This PIL set is pixel-sharp and needs no external service.

Run:  uv run python studio/assets/make_listing_mockups.py
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ---------------------------------------------------------------- paths
SRC = "output/20260730-222145__15_rue_joseph_bara_75006_paris_france__r1500__a495b856"
MAPS = {
    "whimsy":  f"{SRC}/our_playground_map_whimsy_A2_clean_portrait.png",
    "ink":     f"{SRC}/our_playground_map_ink_A2_clean_portrait.png",
    "minimal": f"{SRC}/our_playground_map_minimal_A2_clean_portrait.png",
}
OUT = "posters/fam001-playground-map/brand/listing-photos"
os.makedirs(OUT, exist_ok=True)

W, H = 2000, 2500

# ---------------------------------------------------------------- palette
CREAM   = "#FBF6EC"
BROWN   = "#4A3B2A"   # whimsy text
INK     = "#3D3A35"
CORAL   = "#E0455F"   # whimsy border / home
CORAL2  = "#EF5A5A"   # whimsy marker
GREEN   = "#7FB069"
YELLOW  = "#F4C95D"
SKY     = "#8ECAE6"
MUTED   = "#9A8A72"
MATCOL  = "#FBFAF6"
WOOD    = "#CBA97A"   # the only frame we sell (Gelato "Wood")

# ---------------------------------------------------------------- fonts
F_CHALK = "/System/Library/Fonts/Supplemental/ChalkboardSE.ttc"
F_TREB  = "/System/Library/Fonts/Supplemental/Trebuchet MS.ttf"
F_TREB_B= "/System/Library/Fonts/Supplemental/Trebuchet MS Bold.ttf"


def head(size):
    """Chalkboard SE Bold-ish — matches the whimsy poster title."""
    for idx in (1, 0):
        try:
            return ImageFont.truetype(F_CHALK, size, index=idx)
        except Exception:
            continue
    return ImageFont.truetype(F_TREB_B, size)


def body(size):
    return ImageFont.truetype(F_TREB, size)


def bodyb(size):
    return ImageFont.truetype(F_TREB_B, size)


# ---------------------------------------------------------------- color utils
def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def clamp(x):
    return max(0, min(255, int(x)))


def adjust(h, d):
    r, g, b = hex2rgb(h)
    return (clamp(r + d), clamp(g + d), clamp(b + d))


# ---------------------------------------------------------------- text utils
def tsize(d, txt, fnt):
    b = d.textbbox((0, 0), txt, font=fnt)
    return b[2] - b[0], b[3] - b[1]


def center(d, cx, y, txt, fnt, fill, tracking=0):
    if tracking:
        # manual letter-spacing
        widths = [d.textlength(c, font=fnt) for c in txt]
        total = sum(widths) + tracking * (len(txt) - 1)
        x = cx - total / 2
        for c, cw in zip(txt, widths):
            d.text((x, y), c, font=fnt, fill=fill)
            x += cw + tracking
        _, h = tsize(d, txt, fnt)
        return y + h
    w, h = tsize(d, txt, fnt)
    d.text((cx - w / 2, y), txt, font=fnt, fill=fill)
    return y + h


def wrap(d, txt, fnt, maxw):
    lines, cur = [], ""
    for word in txt.split():
        t = (cur + " " + word).strip()
        if d.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def heart(d, cx, cy, s, fill):
    """Simple heart from two circles + a triangle."""
    r = s / 2
    d.ellipse([cx - s / 2, cy - r / 2, cx, cy + r / 2], fill=fill)
    d.ellipse([cx, cy - r / 2, cx + s / 2, cy + r / 2], fill=fill)
    d.polygon([(cx - s / 2 + 2, cy + r / 4),
               (cx + s / 2 - 2, cy + r / 4),
               (cx, cy + s * 0.75)], fill=fill)


# ---------------------------------------------------------------- backgrounds
def wall(top, bottom):
    img = Image.new("RGB", (W, H), top)
    d = ImageDraw.Draw(img)
    tr, br = hex2rgb(top), hex2rgb(bottom)
    for y in range(H):
        t = y / (H - 1)
        d.line([(0, y), (W, y)],
               fill=(clamp(tr[0] + (br[0] - tr[0]) * t),
                     clamp(tr[1] + (br[1] - tr[1]) * t),
                     clamp(tr[2] + (br[2] - tr[2]) * t)))
    return img


def card(border=True):
    c = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(c)
    if border:
        m = 74
        d.rectangle([m, m, W - m, H - m], outline=CORAL, width=6)
        d.rectangle([m + 18, m + 18, W - m - 18, H - m - 18], outline=CORAL, width=3)
    return c, d


# ---------------------------------------------------------------- framed mockup
def framed(map_path, wall_top, wall_bottom, frame_col, out,
           mat_w=40, frame_w=46, poster_h_frac=0.68, nudge=-0.02):
    canvas = wall(wall_top, wall_bottom).convert("RGBA")
    poster = Image.open(map_path).convert("RGB")
    pw, ph = poster.size
    th = int(H * poster_h_frac)
    tw = int(pw * th / ph)
    poster = poster.resize((tw, th), Image.LANCZOS)

    fw = tw + 2 * mat_w + 2 * frame_w
    fh = th + 2 * mat_w + 2 * frame_w
    fx = (W - fw) // 2
    fy = (H - fh) // 2 + int(H * nudge)

    # soft drop shadow
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    o = 20
    sd.rectangle([fx + o, fy + o + 12, fx + fw + o, fy + fh + o + 20],
                 fill=(50, 42, 34, 95))
    shadow = shadow.filter(ImageFilter.GaussianBlur(30))
    canvas = Image.alpha_composite(canvas, shadow)

    d = ImageDraw.Draw(canvas)
    # frame + bevel
    d.rectangle([fx, fy, fx + fw, fy + fh], fill=frame_col)
    d.line([(fx, fy), (fx + fw, fy)], fill=adjust(frame_col, 34), width=3)
    d.line([(fx, fy), (fx, fy + fh)], fill=adjust(frame_col, 34), width=3)
    d.line([(fx, fy + fh), (fx + fw, fy + fh)], fill=adjust(frame_col, -34), width=3)
    d.line([(fx + fw, fy), (fx + fw, fy + fh)], fill=adjust(frame_col, -34), width=3)
    # mat
    mx, my = fx + frame_w, fy + frame_w
    d.rectangle([mx, my, fx + fw - frame_w, fy + fh - frame_w], fill=MATCOL)
    # inner rabbet line + poster
    px, py = mx + mat_w, my + mat_w
    d.rectangle([px - 2, py - 2, px + tw + 2, py + th + 2], outline="#D8D2C4", width=2)
    canvas.paste(poster, (px, py))

    canvas.convert("RGB").save(out)
    print("saved", out)


# ---------------------------------------------------------------- shadow paste
def paste_with_shadow(c, img, x, y, off=10, blur=16, alpha=70):
    """Paste RGB `img` onto RGB canvas `c` at (x, y) over a soft drop shadow."""
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle(
        [x + off, y + off + 6, x + img.width + off, y + img.height + off + 6],
        fill=(50, 42, 34, alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    merged = Image.alpha_composite(c.convert("RGBA"), sh).convert("RGB")
    c.paste(merged, (0, 0))
    c.paste(img, (x, y))


# ---------------------------------------------------------------- three formats
def three_formats(out, price_digital="€24", price_poster="€44", price_framed="€99"):
    """Mirror of the Etsy format picker: Digital file · Printed poster · Framed poster."""
    c, d = card(border=False)
    center(d, W / 2, 330, "Three ways to have it", head(96), BROWN)
    center(d, W / 2, 468, "pick your format at checkout", body(50), MUTED)

    src = Image.open(MAPS["whimsy"]).convert("RGB")
    thumb_w = 420
    thumb_h = int(src.height * thumb_w / src.width)
    poster = src.resize((thumb_w, thumb_h), Image.LANCZOS)

    col_w, gap = 560, 55
    total = col_w * 3 + gap * 2
    x0 = (W - total) // 2
    top = 760
    cols = [
        ("digital", "Digital file", price_digital, "Print-ready PDF you\nprint yourself"),
        ("poster", "Printed poster", price_poster, "We print it in-country\n& ship it to you"),
        ("framed", "Framed poster", price_framed, "Natural wood frame,\nready to hang"),
    ]

    for i, (kind, name, price, desc) in enumerate(cols):
        cx = x0 + i * (col_w + gap) + col_w // 2
        if kind == "digital":
            # white sheet + poster + folded corner + PDF tag
            pad = 18
            sheet = Image.new("RGB", (thumb_w + 2 * pad, thumb_h + 2 * pad), "#FFFFFF")
            sheet.paste(poster, (pad, pad))
            sd = ImageDraw.Draw(sheet)
            fold = 46
            sd.polygon([(sheet.width - fold, 0), (sheet.width, 0),
                        (sheet.width, fold)], fill="#EDE7DA")
            x = cx - sheet.width // 2
            paste_with_shadow(c, sheet, x, top)
            d = ImageDraw.Draw(c)
            d.rectangle([x, top, x + sheet.width, top + sheet.height],
                        outline="#E3D3AD", width=2)
            block_bottom = top + sheet.height
        elif kind == "poster":
            # thin white border like a bare print
            pad = 22
            pr = Image.new("RGB", (thumb_w + 2 * pad, thumb_h + 2 * pad), "#FCFBF7")
            pr.paste(poster, (pad, pad))
            x = cx - pr.width // 2
            paste_with_shadow(c, pr, x, top)
            d = ImageDraw.Draw(c)
            d.rectangle([x, top, x + pr.width, top + pr.height],
                        outline="#E3D3AD", width=2)
            block_bottom = top + pr.height
        else:
            # mini wood frame + mat + poster
            frame_w, mat_w = 34, 30
            fw = thumb_w + 2 * mat_w + 2 * frame_w
            fh = thumb_h + 2 * mat_w + 2 * frame_w
            frame = Image.new("RGB", (fw, fh), WOOD)
            fd = ImageDraw.Draw(frame)
            fd.rectangle([frame_w, frame_w, fw - frame_w, fh - frame_w], fill=MATCOL)
            frame.paste(poster, (frame_w + mat_w, frame_w + mat_w))
            fd.rectangle([frame_w + mat_w - 2, frame_w + mat_w - 2,
                          frame_w + mat_w + thumb_w + 2, frame_w + mat_w + thumb_h + 2],
                         outline="#D8D2C4", width=2)
            x = cx - fw // 2
            paste_with_shadow(c, frame, x, top - (fh - thumb_h) // 2, off=14, blur=22, alpha=90)
            block_bottom = top - (fh - thumb_h) // 2 + fh
            d = ImageDraw.Draw(c)

        ly = max(top + thumb_h + 120, block_bottom + 70)
        center(d, cx, ly, name, head(56), BROWN)
        center(d, cx, ly + 82, price, bodyb(60), CORAL)
        for j, line in enumerate(desc.split("\n")):
            center(d, cx, ly + 176 + j * 52, line, body(38), MUTED)

    center(d, W / 2, H - 150, "Every format is hand-styled to order", body(42), BROWN)
    c.save(out)
    print("saved", out)


# ---------------------------------------------------------------- showcase
def showcase(out):
    c, d = card(border=False)
    center(d, W / 2, 330, "Three signature styles", head(96), BROWN)
    center(d, W / 2, 465, "one keepsake — your way", body(52), MUTED)

    labels = [("whimsy", "Whimsy", "warm & hand-drawn"),
              ("ink", "Ink & Play", "editorial & refined"),
              ("minimal", "Minimal", "clean & modern")]
    pw_target = 560
    gap = 84
    total = pw_target * 3 + gap * 2
    x0 = (W - total) // 2
    top = 720
    ph_max = 0
    for i, (key, name, desc) in enumerate(labels):
        p = Image.open(MAPS[key]).convert("RGB")
        ratio = pw_target / p.width
        ph = int(p.height * ratio)
        ph_max = max(ph_max, ph)
        p = p.resize((pw_target, ph), Image.LANCZOS)
        x = x0 + i * (pw_target + gap)
        # shadow
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle([x + 10, top + 16, x + pw_target + 10, top + ph + 16],
                                     fill=(50, 42, 34, 70))
        sh = sh.filter(ImageFilter.GaussianBlur(18))
        c.paste(Image.alpha_composite(c.convert("RGBA"), sh).convert("RGB"), (0, 0))
        c.paste(p, (x, top))
        d = ImageDraw.Draw(c)
        d.rectangle([x, top, x + pw_target, top + ph], outline="#E3D3AD", width=2)
        ly = top + ph + 40
        center(d, x + pw_target / 2, ly, name, head(54), BROWN)
        center(d, x + pw_target / 2, ly + 78, desc, body(36), MUTED)
    # footer strip
    fy = top + ph_max + 250
    d.line([(W / 2 - 250, fy - 44), (W / 2 + 250, fy - 44)], fill="#E3D3AD", width=3)
    center(d, W / 2, fy, "Pick your favourite at checkout", body(46), BROWN)
    center(d, W / 2, fy + 74, "clean poster, or the 'Our Playground Adventures' layout",
           body(36), MUTED)
    c.save(out)
    print("saved", out)


# ---------------------------------------------------------------- icon disc
def disc(d, cx, cy, r, fill, symbol=None, txt=None, fnt=None):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    if symbol == "check":
        d.line([(cx - r * 0.42, cy + r * 0.04),
                (cx - r * 0.08, cy + r * 0.40),
                (cx + r * 0.48, cy - r * 0.34)],
               fill="white", width=max(6, int(r * 0.22)), joint="curve")
    elif symbol == "heart":
        heart(d, cx, cy - r * 0.05, r * 1.0, "white")
    elif txt is not None:
        w, h = tsize(d, txt, fnt)
        d.text((cx - w / 2, cy - h / 2 - h * 0.15), txt, font=fnt, fill="white")


# ---------------------------------------------------------------- what you get
def what_you_get(out):
    c, d = card()
    center(d, W / 2, 175, "What you'll get", head(104), BROWN)
    heart(d, W / 2, 355, 46, CORAL)

    rows = [
        ("Hand-styled, made to order", "Drawn for your address, with a preview to approve"),
        ("Choose your format", "Digital file · printed poster · framed poster"),
        ("Made for your family", "Numbered playground list + a star-rating legend"),
        ("Room to make it yours", "Blank spots for notes, drawings & photo corners"),
        ("Print-ready or ready-to-hang", "A 300+ DPI PDF, or we print & ship it to you"),
    ]
    x = 300
    y = 500
    step = 348
    for title, sub in rows:
        disc(d, x, y + 40, 52, CORAL, symbol="check")
        d.text((x + 120, y), title, font=bodyb(60), fill=BROWN)
        for j, line in enumerate(wrap(d, sub, body(42), W - (x + 120) - 220)):
            d.text((x + 120, y + 88 + j * 54), line, font=body(42), fill=MUTED)
        y += step
    center(d, W / 2, H - 190, "Made by a dad, for families", body(34), MUTED)
    c.save(out)
    print("saved", out)


# ---------------------------------------------------------------- how it works
def how_it_works(out):
    c, d = card()
    center(d, W / 2, 180, "How it works", head(104), BROWN)

    steps = [
        ("1", "Tell us where", "Send your address, how far to roam, and your format."),
        ("2", "We hand-style it", "We craft a warm map of every playground around you."),
        ("3", "Get it your way", "Download the file, or we print & ship it to your door."),
    ]
    y = 560
    step = 560
    for num, title, sub in steps:
        disc(d, 340, y, 82, CORAL, txt=num, fnt=head(90))
        d.text((470, y - 78), title, font=bodyb(70), fill=BROWN)
        for j, line in enumerate(wrap(d, sub, body(46), 1180)):
            d.text((470, y + 6 + j * 58), line, font=body(46), fill=MUTED)
        if num != "3":
            d.line([(340, y + 96), (340, y + step - 96)], fill="#E3D3AD", width=5)
        y += step
    center(d, W / 2, H - 200, "Usually delivered within 2–3 days 💛".replace("💛", ""),
           body(46), BROWN)
    heart(d, W / 2 + 430, H - 178, 40, CORAL)
    c.save(out)
    print("saved", out)


# ---------------------------------------------------------------- size guide
def size_guide(out):
    c, d = card()
    center(d, W / 2, 175, "Find your size", head(104), BROWN)
    center(d, W / 2, 320, "Digital includes every size — prints made to the size you pick",
           body(42), MUTED)

    # nested A-series rectangles (share aspect 1:1.414), aligned bottom-left
    specs = [("A2", "42 × 59 cm", 1.0, CORAL),
             ("A3", "30 × 42 cm", 1 / (2 ** 0.5), GREEN),
             ("A4", "21 × 30 cm", 0.5, INK)]
    base_h = 1120
    bx, by = 360, 2100  # bottom-left anchor; A2 right edge ~ bx + 792
    for name, dims, k, col in specs:
        h = base_h * k
        w = h / (2 ** 0.5)
        d.rectangle([bx, by - h, bx + w, by], outline=col, width=8)
        d.text((bx + 26, by - h + 22), name, font=head(64), fill=col)
        d.text((bx + 26, by - h + 108), dims, font=body(38), fill=MUTED)
    # right column, clear of the A2 rectangle
    rx = 1360
    d.text((rx, 640), "Also included", font=bodyb(56), fill=BROWN)
    for j, line in enumerate(["US Letter", "16 × 20 inch", "18 × 24 inch"]):
        disc(d, rx + 24, 800 + j * 96, 17, GREEN)
        d.text((rx + 74, 772 + j * 96), line, font=body(48), fill=BROWN)
    d.text((rx, 1140), "Print at home, or let\nus print & ship it.", font=body(46), fill=MUTED)
    c.save(out)
    print("saved", out)


# ---------------------------------------------------------------- honest note
def honest_note(out):
    c, d = card()
    heart(d, W / 2, 720, 96, CORAL)
    center(d, W / 2, 820, "A little honesty", head(100), BROWN)
    msg = ("Choose digital and you'll get a file to print — nothing is mailed. "
           "Choose a printed or framed map and we produce it and ship it to you. "
           "Colours can shift a touch between screens, printers and paper. We'd "
           "always rather tell you up front, so you get exactly the keepsake you "
           "hoped for.")
    y = 1050
    for line in wrap(d, msg, body(58), W - 520):
        y = center(d, W / 2, y, line, body(58), INK) + 26
    center(d, W / 2, y + 60, "Digital is a file · prints & frames ship to you.",
           body(46), MUTED)
    c.save(out)
    print("saved", out)


# ---------------------------------------------------------------- main
if __name__ == "__main__":
    # We only sell the natural-wood frame, so every mockup shows that frame.
    framed(MAPS["whimsy"], "#EEE5D6", "#E4D8C4", WOOD,
           f"{OUT}/01-framed-whimsy.png", mat_w=42, frame_w=48)
    framed(MAPS["ink"], "#EAE4D8", "#DFD7C7", WOOD,
           f"{OUT}/02-framed-ink.png", mat_w=42, frame_w=48)
    framed(MAPS["minimal"], "#EFEADF", "#E4DDCF", WOOD,
           f"{OUT}/03-framed-minimal.png", mat_w=42, frame_w=48)
    three_formats(f"{OUT}/09-three-formats.png")
    showcase(f"{OUT}/04-showcase-styles.png")
    what_you_get(f"{OUT}/05-what-you-get.png")
    how_it_works(f"{OUT}/06-how-it-works.png")
    size_guide(f"{OUT}/07-size-guide.png")
    honest_note(f"{OUT}/08-honest-note.png")
    print("\nAll listing images written to", OUT)
