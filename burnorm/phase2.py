"""Phase 2 Ship 1 (B-only) Level-1 normalize: ေ/ြ visual-order reorder (rules: Noman, scope: Camella, 2026-10-30).

Input: Phase-1 output text (books_phase1). Per-line only; never whole-page Rabbit on page zg<0.5.

Triggers (per Myanmar-bearing line), per Noman amend:
  ORPHAN_E  : (signal = kinzi `င်္ေ`+C ONLY; other leading ေ+C e.g. ေအာက် is PARKED: never touched,
              counted parked_e_leading, Phase 2b). Original def: ေ (1031) whose previous char is NOT a consonant/medial/stack-member (i.e. start, space,
              punct, vowel, asat, ္ after kinzi `င်္ေ`) AND next char is a consonant -> PDF visual-before-C.
              Legal Unicode `C…ေ` is never touched.
  ORPHAN_YA : ြ (103C) at start / after space / vowel / asat / ေ, before a consonant.
  E_VOWEL   : C+M* C ေ [ိီုူ] (e.g. တွကေို) - ေ glued to wrong cluster (ေ+ိ/ု never legal).
Deterministic reorder = Camella helpers (exact), order: fix_medial_r, fix_kinzi_e, fix_e_shift.
  ၀ေ (1040+1031) excluded from triggers. Bare line-initial ေအာက် NOT auto-reordered (may be legit); only
  Rabbit may fix it, and only through the +0.02 guard. Spaced kinzi (ခြင်္ သေ့) parked.
Old draft notes:
  1. [^C]ြC -> Cြ          (ဟောြပော -> ဟောပြော, ေြC -> ေCြ)
  2. orphan ေ + (C ္C?)M*   -> (C ္C?)M* ေ   (ေအာက် -> အောက်, သင်္ေကတ -> သင်္ကေတ)
  3. (C M*)Cေ[ိီုူ]        -> (C M*)ေ C[ိီုူ] (တွကေို -> တွေကို)
  Orphan ြ with no consonant within next 1-2 chars: left, logged ya_pin_orphan.
Pali soft guard: triggered only by E_VOWEL, line has C္C stacks and no Zawgyi-range -> skip (pali_skip).
Candidates: Rabbit(legacy_font.convert), and reorder. Best accepted iff
  q2(cand) > q2(orig)+0.02, where q2 = phase1.unicode_quality - wrong_order_signals/myanmar_chars
  (P1 formula reused; the wrong-order term is needed since pure reorders don't change asat/wa counts).
Else keep original, log visual_order_fp.
PARKED (not in this ship): U+1069->္တ (Wwin/bit), Win hole tables, 1065/1066/109A-E.
"""
import re
from . import phase1 as p1

C = "\u1000-\u1021\u1023-\u1027\u1029\u102a\u103f"   # consonants + independent vowels
M = "\u103b-\u103e"
GAIN = 0.02
_STACK = re.compile(f"[{C}]\u1039[{C}]")
_ORPHAN_E = re.compile(f"(?:^|(?<![{C}{M}\u1040]))\u1031(?=[{C}])")
_ORPHAN_YA = re.compile(f"(?:^|(?<![{C}]))\u103c(?=\u1031?[{C}])")
_ORPHAN_YA_ANY = re.compile(f"(?:^|(?<![{C}]))\u103c")
_KINZI_E_SIG = re.compile("\u1004\u103a\u1039\u103c?\u1031[\u1000-\u1021]")
_E_VOWEL = re.compile(f"[{C}][{M}]*[{C}]\u1031[\u102d\u102e\u102f\u1030]")

# Camella helpers (exact), applied in order per unit
_K_E = re.compile(f"(\u1004\u103a\u1039)(\u103c?)\u1031([\u1000-\u1021])")
_E_SHIFT = re.compile(f"([{C}][{M}]*)([{C}])\u1031(\u102d\u102f|\u102c|\u102b)")
_E_ASAT = re.compile(f"([\u103a\u1038])\u1031([{C}][{M}]*)")
_MED_R = re.compile(f"([\u102c\u1031\u103a\u1038])\u103c([{C}])")


def fix_kinzi_e(t):
    return _K_E.sub(lambda m: m.group(1) + m.group(3) + m.group(2) + "\u1031", t)


def fix_e_shift(t):
    # ONLY ...Cေို / ...Cော / ...Cေါ ; no space allowed inside (regex has no \s) -> stops at space
    return _E_SHIFT.sub(lambda m: m.group(1) + "\u1031" + m.group(2) + m.group(3), t)


def fix_medial_r(t):
    return _MED_R.sub(lambda m: m.group(1) + m.group(2) + "\u103c", t)


def signals(t):
    t = t or ""
    return {"orphan_e": len(_KINZI_E_SIG.findall(t)), "orphan_ya": len(_ORPHAN_YA.findall(t)),
            "e_vowel": len(_E_VOWEL.findall(t))}


def wrong_order_count(t):
    return sum(signals(t).values())


def q2(t):
    return p1.unicode_quality(t) - wrong_order_count(t) / max(1, p1.myanmar_count(t))


HELPERS = None  # set below


def reorder(t):
    """All helpers unguarded (diagnostic). Production path uses greedy_reorder."""
    for h in HELPERS:
        t = h(t)
    return t


def _per_match(rx, rep, t):
    """Apply rx one match at a time; keep each edit only if q2 rises (per-match guard)."""
    pos = 0
    while True:
        m = rx.search(t, pos)
        if not m:
            return t
        c = t[:m.start()] + rep(m) + t[m.end():]
        if q2(c) > q2(t):
            t = c
        pos = m.start() + 1


def greedy_reorder(t):
    """Helpers applied per match, each kept only if it raises q2; so ော/ေါ shifts
    (which fix no signal) and noisy ြ-after-vowel moves never land on their own."""
    t = _per_match(_MED_R, lambda m: m.group(1) + m.group(2) + "\u103c", t)
    t = _per_match(_K_E, lambda m: m.group(1) + m.group(3) + m.group(2) + "\u1031", t)
    t = _per_match(_E_SHIFT, lambda m: m.group(1) + "\u1031" + m.group(2) + m.group(3), t)
    return t


def parked_e_leading(t):
    return len(_ORPHAN_E.findall(t or "")) - len(_KINZI_E_SIG.findall(t or ""))


def is_pali_like(t, sig):
    return (sig["orphan_e"] == 0 and sig["orphan_ya"] == 0 and bool(_STACK.search(t))
            and not p1.has_zg_range(t))


def to_unicode_line_phase2(unit, rabbit_convert_fn=None):
    """Returns (text, note). note in no_myanmar|no_trigger|pali_skip|accepted_reorder|accepted_rabbit|visual_order_fp."""
    if p1.myanmar_count(unit) == 0:
        return unit, "no_myanmar"
    sig = signals(unit)
    if not any(sig.values()):
        return unit, "no_trigger"
    if is_pali_like(unit, sig):
        return unit, "pali_skip"
    q0 = q2(unit)
    cands = []
    if not p1.has_zg_range(unit):
        rabbit_convert_fn = False   # Rabbit only on units with Zawgyi-range glyphs (B is Unicode-order repair)
    if rabbit_convert_fn is None:
        from . import zawgyi_rabbit
        rabbit_convert_fn = zawgyi_rabbit.convert
    if rabbit_convert_fn:
      try:
        cands.append(("accepted_rabbit", rabbit_convert_fn(unit)))
      except Exception:
        pass
    cands.append(("accepted_reorder", greedy_reorder(unit)))
    # lock 3: leading ေ+C never auto-touched -> reject any candidate that changes the parked-ေ count
    pk = parked_e_leading(unit)
    cands = [c for c in cands if parked_e_leading(c[1]) == pk]
    if not cands:
        return unit, "visual_order_fp"
    best = max(cands, key=lambda c: q2(c[1]))
    if q2(best[1]) > q0 + GAIN:
        return best[1], best[0]
    return unit, "visual_order_fp"


def to_unicode_text_phase2(text, rabbit_convert_fn=None, stats=None, samples=None):
    out = []
    for unit in (text or "").split("\n"):
        new, note = to_unicode_line_phase2(unit, rabbit_convert_fn)
        if stats is not None:
            stats[note] = stats.get(note, 0) + 1
            if note not in ("no_myanmar", "no_trigger"):
                stats["b_trigger"] = stats.get("b_trigger", 0) + 1
            if note.startswith("accepted"):
                stats["accepted"] = stats.get("accepted", 0) + 1
            stats["parked_e_leading"] = stats.get("parked_e_leading", 0) + parked_e_leading(new)
            stats["ya_pin_orphan"] = stats.get("ya_pin_orphan", 0) + \
                len(_ORPHAN_YA_ANY.findall(new)) - len(_ORPHAN_YA.findall(new))
        if samples is not None and note.startswith(("accepted", "visual", "pali")):
            samples.append((note, unit, new))
        out.append(new)
    return "\n".join(out)


HELPERS = [fix_medial_r, fix_kinzi_e, fix_e_shift]
