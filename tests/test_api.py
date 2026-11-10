from myanmar_uni_convert import classify_font, convert, convert_with_stats, label_kind
from myanmar_uni_convert import zawgyi_rabbit


def test_classify_wininnwa():
    assert classify_font("WinInnwa") == "win"
    assert label_kind("WinInnwa") == "win"


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


def test_convert_with_stats_shape():
    result = convert_with_stats("hello", auto=False)
    assert hasattr(result, "text")
    assert hasattr(result, "branch")
    assert isinstance(result.stats, dict)


def test_legacy_try_with_win_kind_empty_safe():
    # Empty / English-looking should not explode.
    out = convert("Hello world", font="WinInnwa", auto=False)
    assert isinstance(out, str)
