from burnorm import (
    classify_font,
    convert,
    convert_with_stats,
    label_kind,
    normalize,
    normalize_with_stats,
    to_unicode,
)
from burnorm import zawgyi_rabbit


def test_classify_wininnwa():
    assert classify_font("WinInnwa") == "win"
    assert label_kind("WinInnwa") == "win"


def test_classify_short_legacy_names():
    assert classify_font("CE") == "ce"
    assert classify_font("King") == "king"
    assert label_kind("CE") == "ce"
    assert label_kind("King") == "king"


def test_classify_zawgyi():
    assert classify_font("Zawgyi-One") == "zawgyi"


def test_rabbit_roundtrip_smoke():
    # Known Zawgyi sample from Rabbit docs (smoke only).
    zg = "မဂၤလာပါ"
    uni = zawgyi_rabbit.convert(zg)
    assert uni
    assert any("\u1000" <= c <= "\u109F" for c in uni)


def test_convert_passthrough_unicode():
    text = "မင်္ဂလာပါ"
    out = convert(text, kind="unicode", auto=False)
    assert "မ" in out


def test_to_unicode_alias():
    text = "မင်္ဂလာပါ"
    assert to_unicode(text, kind="unicode", auto=False) == convert(
        text, kind="unicode", auto=False
    )


def test_normalize_unicode_smoke():
    text = "မင်္ဂလာပါ"
    out = normalize(text)
    assert "မ" in out
    result = normalize_with_stats(text)
    assert result.branch == "normalize"
    assert result.kind == "unicode"
    assert isinstance(result.stats, dict)


def test_normalize_empty_safe():
    assert normalize("") == ""
    assert normalize_with_stats("").text == ""


def test_convert_with_stats_shape():
    result = convert_with_stats("hello", auto=False)
    assert hasattr(result, "text")
    assert hasattr(result, "branch")
    assert isinstance(result.stats, dict)


def test_legacy_try_with_win_kind_empty_safe():
    # Empty / English-looking should not explode.
    out = convert("Hello world", font="WinInnwa", auto=False)
    assert isinstance(out, str)
