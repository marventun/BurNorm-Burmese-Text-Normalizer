from burnorm.legacy_maps import convert_table, table_for_face, table_for_kind


def test_table_lookup():
    assert table_for_kind("win") == "WinInnwa"
    assert table_for_face("WinInnwa") == "WinInnwa"
    assert table_for_kind("academy") == "Academy"


def test_convert_table_smoke():
    # Mapping should accept empty and return empty-ish safely.
    assert convert_table("", "WinInnwa") == ""
    # Unmapped Latin without a real WinInnwa page may pass through or map;
    # just ensure no exception and a string result.
    out = convert_table("abc", "WinInnwa")
    assert isinstance(out, str)
