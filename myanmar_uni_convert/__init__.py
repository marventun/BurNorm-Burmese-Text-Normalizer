"""myanmar-uni-convert — legacy / Zawgyi Myanmar encodings → Unicode."""

from .api import (
    ConvertResult,
    KEEP_ASCII,
    classify_font,
    convert,
    convert_with_stats,
    label_kind,
    resolve_kind,
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
    "resolve_kind",
    "zawgyi_probability",
    "__version__",
]
