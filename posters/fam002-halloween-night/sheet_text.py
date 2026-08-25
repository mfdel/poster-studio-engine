"""Every printed string on the Halloween sheet (FAM-002), in one place.

``panel.py`` and ``layouts.py`` render five different sheets from the same copy.
When the wording lived in both modules the two could drift, and a buyer who
bought the map sheet and the bonus sheet would get two different vocabularies for
the same box.

The rule that must never break
------------------------------
Nothing here names a house, and nothing claims which houses give treats or which
houses are safe. That data does not exist before the evening — a porch light goes
on when a neighbour decides it does. The sheet records the child's night; it does
not promise one. Keep every string on this side of that line.
"""
from __future__ import annotations

HEADING = "Our Trick-or-Treat Night"
SHEET_HEADING = "The streets we walked"
ROUTE_CALL = "Draw the route on the map"
HINT = ("Your house is marked on the map. Draw the streets you walked, "
        "then colour one box for every treat.")

FIELDS = ["Costume", "We walked with"]
TALLY_LABEL = "Treats we counted"
TALLY_SHORT = "Treats counted"
MEMORY = "The house we liked best"
DRAW_LABEL = "Draw the best costume you saw"

TALLY_COUNT = 40          # boxes to colour — a good night's haul, and it fits
TALLY_CELL_MM = (3.5, 8.5)  # a box small enough to fit, big enough for a crayon

# --- The bonus spotting sheet ---------------------------------------------- #

# Deliberately empty. The spotting sheet ships in the same pack as the map
# sheet, so calling it a bonus on the paper reads as filler to the child who
# is holding it. The date keeps that line company on its own.
BONUS_EYEBROW = ""
BONUS_TITLE = "Things we saw on Halloween"
BONUS_HINT = "Cross one off for every one you spot. Take it with you."

# Sixteen things a child can actually find on any street, in any town, without
# the sheet having to know anything about the neighbourhood. Nothing here depends
# on a particular house doing a particular thing.
BONUS_ITEMS = [
    "A carved pumpkin", "A porch light on", "A black cat", "A skeleton",
    "A ghost", "Someone in a cape", "A spider web", "A dog in costume",
    "Two of the same costume", "A candle in a window", "Orange lights",
    "A witch hat", "A friend from school", "A bat shape", "Cobwebs on a fence",
    "The biggest pumpkin",
]
