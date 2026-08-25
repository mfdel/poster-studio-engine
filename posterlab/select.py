"""Expanding a comma-separated CLI selection into the list of names it stands for.

Every product has flags that name *which* of a set to render — ``--size``,
``--theme``, ``--layout``, ``--variant``. They all want the same three things:
one name (``A4``), a group word that stands for many (``all``, ``bundle``,
``pod``), or a list of either (``Letter,A4``). That rule lives here once, so a
product never invents a second syntax for the same idea.

Order is the order asked for, and a name given twice is kept once — a digital
download must not carry the same file twice, and a render must not do the same
work twice.
"""
from __future__ import annotations

from typing import Iterable


def split_selection(value: str) -> list[str]:
    """The non-empty tokens of a comma-separated flag value, in order."""
    return [t.strip() for t in str(value).split(",") if t.strip()]


def expand_selection(value: str, known: Iterable[str] | None = None, *,
                     groups: dict[str, list[str]] | None = None,
                     what: str = "value") -> list[str]:
    """Expand one flag value into the list of names it selects.

    ``known`` is every name the flag accepts; pass ``None`` to skip validation
    when something downstream is the real authority (``--theme`` also takes a
    path, and ``load_theme`` is what decides whether it resolves). ``groups``
    maps a group word to the names it stands for, e.g. ``{"all": [...]}``.
    """
    names = list(known) if known is not None else None
    groups = dict(groups or {})

    picked: list[str] = []
    for token in split_selection(value):
        # Group words are lowercase and no real name collides with one, so
        # ``All`` works too — a size name's own case still has to be exact.
        members = groups.get(token, groups.get(token.casefold()))
        if members is None:
            if names is not None and token not in names:
                choices = f"{names}" + (f", or one of {sorted(groups)}" if groups else "")
                raise SystemExit(f"Unknown {what} {token!r}; choose from {choices}")
            members = [token]
        for name in members:
            if name not in picked:
                picked.append(name)

    if not picked:
        raise SystemExit(f"No {what} selected — {value!r} names nothing to render")
    return picked
