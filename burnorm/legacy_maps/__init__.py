# -*- coding: utf-8 -*-
"""Legacy Myanmar ASCII/ANSI fonts → Unicode via Burglish OE tables.

Tables from scriptive/burglish (MIT). Converts through Myanmar3 slots, plus
complete multi-codepoint ligature / stacked-consonant slot expansions, then
applies visual reorder for ေ / ြ and post-base kinzi င်္.

Win Myanmar pages prefer the syllable-aware WinInnwa converter. Academy, CE,
MyaZedi, Metrix, Gandamar, King, Wwin, and MS-Heavy use these OE tables.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

_DATA = json.loads((Path(__file__).resolve().parent / "burg_fonts.json").read_text(encoding="utf-8"))
_TARGET = "Myanmar3"
_MARK_ORDER = {"\u103B": 0, "\u103C": 1, "\u103D": 2, "\u103E": 3, "\u1031": 4}
_VISUAL = re.compile(
    r"(?<![\u1000-\u102A\u1039\u103B-\u103E])([\u1031\u103C]+)([\u1000-\u1021](?:\u1039[\u1000-\u1021])?)([\u103B-\u103E]*)"
)
_ENGLISH = re.compile(
    r"\b(the|and|of|to|in|is|for|that|with|on|as|are|this|be|or|by|from|at|"
    r"an|was|were|have|has|not|but|what|all|can|their|which|you|your|will|"
    r"chapter|page|figure|table|section)\b",
    re.IGNORECASE,
)
_MARKS = set("<>;&[]{}*#@+$=~")

# Catalog kind → burglish table name
KIND_TO_TABLE = {
    "win": "WinInnwa",
    "academy": "Academy",
    "ce": "CE",
    "myazedi": "MyaZedi",
    "legacy": "Metrix",
    "gandamar": "Gandamar",
    "king": "King",
    "wwin": "WwinBurmese",
    "msheavy": "MSHEAVY",
    "kannaka": "Kannaka",
    "mmyanmar": "MMyanmar1",
}

FACE_TO_TABLE = {}
for table, info in _DATA.items():
    for css in info.get("css") or []:
        FACE_TO_TABLE[re.sub(r"[^0-9a-z]+", "", css.lower())] = table
    FACE_TO_TABLE[re.sub(r"[^0-9a-z]+", "", table.lower())] = table

FACE_TO_TABLE.update(
    {
        "winresearcher": "WinInnwa",
        "winmandalay": "WinInnwa",
        "winbagan": "WinInnwa",
        "winmajestic": "WinInnwa",
        "winthida": "WinInnwa",
        "winzayar": "WinInnwa",
        "winyadanar": "WinInnwa",
        "winyadanapon": "WinInnwa",
        "winkyaw": "WinInnwa",
        "winalinkar": "WinInnwa",
        "wingantgaw": "WinInnwa",
        "winpadauk": "WinInnwa",
        "wintaunggyi": "WinInnwa",
        "wintaungyi": "WinInnwa",
        "winpyitinehtaung": "WinInnwa",
        "winsittwe": "WinInnwa",
        "winsittway": "WinInnwa",
        "winpazundaung": "WinInnwa",
        "winkaung": "WinInnwa",
        "winmyat": "WinInnwa",
        "winshwemyan": "WinInnwa",
        "wintheikpa": "WinInnwa",
        "winkalaw": "WinInnwa",
        "aeyar": "Academy",
        "aekari": "Academy",
        "cefont": "CE",
        "cetext": "CE",
        "cenormal": "CE",
        "cebold": "CE",
        "cebook": "CE",
        "cenews": "CE",
        "cecomputereain": "CE",
        "ceheading": "CE",
        "computereain": "CE",
        "ceclassic": "CE",
        "ceexcel": "CE",
        "metrix1": "Metrix",
        "metrix3": "Metrix",
        "metix18": "Metrix",
        "matrix": "Metrix",
        "gandamarletter1": "Gandamar",
        "kingmyanmarsar": "King",
        "wwinburmese": "WwinBurmese",
        "wwinburmese1": "WwinBurmese",
        "wwin": "WwinBurmese",
        "winburmese": "WwinBurmese",
        "winhanponnya": "WwinBurmese",
        "myawaddy01": "WwinBurmese",
        "myawaddy05": "WwinBurmese",
        "hannwethaki": "WwinBurmese",
        "blnewstrawtype": "WwinBurmese",
        "msheavy": "MSHEAVY",
        "msmoom": "MSHEAVY",
        "mmyanmar1": "MMyanmar1",
        "bit": "MyaZedi",
        "mandalay": "MyaZedi",
        "myazedi": "MyaZedi",
        "shwe": "Metrix",
        "shwethin": "Metrix",
        "arthouse": "Metrix",
        "w10arthousewin": "Metrix",
        "w42arthouse": "Metrix",
        "w53arthouse": "Metrix",
        "w67arthouse": "Metrix",
        "w68arthouse": "Metrix",
        "wanthu": "Metrix",
        "bagan": "Metrix",
        "tharawun": "Metrix",
        "pyimyanmar": "Metrix",
        "shwehintha": "Metrix",
    }
)

_SKIP = {0, 4095}
_SKIP_TABLES = {_TARGET, "Zawgyi", "UniBurma"}

# Multi-codepoint Unicode strings for Burglish OE slots where Myanmar3 has 0
_SLOT_STRINGS = {
    33: "\u1039\u1000",
    34: "\u1039\u1001",
    35: "\u1039\u1002",
    36: "\u1039\u1003",
    38: "\u1039\u1005",
    39: "\u1039\u1006",
    40: "\u1039\u1007",
    41: "\u1039\u1008",
    43: "\u1039\u100b",
    44: "\u1039\u100c",
    47: "\u1039\u100e",
    48: "\u1039\u100f",
    49: "\u1039\u1010",
    50: "\u1039\u1011",
    51: "\u1039\u1012",
    52: "\u1039\u1013",
    53: "\u1039\u1014",
    54: "\u1039\u1015",
    55: "\u1039\u1016",
    56: "\u1039\u1017",
    57: "\u1039\u1018",
    60: "\u1039\u101c",
    62: "\u1039\u1019",
    83: "\u1004\u103a\u1039",
    86: "\u102b\u103a",
    91: "\u103d\u103e",
    96: "\u103b",
    97: "\u103b",
    100: "\u103c",
    101: "\u103c",
    102: "\u103c",
    103: "\u103c",
    104: "\u103c",
    105: "\u103c",
    106: "\u103c",
    109: "\u1037",
    110: "\u1037",
    115: "\u1014",
    116: "\u101b",
    117: "\u100b\u1039\u100c",
    129: "\u102f",
    130: "\u1030",
    131: "\u103e\u102f",
    132: "\u103e\u1030",
    134: "\u103e",
    136: "\u1004\u103a\u1039\u102d",
    137: "\u1004\u103a\u1039\u102e",
    138: "\u102d\u1036",
    139: "\u1031\u103d",
    142: "\u103b\u103d",
    143: "\u103b\u103e",
    144: "\u103b\u103d\u103e",
    146: "\u103c\u103d",
    147: "\u103c\u102f",
    155: "\u103e",
    156: "\u1014",
    159: "\u104e",
    171: "\u100b\u1039\u100b",
    172: "\u100d\u1039\u100d",
    173: "\u100d\u1039\u100e",
    175: "\u100f\u1039\u100d",
    176: "\u100f\u1039\u100c",
    177: "\u100f\u1039\u100f",
    202: "\u1039\u1010\u103d",
    204: "\u1039\u1018",
    206: "\u1039\u1007",
    207: "\u1039\u1010",
    208: "\u1039\u1011",
    209: "\u1039\u1018",
    213: "\u103e\u102f",
    215: "\u102f",
}


def _maps(table: str):
    src = _DATA[table]["OE"]
    dst = _DATA[_TARGET]["OE"]
    forward = {}
    for index, code in enumerate(src):
        if code in _SKIP:
            continue
        if index in _SLOT_STRINGS:
            forward[code] = _SLOT_STRINGS[index]
            continue
        if index >= len(dst):
            break
        target = dst[index]
        if target in _SKIP:
            continue
        forward[code] = chr(target)
    if table == "WwinBurmese":
        forward.update({
            ord("O"): "\u1025",
            ord("_"): "\u103e\u102f",
            ord("‹"): "\u1037",
            ord("‡"): "\u103e",
            ord("ò"): "\u103c\u102f",
            ord("ó"): "\u103c\u102d\u102f",
            ord("º"): "\u103c",
            ord("Ë"): "\u100b",
            ord("À"): "\u100f\u1039\u100f",
            ord("±"): "\u101b",
            ord("·"): " ",
            ord("M"): "\u103c",
            ord("B"): "\u103c",
            ord("û"): "\u103c\u102f",
            ord("`"): "\u1039\u1015",
            ord("R"): "\u1039\u1019",
            ord("|"): "\u103b\u103d",
            0x17: " ",
        })
    elif table == "MyaZedi":
        forward.update({
            0x10A0: " ",
            0x10A1: "\u102f",
            0x1080: "\u103e",
        })
    return forward


_CACHE = {name: _maps(name) for name in _DATA if name not in _SKIP_TABLES}


def table_for_face(name: str) -> str:
    key = re.sub(r"[^0-9a-z]+", "", ((name or "").split("+")[-1]).lower())
    if key in FACE_TO_TABLE:
        return FACE_TO_TABLE[key]
    if key.startswith("wwin") or key.startswith("winhan") or key.startswith("myawaddy") or key.startswith("hannwe"):
        return "WwinBurmese"
    if "arthouse" in key or key.startswith("metrix") or key.startswith("metix"):
        return "Metrix"
    # Arlarwade / Amyanmar (မြန်မာသဒ္ဒါပေါင်းချုပ် and similar) use the Kannaka OE map.
    if key.startswith("arlar") or key in ("amyanmar", "kannaka"):
        return "Kannaka"
    if key.startswith("win"):
        return "WinInnwa"
    return ""


def table_for_kind(kind: str) -> str:
    return KIND_TO_TABLE.get(kind or "", "")


def _logical_cluster(match):
    pre = match.group(1)
    base = match.group(2)
    post_meds = list(match.group(3) or "")
    meds = [ch for ch in pre if ch != "\u1031"] + post_meds
    e_marks = [ch for ch in pre if ch == "\u1031"]
    ordered = []
    for ch in sorted(meds, key=lambda item: _MARK_ORDER.get(item, 9)):
        if ch not in ordered:
            ordered.append(ch)
    return base + "".join(ordered) + ("\u1031" if e_marks else "")


def convert_table(text: str, table: str) -> str:
    if not text or table not in _CACHE:
        return text or ""
    mapping = _CACHE[table]
    out = []
    for ch in text:
        mapped = mapping.get(ord(ch))
        if mapped is None:
            out.append(ch)
            continue
        if mapped.startswith("\u1004\u103a\u1039") and out:
            tail = mapped[3:]
            ins = len(out)
            while ins > 0 and out[ins - 1] in "\u103b\u103c\u103d\u103e":
                ins -= 1
            if ins > 0 and "\u1000" <= out[ins - 1][:1] <= "\u1021":
                ins -= 1
            while ins > 0 and out[ins - 1] in ("\u1031", "\u103c", "\u103c\u103d"):
                ins -= 1
            out.insert(ins, "\u1004\u103a\u1039")
            if tail:
                out.append(tail)
            continue
        out.append(mapped)
    result = "".join(out)
    for _ in range(4):
        nxt = _VISUAL.sub(_logical_cluster, result)
        if nxt == result:
            break
        result = nxt
    # Kannaka/Arlarwade often emits အြက instead of အကြ
    for _ in range(3):
        nxt = re.sub(r"\u1021\u103c([\u1000-\u1021])", "အ\\1\u103c", result)
        if nxt == result:
            break
        result = nxt
    result = re.sub(r"\u1036([\u103b-\u103e\u102d-\u1030]+)", "\\1\u1036", result)
    result = re.sub(r"([\u102f\u1030])([\u103b-\u103e]+)", r"\2\1", result)
    result = re.sub(r"([\u102f\u1030])([\u102d\u102e])", r"\2\1", result)
    # Common Kannaka / Arlarwade title ligature slip
    result = result.replace("သဒ္ထါ", "သဒ္ဒါ")
    return result


def convert_face(text: str, face: str) -> str:
    table = table_for_face(face)
    return convert_table(text, table) if table else text


def convert_kind(text: str, kind: str) -> str:
    table = table_for_kind(kind)
    return convert_table(text, table) if table else text


def _quality(text: str) -> int:
    asat = len(re.findall(r"[\u1000-\u1021]\u103a", text or ""))
    wa = len(re.findall(r"[\u1000-\u1021]\u103d", text or ""))
    leftover = len(re.findall(r"[\u1033\u1034\u105a-\u109f]", text or ""))
    return asat + wa - 4 * leftover


def _ascii_letters(text: str) -> int:
    return sum(1 for ch in text or "" if ch.isascii() and ch.isalpha())


def _myanmar_letters(text: str) -> int:
    return sum(1 for ch in text or "" if "\u1000" <= ch <= "\u109F")


def _myazedi_ext(text: str) -> int:
    return sum(1 for ch in text or "" if "\u1050" <= ch <= "\u10A1")


def _looks_english(text: str) -> bool:
    return len(_ENGLISH.findall(text or "")) >= 8


def try_convert(text: str, faces=None, kind: str = "") -> str:
    """Return Unicode when a named legacy map clearly helps; otherwise \"\"."""
    if not text:
        return ""
    ascii_n = _ascii_letters(text)
    my_n = _myanmar_letters(text)
    mz_ext = _myazedi_ext(text)
    marks = sum(ch in _MARKS for ch in text)
    named = bool(kind or faces)
    tables = []
    if kind:
        table = table_for_kind(kind)
        if table:
            tables.append(table)
    for face in faces or []:
        table = table_for_face(face)
        if table and table not in tables:
            tables.append(table)
    # MyaZedi uses U+1000..U+10A1 slots instead of ASCII
    if ("MyaZedi" in tables or mz_ext >= 6) and my_n >= 10:
        converted = convert_table(text, "MyaZedi")
        if _myazedi_ext(converted) < mz_ext or _quality(converted) > _quality(text):
            return converted
    min_ascii = 2 if named else 20
    if ascii_n < min_ascii or my_n > ascii_n * 0.25:
        return ""
    if not tables:
        return ""
    if _looks_english(text) and (not named or marks < 4):
        return ""
    if ascii_n >= 30 and my_n < 5 and marks < 2 and not faces:
        return ""
    best = ""
    best_score = None
    for table in tables:
        converted = convert_table(text, table)
        produced = _myanmar_letters(converted)
        leftover = _ascii_letters(converted)
        need = max(3 if named else 16, int(ascii_n * 0.70))
        if produced < need:
            continue
        if leftover > max(3, int(ascii_n * 0.05)):
            continue
        if my_n and produced < my_n:
            continue
        quality = _quality(converted)
        if quality < max(0 if named else 1, produced // 80):
            continue
        score = (quality, produced, -leftover)
        if best_score is None or score > best_score:
            best_score = score
            best = converted
    return best


_WIN_PALI_PRE = [
    ("aဋ္ဌm", "\u1039\u100c\u102c"),
    ("aဏ္ဍm", "\u1039\u100d\u102c"),
    ("Åm", "\u1039\u1010\u102c"),
    ("Åd", "\u1039\u1010\u102d"),
    ("ÅK", "\u1039\u1010\u102f"),
    ("ÅD", "\u1039\u1010\u102e"),
    ("Å", "\u1039\u1010"),
    ("Ém", "\u1039\u1010\u103d\u102c"),
    ("É", "\u1039\u1010\u103d"),
    ("åm", "\u1039\u1010\u102c"),
    ("å", "\u1039\u1010"),
    ("ö", "\u1039\u1005"),
    ("®", "\u1039\u1019"),
    ("Á", "\u1039\u1017"),
    ("¨", "\u1039\u1012"),
    ("¾", "\u1039\u1002"),
    ("´", "\u1039\u1012"),
    ("¬", "\u1039\u1010\u1039\u1011"),
    ("Ó", "\u1009\u102c"),
    ("½", "\u101b"),
    ("§dK;", "\u103e\u102d\u102f\u1038"),
    ("§K;", "\u103e\u102d\u102f\u1038"),
    ("§", "\u103e"),
    ("I;", "\u103e\u102f\u1038"),
    ("I", "\u103e\u102f"),
    ("Hh", "\u1036\u1037"),
    ("H", "\u1036"),
    ("d|d", "\u102d\u100b\u1039\u100c\u102d"),
    ("|", "\u100b\u1039\u100c"),
    ("Fm", "\u1039\u1001\u103b\u102c"),
    ("GU", "\u103d\u1037"),
    ("G", "\u103d"),
    ("J", "\u1032"),
    ("ç", "\u104a"),
    ("]]", "“"),
    ("}}", "”"),
    ("«", "“"),
    ("»", "”"),
]


def _win_clean_post(text: str) -> str:
    for src, dst in _WIN_PALI_PRE:
        if src in text:
            text = text.replace(src, dst)
    text = re.sub(r"(?<=[\u1000-\u103F])D;", "\u102e\u1038", text)
    text = re.sub(r"(?<=[\u1000-\u103F])D", "\u102e", text)
    text = re.sub(r"(?<=[\u1000-\u103F])dK;", "\u102d\u102f\u1038", text)
    text = re.sub(r"(?<=[\u1000-\u103F])dK", "\u102d\u102f", text)
    text = re.sub(r"(?<=[\u1000-\u103F])K;", "\u102f\u1038", text)
    text = re.sub(r"(?<=[\u1000-\u103F])K", "\u102f", text)
    text = re.sub(r"(?<=[\u1000-\u103F])d", "\u102d", text)
    text = re.sub(r"(?<=[\u1000-\u103F])sm;", "\u103b\u102c\u1038", text)
    text = re.sub(r"(?<=[\u1000-\u103F])Sg", "\u103e\u102b", text)
    text = re.sub(r"(?<=[\u1000-\u103F])S", "\u103e", text)
    text = re.sub(r"(?<=[\u1000-\u103F])g;", "\u102b\u1038", text)
    text = re.sub(r"(?<=[\u1000-\u103F])g", "\u102b", text)
    text = re.sub(r"(?<=[\u1000-\u103F])m;", "\u102c\u1038", text)
    text = re.sub(r"(?<=[\u1000-\u103F])m", "\u102c", text)
    text = re.sub(r"(?<=[\u1000-\u103F])k", "\u102f", text)
    text = re.sub(r"(?<=[\u1000-\u103F])Y", "\u1037", text)
    text = re.sub(r"(?<=[\u1000-\u103F])U", "\u1037", text)
    text = re.sub(r"(?<=[\u1000-\u103F])Q", "\u103b\u103e", text)
    text = re.sub(r"(?<=[\u1000-\u103F]);", "\u1038", text)
    text = re.sub(r"\](?=[\u1000-\u103F])", "“", text)
    text = re.sub(r"(?<=[\u1000-\u104F])\}", "”", text)
    text = re.sub(r"\u1036([\u103b-\u103e\u102d-\u1030]+)", "\\1\u1036", text)
    text = re.sub(r"([\u102f\u1030])([\u103b-\u103e]+)", r"\2\1", text)
    text = re.sub(r"([\u102f\u1030])([\u102d\u102e])", r"\2\1", text)
    return text


def _win_syllable(text: str, require_page: bool = True, has_win_font: bool = False) -> str:
    """Syllable-aware WinInnwa → Unicode. Safer than the OE byte map for Win."""
    ascii_n = _ascii_letters(text)
    my_n = _myanmar_letters(text)
    min_ascii = 40 if require_page else 6
    if ascii_n < min_ascii or my_n > ascii_n * 0.25:
        return ""
    if _looks_english(text) and (not has_win_font or sum(ch in _MARKS for ch in text) < 4):
        return ""
    try:
        from ..wininnwa.converter import convert as win_convert
        converted = _win_clean_post(win_convert(text, "wininnwa", "unicode"))
    except Exception:
        return ""
    produced = _myanmar_letters(converted)
    leftover = _ascii_letters(converted)
    need = max(min_ascii, int(ascii_n * 0.88)) if require_page else max(4, int(ascii_n * 0.78))
    if produced < need:
        return ""
    if leftover > max(5, int(ascii_n * 0.08)):
        return ""
    return converted


def _convert_line_by_line(text: str, tables, has_win: bool) -> str:
    # For mixed English + Legacy ASCII pages (e.g. CC license in English + WinInnwa/Wwin Burmese)
    from ..wininnwa.converter import convert as win_convert
    lines = text.splitlines()
    out_lines = []
    converted_any = False
    for line in lines:
        s = line.strip()
        if not s:
            out_lines.append(line)
            continue
        # If this individual line has >= 2 English stopwords and no legacy punctuation, keep it as English!
        en_words = len(_ENGLISH.findall(s))
        marks = sum(ch in _MARKS for ch in s)
        if en_words >= 2 and marks < 2:
            out_lines.append(line)
            continue
        a_n = _ascii_letters(s)
        if a_n < 3:
            out_lines.append(line)
            continue
        done_line = ""
        if has_win and ("WinInnwa" in tables or not tables):
            try:
                cand = _win_clean_post(win_convert(line, "wininnwa", "unicode"))
                if _myanmar_letters(cand) >= max(2, int(a_n * 0.75)):
                    done_line = cand
            except Exception:
                pass
        if not done_line:
            for tbl in tables:
                cand = convert_table(line, tbl)
                if _myanmar_letters(cand) >= max(2, int(a_n * 0.70)) and _quality(cand) >= 0:
                    done_line = cand
                    break
        if done_line:
            out_lines.append(done_line)
            converted_any = True
        else:
            out_lines.append(line)
    return "\n".join(out_lines) if converted_any else ""


_ENG_TOKEN_DICT = re.compile(
    r"^(the|and|of|to|in|is|for|that|with|on|as|are|this|be|or|by|from|at|"
    r"an|was|were|have|has|not|but|what|all|can|their|which|you|your|will|"
    r"chapter|page|figure|table|section|system|systems|operating|source|open|"
    r"getting|start|started|linux|windows|kernel|shell|command|commands|line|"
    r"interpreter|program|programs|programming|file|files|install|installation|"
    r"user|users|account|accounts|network|networking|server|servers|client|"
    r"data|database|code|web|application|applications|interface|commercial|"
    r"distribution|distros|media|device|devices|driver|drivers|root|edit|"
    r"warning|wanning|hardware|software|computer|cracker|cracking|reverse|"
    r"engineering|basic|language|version|guide|book|note|notes|creative|"
    r"commons|attribution|sharealike|international|license|licensed|under|"
    r"work|view|copy|visit|myanmar|knowledge|society|education|federal|"
    r"field|type|types|method|methods|graphic|mode|dialog|box|screen|"
    r"primary|swap|memory|directory|folder|partition|partitions|loader|"
    r"language|setting|settings|password|configuration|welcome|skip|"
    r"democracy|real|life|case|sensitive|individual|operate|partition|auto|"
    r"manual|next|click|hard|disk|drive|drives|format|boot|loader|password)$",
    re.IGNORECASE,
)


def _is_english_token_in_win(token: str) -> bool:
    core = token.strip("()[]{}.,:;\"'!?/-\\")
    if not core or not any(c.isascii() and c.isalpha() for c in core):
        return False
    if "http://" in core or "https://" in core or "www." in core or ".com" in core or ".org" in core:
        return True
    if _ENG_TOKEN_DICT.match(core):
        return True
    if len(core) >= 3 and core.isalpha() and core[0] in "ilmgdDkKfFsShHJYUG;":
        return True
    if core in ("g", "m", "d", "k"):
        return False
    if len(core) >= 4 and re.search(r"(mm|ll|ii|dd|gg|ff|ss|kk)", core):
        return True
    if len(core) >= 3 and re.search(r"a([mgdDkKflisSh;]|$)", core):
        return True
    if len(core) >= 5 and re.search(r"[ucCpZnxeyzAbrvoVt]{4,}", core):
        return True
    return False


def _convert_win_segment(seg: str) -> str:
    from ..wininnwa.converter import convert as win_convert

    parts = re.split(r"(\s+)", seg)
    out = []
    for part in parts:
        if not part or part.isspace():
            out.append(part)
            continue
        if _is_english_token_in_win(part):
            cleaned = re.sub(r"^\]", "“", part)
            cleaned = re.sub(r"\}$", "”", cleaned)
            out.append(cleaned)
        else:
            out.append(_win_clean_post(win_convert(part, "wininnwa", "unicode")))
    return "".join(out)


def _span_aware_convert(page) -> str:
    """Convert only spans whose font is a Myanmar legacy font; preserve English font spans as English."""
    from ..font_catalog import classify_font

    try:
        spans = page.get_texttrace()
    except Exception:
        return ""
    if not spans:
        return ""
    prev_sig = None
    lines = []
    converted_chars = 0
    for s in spans:
        sdir = s.get("dir")
        if sdir and abs(sdir[0]) < 0.5:
            continue
        fn = ((s.get("font") or "").split("+")[-1]).strip()
        chars = s.get("chars") or []
        if not chars:
            continue
        bbox = tuple(round(v, 1) for v in (s.get("bbox") or ()))
        sig = (fn, bbox, tuple((c[0], c[1]) for c in chars))
        if sig == prev_sig:
            continue
        prev_sig = sig
        kind = classify_font(fn)
        tbl = table_for_face(fn)
        is_leg = kind in (
            "win",
            "wwin",
            "academy",
            "ce",
            "myazedi",
            "legacy",
            "gandamar",
            "king",
            "msheavy",
            "kannaka",
            "mmyanmar",
        ) or bool(tbl)
        span_lines = []
        for c in chars:
            ucs = c[0]
            if not isinstance(ucs, int) or not ucs or ucs == 0xFFFD:
                continue
            origin = c[2] if len(c) > 2 else (0, 0)
            x, y = round(origin[0], 1), round(origin[1], 1)
            ch = chr(ucs)
            if span_lines and abs(span_lines[-1][0] - y) <= 4:
                span_lines[-1][2].append(ch)
            else:
                span_lines.append([y, x, [ch]])
        for y, x, ch_list in span_lines:
            seg = "".join(ch_list)
            tag = (is_leg, kind, tbl)
            if lines and abs(lines[-1][0] - y) <= 4 and lines[-1][1] and lines[-1][1][-1][2] == tag:
                prev_x, prev_seg, _ = lines[-1][1][-1]
                lines[-1][1][-1] = (prev_x, prev_seg + seg, tag)
            elif lines and abs(lines[-1][0] - y) <= 4:
                lines[-1][1].append((x, seg, tag))
            else:
                lines.append([y, [(x, seg, tag)]])
    out_lines = []
    for _y, segs in lines:
        parts = []
        for idx, (_x, seg, (is_leg, kind, tbl)) in enumerate(segs):
            if is_leg and seg.strip():
                if _looks_english(seg) and sum(ch in _MARKS for ch in seg) < 2:
                    conv_seg = seg
                elif kind == "win" or tbl == "WinInnwa":
                    conv_seg = _convert_win_segment(seg)
                    converted_chars += _myanmar_letters(conv_seg)
                else:
                    conv_seg = convert_table(seg, tbl or table_for_kind(kind) or "WwinBurmese")
                    converted_chars += _myanmar_letters(conv_seg)
            else:
                conv_seg = seg
            if parts and not parts[-1].endswith(" ") and not conv_seg.startswith(" "):
                prev_leg = segs[idx - 1][2][0]
                if not is_leg and not prev_leg and conv_seg[:1].isalnum() and parts[-1][-1:].isalnum():
                    parts.append(" ")
                elif is_leg != prev_leg and conv_seg[:1] not in "၊။)]}”’" and parts[-1][-1:] not in "([{“‘":
                    parts.append(" ")
            parts.append(conv_seg)
        out_lines.append("".join(parts))
    if converted_chars < 10:
        return ""
    return "\n".join(out_lines)

def page_faces(page):
    faces = []
    try:
        for item in page.get_fonts():
            name = ((item[3] or "").split("+")[-1]).strip()
            if name:
                faces.append(name)
    except Exception:
        return []
    return faces


def page_convert(page, text: str) -> str:
    """Convert a page of legacy ASCII or MyaZedi ONLY when the embedded font is a Myanmar legacy font."""
    if not text:
        return ""
    faces = page_faces(page)
    from ..font_catalog import classify_font

    kinds = set()
    legacy_faces = []
    for face in faces:
        kind = classify_font(face)
        if not kind:
            if table_for_face(face):
                legacy_faces.append(face)
                kinds.add("legacy")
            continue
        kinds.add(kind)
        if kind not in ("unicode", "zawgyi"):
            legacy_faces.append(face)

    ascii_n = _ascii_letters(text)
    my_n = _myanmar_letters(text)

    if "myazedi" in kinds:
        got = try_convert(text, faces=legacy_faces or ["bit"], kind="myazedi")
        if got:
            return got

    if not legacy_faces:
        return ""

    if ascii_n < 15:
        return ""

    span_conv = _span_aware_convert(page)
    if span_conv and _myanmar_letters(span_conv) >= 15:
        return span_conv

    if my_n > ascii_n * 0.25:
        return ""

    for kind in ("wwin", "academy", "ce", "myazedi", "gandamar", "king", "msheavy", "kannaka", "mmyanmar", "legacy"):
        if kind in kinds:
            got = try_convert(text, faces=legacy_faces, kind=kind)
            if got:
                return got

    if "win" in kinds:
        got = _win_syllable(text, has_win_font=True)
        if got:
            return got
        got = try_convert(text, faces=legacy_faces, kind="win")
        if got:
            return got

    return try_convert(text, faces=legacy_faces, kind="")
