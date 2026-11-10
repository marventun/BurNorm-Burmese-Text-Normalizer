# -*- coding: utf-8 -*-
"""Decide when a PDF page is WinInnwa / Academy ASCII and convert it."""

from __future__ import annotations

import re

from ..font_catalog import KEEP_ASCII, WIN, classify_font
from .converter import convert

WIN_FONT = re.compile(
    r"win\s*-?\s*innwa|academy|wwin|win\s*-?\s*myan|"
    + "|".join(re.escape(name) for name in WIN),
    re.IGNORECASE,
)
_MARKS = set("<>;&[]{}*#@+$=~")
_ASCII_KINDS = set(KEEP_ASCII) | {"win", "wwin", "academy", "ce", "legacy", "gandamar", "king", "msheavy"}


def ascii_letters(text):
    return sum(1 for ch in text or "" if ch.isascii() and ch.isalpha())


def myanmar_letters(text):
    return sum(1 for ch in text or "" if "\u1000" <= ch <= "\u109F")


def win_marks(text):
    return sum(ch in _MARKS for ch in (text or ""))


def page_font_kinds(page):
    kinds = set()
    try:
        for item in page.get_fonts():
            name = ((item[3] or "").split("+")[-1]).strip()
            kind = classify_font(name)
            if kind:
                kinds.add(kind)
    except Exception:
        return set()
    return kinds


def page_has_win_font(page):
    kinds = page_font_kinds(page)
    if kinds & _ASCII_KINDS:
        return True
    try:
        names = [item[3] for item in page.get_fonts()]
    except Exception:
        return False
    return any(WIN_FONT.search(name or "") for name in names)


def converted_text(text):
    """Return Unicode when the ASCII is the WinInnwa alphabet. Otherwise \"\"."""
    letters = ascii_letters(text)
    if letters < 40 or myanmar_letters(text) > letters * 0.25:
        return ""
    try:
        converted = convert(text, "wininnwa", "unicode")
    except Exception:
        return ""
    produced = myanmar_letters(converted)
    leftover = ascii_letters(converted)
    if produced < max(40, int(letters * 0.92)):
        return ""
    if leftover > max(3, int(letters * 0.05)):
        return ""
    return converted


def page_text(page, text):
    if not text:
        return ""
    letters = ascii_letters(text)
    if letters < 40 or myanmar_letters(text) > letters * 0.25:
        return ""
    marks = win_marks(text) + text.count(";")
    if not page_has_win_font(page) and marks < 6:
        return ""
    return converted_text(text)


def note_fonts(page, fonts, text):
    if fonts is None:
        return
    weight = max(ascii_letters(text), 1)
    names = []
    try:
        for item in page.get_fonts():
            name = ((item[3] or "").split("+")[-1]).strip()
            if WIN_FONT.search(name) or classify_font(name) in _ASCII_KINDS:
                names.append(name)
    except Exception:
        names = []
    if not names and page_has_win_font(page):
        names = ["WinInnwa"]
    for name in dict.fromkeys(names):
        fonts[name] = fonts.get(name, 0) + weight


def note_catalog(page, fonts, text):
    """Accumulate legacy ASCII font weights for describe_font / book labels."""
    note_fonts(page, fonts, text)
