"""Light Unicode cleanup after conversion (NFC, invisibles, mark glue)."""
from __future__ import annotations

import re
import unicodedata

_STRIP = dict.fromkeys(map(ord, "\ufeff\u200b\u200c\u200d\u2060\u00ad"), None)
_MARK = "\u102B-\u103E\u1036\u1037\u1038"
_HSPACE_RUN = re.compile(r"[ \t\xa0\u2000-\u200b\u202f\u205f]{2,}")
_BEFORE_DEPENDENT = re.compile(rf" (?=[{_MARK}\u103A])")
_AFTER_MARK_SPACE = re.compile(rf"(?<=[{_MARK}]) (?=[{_MARK}])")
_LATIN_BETWEEN_DIGITS = re.compile(r"(?<=[\u1040-\u1049])[A-Za-z](?=[\u1040-\u1049])")
_ONLY_MARKS = re.compile(rf"^[{_MARK}\u103A]+$")
_WATERMARK = re.compile(r"burmeseclassic\.com|classic\.com", re.IGNORECASE)


def glue_marks(text: str) -> str:
    out: list[str] = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        if out and _ONLY_MARKS.match(line):
            out[-1] += line
            continue
        out.append(line)
    return "\n".join(out)


def collapse_marks(text: str) -> str:
    text = re.sub(rf"([{_MARK}\u103A])\1+", r"\1", text or "")
    for cluster in ("ီး", "ာ်", "ာ့"):
        text = text.replace(cluster + cluster[0], cluster)
    return text


# Common Unicode mark-order leftovers after Zawgyi convert / OCR.
_MARK_ORDER = (
    ("့ဲ", "ဲ့"),
    ("့ံ", "ံ့"),
)


def reorder_marks(text: str) -> str:
    t = text or ""
    for bad, good in _MARK_ORDER:
        t = t.replace(bad, good)
    return t


def cleanup(text: str) -> str:
    """NFC + strip invisibles + glue/collapse marks. Safe for already-Unicode text."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text).translate(_STRIP)
    text = text.replace("\u00a0", " ").replace("\u00ad", "")
    text = re.sub(r"[\u2000-\u200b\u202f\u205f\ufeff]+", "", text)
    text = re.sub(r"[\u0080-\u00ff\u0100-\u024f]{2,}", " ", text)
    text = _WATERMARK.sub(" ", text)
    text = glue_marks(text)
    text = reorder_marks(text)
    text = collapse_marks(text)
    text = _HSPACE_RUN.sub(" ", text)
    text = _BEFORE_DEPENDENT.sub("", text)
    text = _AFTER_MARK_SPACE.sub("", text)
    text = _LATIN_BETWEEN_DIGITS.sub("", text)
    text = _HSPACE_RUN.sub(" ", text)
    return text
