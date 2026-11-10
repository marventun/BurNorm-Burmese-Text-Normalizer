"""Public convert API: legacy / Zawgyi / other fonts → Myanmar Unicode."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from . import font_catalog, kinzi, phase1, phase2, post, zawgyi_rabbit
from .font_catalog import KEEP_ASCII, classify_font, label_kind
from .legacy_maps import try_convert as legacy_try_convert

DEFAULT_ZAWGYI_MIN = 0.5


@dataclass
class ConvertResult:
    text: str
    kind: str = ""
    zawgyi_score: float = 0.0
    branch: str = "passthrough"  # legacy | zawgyi | unicode_scrub | passthrough
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


def convert(
    text: str,
    font: Optional[str] = None,
    kind: Optional[str] = None,
    *,
    auto: bool = True,
    zawgyi_min: float = DEFAULT_ZAWGYI_MIN,
    cleanup: bool = True,
    detector=None,
) -> str:
    """Convert legacy / Zawgyi text to Myanmar Unicode.

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
    cleanup:
        Apply light NFC / mark cleanup after conversion.
    """
    return convert_with_stats(
        text,
        font=font,
        kind=kind,
        auto=auto,
        zawgyi_min=zawgyi_min,
        cleanup=cleanup,
        detector=detector,
    ).text


def convert_with_stats(
    text: str,
    font: Optional[str] = None,
    kind: Optional[str] = None,
    *,
    auto: bool = True,
    zawgyi_min: float = DEFAULT_ZAWGYI_MIN,
    cleanup: bool = True,
    detector=None,
) -> ConvertResult:
    """Same as :func:`convert`, but also returns kind / branch / stats."""
    raw = text or ""
    resolved = resolve_kind(font, kind)
    faces = [part.strip() for part in (font or "").replace("|", ",").split(",") if part.strip()]
    stats: dict[str, Any] = {"phase1": {}, "phase2": {}}
    det = detector if detector is not None else _detector()
    score = zawgyi_probability(raw, det) if (auto or resolved in ("", "zawgyi", "unicode")) else 0.0

    out = raw
    branch = "passthrough"

    # Branch A: named legacy ASCII fonts (WinInnwa, Academy, CE, …)
    if resolved in KEEP_ASCII:
        converted = legacy_try_convert(raw, faces=faces or None, kind=resolved)
        if not converted and resolved == "win":
            from .legacy_maps import _win_syllable

            converted = _win_syllable(raw, require_page=False, has_win_font=True) or ""
        if converted:
            out = converted
            branch = "legacy"
            p2_stats: dict[str, int] = {}
            out = phase2.to_unicode_text_phase2(out, zawgyi_rabbit.convert, stats=p2_stats)
            stats["phase2"] = p2_stats
            if getattr(kinzi, "KINZI_ENABLED", False):
                out, n = kinzi.fix_text(out)
                stats["kinzi_fixes"] = n
            if cleanup:
                out = post.cleanup(out)
            return ConvertResult(text=out, kind=resolved, zawgyi_score=score, branch=branch, stats=stats)

    # Branch B: Zawgyi / auto Unicode scrub path
    run_zg = False
    if resolved == "zawgyi":
        run_zg = True
        branch = "zawgyi"
    elif auto and (
        score >= zawgyi_min
        or phase1.has_zg_range(raw)
        or phase1.page_has_myanmar_unit(raw)
    ):
        run_zg = True
        branch = "zawgyi" if (score >= zawgyi_min or phase1.has_zg_range(raw)) else "unicode_scrub"

    p1_stats: dict[str, int] = {}
    if run_zg:
        out = phase1.to_unicode_text(
            out, det, zawgyi_min, rabbit_convert_fn=zawgyi_rabbit.convert, stats=p1_stats
        )
    else:
        out, _ = phase1.scrub_residual_zawgyi_glyphs(out)
        branch = branch if branch != "passthrough" else ("unicode_scrub" if resolved == "unicode" else "passthrough")
    stats["phase1"] = p1_stats

    p2_stats = {}
    out = phase2.to_unicode_text_phase2(out, zawgyi_rabbit.convert, stats=p2_stats)
    stats["phase2"] = p2_stats
    if getattr(kinzi, "KINZI_ENABLED", False):
        out, n = kinzi.fix_text(out)
        stats["kinzi_fixes"] = n
    if cleanup:
        out = post.cleanup(out)

    return ConvertResult(
        text=out,
        kind=resolved or ("zawgyi" if branch == "zawgyi" else ""),
        zawgyi_score=score,
        branch=branch,
        stats=stats,
    )


__all__ = [
    "ConvertResult",
    "KEEP_ASCII",
    "classify_font",
    "convert",
    "convert_with_stats",
    "label_kind",
    "resolve_kind",
    "zawgyi_probability",
]
