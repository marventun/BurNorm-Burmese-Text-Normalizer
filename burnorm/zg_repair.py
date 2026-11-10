"""Conservative Zawgyi OCR/extraction repairs before Rabbit convert.

Handles common broken sequences from PDF/OCR extraction:
- spaces inserted before dependent marks (``န႔ ဲ``, ``ေတကြ ို``)
- swapped ``႔``/``ဲ`` order (``န႔ဲ`` → ``နဲ႔``)
- ``ခ့ဖဲ`` → ``ခဲ့ဖ`` mark placement
- ``ေတကြ`` OCR garble for ``ေတြ`` (တွေ)
"""
from __future__ import annotations

import re

_C = "\u1000-\u1021"
# Dependent signs that must glue to the previous syllable.
# NOTE: exclude U+1031 (ေ) — in Zawgyi it is stored *before* its consonant, so
# a space before ေ is usually a real word break (``စ ေရး``), not OCR glue.
_DEP = (
    "\u102B-\u1030"  # vowels ါ-ူ (not ေ)
    "\u1032"  # ဲ
    "\u1036-\u1038"  # ံ ့ း
    "\u103A-\u103E"  # ် ျ ြ ွ ှ (and asat)
    "\u105A-\u109F"  # Zawgyi presentation / extended
)
_SPACE_BEFORE_DEP = re.compile(rf"([\u1000-\u109F])[ \t\xa0]+(?=[{_DEP}])")
_DOT_THEN_E = re.compile(rf"([{_C}])\u1094\u1032")  # C႔ဲ → Cဲ႔
_DOT_C_E = re.compile(rf"([{_C}])\u1037([{_C}])\u1032")  # C့Cဲ → Cဲ့C (ခဲ့ဖ)
_TEKWA_KO = re.compile("\u1031\u1010\u1000\u103c\u102d\u102f")  # ေတကြို → ေတြကို
_TEKWA = re.compile("\u1031\u1010\u1000\u103c")  # ေတကြ → ေတြ
_A_DHA = "အ့ဒဲါ"  # OCR garble of အဲဒါ


def repair_zawgyi(text: str) -> str:
    """Fix common Zawgyi extraction glitches. Safe no-op on clean Zawgyi/Unicode."""
    t = text or ""
    if not t:
        return ""

    # Only remove spaces that sit *before dependent marks*, keep word spaces.
    prev = None
    while prev != t:
        prev = t
        t = _SPACE_BEFORE_DEP.sub(r"\1", t)

    # Exact OCR phrases first (before general mark swaps).
    t = t.replace(_A_DHA, "အဲဒါ")
    t = _TEKWA_KO.sub("ေတြကို", t)
    t = _TEKWA.sub("ေတြ", t)

    # Mark order repairs.
    t = _DOT_THEN_E.sub(lambda m: m.group(1) + "\u1032\u1094", t)
    t = _DOT_C_E.sub(lambda m: m.group(1) + "\u1032\u1037" + m.group(2), t)
    return t
