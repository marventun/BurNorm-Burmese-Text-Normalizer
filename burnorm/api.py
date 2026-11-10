"""Public API: Burmese PDF/legacy-font & Zawgyi → Unicode + normalize."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from . import kinzi, phase1, phase2, post, zawgyi_rabbit
from .font_catalog import KEEP_ASCII, classify_font, label_kind
from .legacy_maps import try_convert as legacy_try_convert
from .zg_repair import repair_zawgyi

DEFAULT_ZAWGYI_MIN = 0.5


@dataclass
class ConvertResult:
    """Result of :func:`convert` / :func:`normalize` / :func:`to_unicode`."""

    text: str
    kind: str = ""
    zawgyi_score: float = 0.0
    branch: str = "passthrough"  # legacy | zawgyi | normalize | passthrough
    stats: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.text


def _detector():
    try:
        import myanmartools

        return myanmartools.ZawgyiDetector()
    except Exception:
        return None


def zawgyi_probability(text: str, detector=None) -> float:
    det = detector if detector is not None else _detector()
    if det is None:
        return 0.0
    sub = "".join(c for c in (text or "") if "\u1000" <= c <= "\u109F" or c in " \n")
    if not sub.strip():
        return 0.0
    try:
        score = float(det.get_zawgyi_probability(sub))
    except Exception:
        return 0.0
    if score != score or score < 0.0 or score > 1.0:
        return 0.0
    return score


def resolve_kind(font: Optional[str] = None, kind: Optional[str] = None) -> str:
    if kind:
        return kind.strip().lower()
    if font:
        return label_kind(font) or classify_font(font)
    return ""


def normalize_with_stats(
    text: str,
    *,
    repair_order: bool = True,
    fix_kinzi: bool = True,
    cleanup: bool = True,
) -> ConvertResult:
    """Normalize already-Unicode Burmese text.

    Safe to call on converted Unicode or native Unicode. Does **not** run
    Zawgyi/legacy encoding conversion — use :func:`convert` / :func:`to_unicode`
    when the source encoding may be Zawgyi or a legacy font.
    """
    out = text or ""
    stats: dict[str, Any] = {"phase2": {}, "kinzi_fixes": 0}

    if repair_order:
        p2_stats: dict[str, int] = {}
        out = phase2.to_unicode_text_phase2(out, zawgyi_rabbit.convert, stats=p2_stats)
        stats["phase2"] = p2_stats

    if fix_kinzi and getattr(kinzi, "KINZI_ENABLED", False):
        out, n = kinzi.fix_text(out)
        stats["kinzi_fixes"] = n

    if cleanup:
        out = post.cleanup(out)

    return ConvertResult(text=out, kind="unicode", branch="normalize", stats=stats)


def normalize(
    text: str,
    *,
    repair_order: bool = True,
    fix_kinzi: bool = True,
    cleanup: bool = True,
) -> str:
    """Normalize already-Unicode Burmese text. See :func:`normalize_with_stats`."""
    return normalize_with_stats(
        text,
        repair_order=repair_order,
        fix_kinzi=fix_kinzi,
        cleanup=cleanup,
    ).text


def convert_with_stats(
    text: str,
    font: Optional[str] = None,
    kind: Optional[str] = None,
    *,
    auto: bool = True,
    zawgyi_min: float = DEFAULT_ZAWGYI_MIN,
    normalize_output: bool = True,
    repair_order: bool = True,
    fix_kinzi: bool = True,
    cleanup: bool = True,
    detector=None,
) -> ConvertResult:
    """Universal converter: legacy / Zawgyi / mixed → Myanmar Unicode (+ normalize).

    Parameters
    ----------
    text:
        Input string (already extracted; this library does not open PDFs).
    font:
        Optional embedded font name, e.g. ``\"WinInnwa\"`` or ``\"Zawgyi-One\"``.
    kind:
        Optional catalog kind: ``win``, ``academy``, ``ce``, ``zawgyi``, …
    auto:
        If True and no legacy kind is given, use Zawgyi detection / Phase 1.
    normalize_output:
        After encoding conversion, run Unicode normalization (Phase 2 / Kinzi / cleanup).
    """
    raw = text or ""
    resolved = resolve_kind(font, kind)
    faces = [part.strip() for part in (font or "").replace("|", ",").split(",") if part.strip()]
    stats: dict[str, Any] = {"phase1": {}}
    det = detector if detector is not None else _detector()
    score = zawgyi_probability(raw, det) if (auto or resolved in ("", "zawgyi", "unicode")) else 0.0

    out = raw
    branch = "passthrough"
    did_encode = False

    # Branch A: named legacy ASCII fonts (WinInnwa, Academy, CE, …)
    if resolved in KEEP_ASCII:
        converted = legacy_try_convert(raw, faces=faces or None, kind=resolved)
        if not converted and resolved == "win":
            from .legacy_maps import _win_syllable

            converted = _win_syllable(raw, require_page=False, has_win_font=True) or ""
        if converted:
            out = converted
            branch = "legacy"
            did_encode = True

    # Branch B: Zawgyi / auto Rabbit path (also if legacy convert produced nothing)
    if not did_encode and (
        resolved == "zawgyi"
        or (auto and (score >= zawgyi_min or phase1.has_zg_range(raw)))
    ):
        branch = "zawgyi"
        repaired = repair_zawgyi(out)
        if repaired != out:
            stats["zg_repair"] = True
            out = repaired
        p1_stats: dict[str, int] = {}
        out = phase1.to_unicode_text(
            out, det, zawgyi_min, rabbit_convert_fn=zawgyi_rabbit.convert, stats=p1_stats
        )
        stats["phase1"] = p1_stats
        did_encode = True

    if normalize_output:
        norm = normalize_with_stats(
            out,
            repair_order=repair_order,
            fix_kinzi=fix_kinzi,
            cleanup=cleanup,
        )
        stats.update(norm.stats)
        out = norm.text
        if branch == "passthrough" and resolved in ("", "unicode"):
            branch = "normalize"

    return ConvertResult(
        text=out,
        kind=resolved or ("zawgyi" if branch == "zawgyi" else ("unicode" if branch == "normalize" else "")),
        zawgyi_score=score,
        branch=branch,
        stats=stats,
    )


def convert(
    text: str,
    font: Optional[str] = None,
    kind: Optional[str] = None,
    *,
    auto: bool = True,
    zawgyi_min: float = DEFAULT_ZAWGYI_MIN,
    normalize_output: bool = True,
    repair_order: bool = True,
    fix_kinzi: bool = True,
    cleanup: bool = True,
    detector=None,
) -> str:
    """Universal converter to Myanmar Unicode. See :func:`convert_with_stats`."""
    return convert_with_stats(
        text,
        font=font,
        kind=kind,
        auto=auto,
        zawgyi_min=zawgyi_min,
        normalize_output=normalize_output,
        repair_order=repair_order,
        fix_kinzi=fix_kinzi,
        cleanup=cleanup,
        detector=detector,
    ).text


def to_unicode(
    text: str,
    font: Optional[str] = None,
    kind: Optional[str] = None,
    *,
    auto: bool = True,
    zawgyi_min: float = DEFAULT_ZAWGYI_MIN,
    cleanup: bool = True,
    detector=None,
) -> str:
    """Alias for :func:`convert` — one-call encode-detect → Unicode → normalize."""
    return convert(
        text,
        font=font,
        kind=kind,
        auto=auto,
        zawgyi_min=zawgyi_min,
        cleanup=cleanup,
        detector=detector,
    )


__all__ = [
    "ConvertResult",
    "KEEP_ASCII",
    "classify_font",
    "convert",
    "convert_with_stats",
    "label_kind",
    "normalize",
    "normalize_with_stats",
    "resolve_kind",
    "to_unicode",
    "zawgyi_probability",
]
