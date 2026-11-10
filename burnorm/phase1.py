"""Phase 1 Level-1 normalize fixes (rules: Noman; ship order locked 2026-10-30).

Zawgyi/Rabbit path only. wininnwa/ and legacy_maps/ (KEEP_ASCII branch) are untouched:
call to_unicode_text() AFTER that branch would have run, BEFORE postprocess().
"""
import re

_MY = re.compile(r"[\u1000-\u109F]")
# Zawgyi-only presentation range; excludes Shan digits U+1090-1099 per Noman.
_ZG = re.compile(r"[\u105A-\u108F\u109A-\u109F]")
_ASAT = re.compile(r"[\u1000-\u1021]\u103a")
_WA = re.compile(r"[\u1000-\u1021]\u103d")
EPS = 0.01
GAIN = 0.02


def myanmar_count(text):
    return len(_MY.findall(text or ""))


def myanmar_subset(text):
    return "".join(c for c in (text or "") if "\u1000" <= c <= "\u109F" or c in " \n")


def has_zg_range(text):
    return bool(_ZG.search(text or ""))


def zg_mark_count(text):
    return len(_ZG.findall(text or ""))


def unicode_quality(text):
    # q = (asat-pairs + wa-pairs - 4*Zawgyi-range leftovers) / max(1, Myanmar chars)  (length-normalised legacy_font._quality)
    t = text or ""
    raw = len(_ASAT.findall(t)) + len(_WA.findall(t)) - 4 * zg_mark_count(t)
    return raw / max(1, myanmar_count(t))


def _score(detector, text):
    sub = myanmar_subset(text)
    if not sub.strip() or detector is None:
        return 0.0
    try:
        s = float(detector.get_zawgyi_probability(sub))
    except Exception:
        return 0.0
    return s if 0.0 <= s <= 1.0 else 0.0


def _default_rabbit():
    from . import zawgyi_rabbit
    return zawgyi_rabbit.convert


def to_unicode_line(unit, detector, zawgyi_min=0.5, rabbit_convert_fn=None):
    """Callme per-line quality guard. Returns (text, score_u, accepted, note)."""
    if myanmar_count(unit) == 0:
        return unit, 0.0, False, "no_myanmar"
    rabbit_convert_fn = rabbit_convert_fn or _default_rabbit()
    score_u = _score(detector, unit)
    base_q = unicode_quality(unit)
    strong = score_u >= 0.95 or has_zg_range(unit) or zg_mark_count(unit) >= 3 or base_q < -0.05
    weak = score_u >= zawgyi_min
    if not (strong or weak):
        return unit, score_u, False, "unicode_keep"
    cand = rabbit_convert_fn(unit)
    qc = unicode_quality(cand)
    if strong and qc >= base_q - EPS:
        return cand, score_u, True, "strong_accept"
    if not strong and qc > base_q + GAIN:
        return cand, score_u, True, "weak_accept"
    return unit, score_u, False, "rabbit_fp_keep"


def to_unicode_text(text, detector, zawgyi_min=0.5, rabbit_convert_fn=None, stats=None):
    lines = []
    for unit in (text or "").split("\n"):
        out, _s, acc, note = to_unicode_line(unit, detector, zawgyi_min, rabbit_convert_fn)
        if stats is not None:
            stats[note] = stats.get(note, 0) + 1
        lines.append(out)
    return "\n".join(lines)


def page_has_myanmar_unit(text, min_chars=20):
    """Unit gate: any line with >=min_chars Myanmar (not TOC/English head first-3000 chars)."""
    return any(myanmar_count(line) >= min_chars for line in (text or "").split("\n"))


def count_zawgyi_lines(text, detector, min_score=0.5, min_my=10):
    """Lines (with >=min_my Myanmar) still scoring >=min_score on ACCEPTED output."""
    return sum(1 for line in (text or "").split("\n")
               if myanmar_count(line) >= min_my and _score(detector, line) >= min_score)


def book_done_ok(text, detector, max_zg_lines=0):
    """DONE iff zg>=0.5 lines <= max_zg_lines. Broad Zawgyi-range count is reported only."""
    stats = {
        "zg_lines": count_zawgyi_lines(text, detector),
        "residual_broad": zg_mark_count(text),
    }
    ok = stats["zg_lines"] <= max_zg_lines
    return ok, stats
