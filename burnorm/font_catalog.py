# -*- coding: utf-8 -*-
"""Classify an embedded Myanmar font name.

Win Myanmar fonts share the WinInnwa alphabet. Zawgyi uses the Zawgyi
converter. The Unicode fonts are already Unicode. Academy, Computer Eain,
MyaZedi, Metrix, Gandamar, King, Wwin, and MS-Heavy are converted with the
Burglish OE tables in legacy_maps.
"""

import re

_SPLIT = re.compile(r"[,;/|]")

WIN = (
    "wininnwa",
    "winresearcher",
    "winmandalay",
    "winbagan",
    "winmajestic",
    "winthida",
    "winzayar",
    "winyadanar",
    "winkyaw",
    "winalinkar",
    "wingantgaw",
    "winpadauk",
    "wintaunggyi",
    "wintaungyi",
    "wintaungyee",
    "winpyitinehtaung",
    "winsittwe",
    "winpazundaung",
    "winkaung",
    "winmyat",
    "winshwemyan",
    "wintheikpa",
)

CE = (
    "cefont",
    "cetext",
    "cenormal",
    "cebold",
    "cebook",
    "cenews",
    "cecomputereain",
    "ceheading",
    "ceclassic",
    "ceexcel",
    "computereain",
)

LEGACY = (
    "metrix",
    "shwethin",
    "shwehintha",
    "arthouse",
    "wanthu",
    "bagan",
    "tharawun",
    "pyimyanmar",
)

GANDAMAR = ("gandamar",)
KING = ("kingmyanmarsar", "kingmyanmar")
WWIN = ("wwinburmese", "wwin", "winhan", "winburmese", "myawaddy", "hannwethaki", "blnew")
MSHEAVY = ("msheavy", "msmoom")
KANNAKA = ("kannaka", "arlarwade", "amyanmar", "arlar")
MMYANMAR = ("mmyanmar1", "mmyanmar")

UNICODE = (
    "pyidaungsu",
    "myanmarcensus",
    "myanmar3",
    "myanmar2",
    "myanmar1",
    "padauk",
    "notosansmyanmar",
    "notoserifmyanmar",
    "myanmartext",
    "tharlon",
    "thanlwin",
    "myanmarsans",
    "paoh",
    "masterpieceuni",
    "masterpiececlassical",
    "yunghkio",
    "namkhone",
    "panglong",
    "taunggyi",
    "ayar",
    "mon3",
    "aunimon",
    "aoramon",
    "kayin",
    "karenunicode",
    "sgawkaren",
    "pwokaren",
    "rawang",
    "jinghpaw",
    "walone",
    "sabon",
    "parabaik",
    "gondamar",
    "cherry",
    "kanbawza",
    "maymyo",
    "inlay",
    "shwedaung",
)

_LEGACY_EXACT = frozenset(("shwe",))
KEEP_ASCII = (
    "win",
    "academy",
    "ce",
    "myazedi",
    "legacy",
    "gandamar",
    "king",
    "wwin",
    "msheavy",
    "kannaka",
    "mmyanmar",
)
_KEEP = KEEP_ASCII + ("zawgyi",)


def font_key(name):
    base = (name or "").split("+")[-1]
    return re.sub(r"[^0-9a-z]+", "", base.lower())


def classify_font(name):
    key = font_key(name)
    if not key or key in ("unknown", "calibri", "arial", "timesnewroman"):
        return ""
    if "zawgyi" in key:
        return "zawgyi"
    if any(key.startswith(item) for item in WIN):
        return "win"
    if key.startswith("academy") or key in ("aeyar", "aekari"):
        return "academy"
    if key == "ce" or any(key.startswith(item) for item in CE):
        return "ce"
    if "myazedi" in key or key in ("bit", "mandalay"):
        return "myazedi"
    if any(key.startswith(item) for item in GANDAMAR):
        return "gandamar"
    if key == "king" or any(key.startswith(item) for item in KING):
        return "king"
    if any(key.startswith(item) for item in WWIN):
        return "wwin"
    if any(key.startswith(item) for item in MSHEAVY):
        return "msheavy"
    if any(key.startswith(item) for item in KANNAKA):
        return "kannaka"
    if any(key.startswith(item) for item in MMYANMAR):
        return "mmyanmar"
    if any(key.startswith(item) for item in UNICODE):
        return "unicode"
    if key in _LEGACY_EXACT or any(key.startswith(item) for item in LEGACY):
        return "legacy"
    return ""


def label_kind(label):
    found = []
    for part in _SPLIT.split(label or ""):
        kind = classify_font(part)
        if kind:
            found.append(kind)
    for kind in _KEEP + ("unicode",):
        if kind in found:
            return kind
    return ""


def keeps_legacy_text(label):
    return label_kind(label) in _KEEP
