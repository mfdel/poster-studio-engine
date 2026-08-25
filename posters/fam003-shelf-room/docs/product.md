# FAM-003 — Shelf Room

## What it is

Shelf Room is a print-at-home pack. The pack turns one cube shelf into a small room.
The buyer prints the pages, cuts the panels, and glues them inside the cube.
The room becomes a play space for small figures and a display space for objects.

The pack is a digital download. No physical item ships.

## Who buys it

Parents of children between 3 and 8 years old.
Buyers of dollhouse and small-world play items.
Gift buyers who want a low-cost present that needs no assembly tools.

## What the buyer receives

The pack contains one PDF for each paper size.
Each PDF has this order:

1. A calibration page with a 50 mm test square.
2. An assembly map that shows where each panel goes.
3. The artwork sheets.

The pack also contains a how-to-print note and a licence note.

## Sheet count

The default cube is the IKEA Kallax opening: 330 x 330 x 390 mm.
The pack covers four faces: the floor, the back, and the two side walls.
The ceiling is optional, because the ceiling is unlit and is rarely seen.

| Paper | Easy mode | Eco mode |
|---|---|---|
| A4 | 16 sheets | 11 sheets |
| Letter | 16 sheets | 11 sheets |

Easy mode prints one panel on each sheet.
Eco mode packs more than one panel on a sheet. Eco mode saves 5 sheets.

The engine covers 360 mm of the 390 mm depth. The last 30 mm sit behind the
shelf lip. This trim is what lets the offcut panels share a sheet.

## Print rules

Every join has a 10 mm overlap.
Every cut line runs straight across the sheet. No cut turns a corner.
Every seam carries a drawn feature. The feature is a wallpaper stripe edge, a
picture rail, the top of the skirting board, a floorboard end joint, or a ceiling
moulding. The seam therefore reads as part of the room. This holds for any cube
size, not only the default one.

The buyer must print at 100 percent. The buyer must not use "Fit to page".
Page 1 proves the scale with a 50 mm square.

## Trademark rule

The product fits cube shelves made by many companies. The opening is 33 x 33 cm.

State the dimension first and the brand second.
Never put a trademark in the shop name, the domain, or the logo.
Never use another company's logo, colours, or product photographs.
Print this line in every listing and in the licence note:

> Not affiliated with, endorsed by, or sponsored by Inter IKEA Systems B.V.
> IKEA and KALLAX are trademarks of Inter IKEA Systems B.V.

## Commands

Build the default pack:

```
uv run python posters/fam003-shelf-room/make.py --theme whimsy --preview
```

Build both paper sizes:

```
uv run python posters/fam003-shelf-room/make.py --size both
```

Build for a different shelf:

```
uv run python posters/fam003-shelf-room/make.py --cube 380x380x400 --cover-depth 370
```

## State on 2026-08-20

The engine works. The engine writes a correct pack for any cube size.
The artwork is a first draft in one theme family. The artwork needs a design pass
before the product is listed.
