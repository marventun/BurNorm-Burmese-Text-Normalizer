"""BurNorm — Burmese PDF/legacy-font & Zawgyi → Unicode + normalize."""

from .api import (
    ConvertResult,
    KEEP_ASCII,
    classify_font,
    convert,
    convert_with_stats,
    label_kind,
    normalize,
    normalize_with_stats,
    resolve_kind,
    to_unicode,
    zawgyi_probability,
)
from .font_catalog import keeps_legacy_text

__version__ = "0.1.0"
__all__ = [
    "ConvertResult",
    "KEEP_ASCII",
    "classify_font",
    "convert",
    "convert_with_stats",
    "keeps_legacy_text",
    "label_kind",
    "normalize",
    "normalize_with_stats",
    "resolve_kind",
    "to_unicode",
    "zawgyi_probability",
    "__version__",
]
