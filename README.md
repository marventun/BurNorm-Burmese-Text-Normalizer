# myanmar-uni-convert

Convert **legacy Myanmar encodings** and **Zawgyi** text to **Myanmar Unicode**.

This library maps WinInnwa / Academy / CE / other legacy fonts and Zawgyi text into Unicode, then applies guarded normalization (Phase 1 / Phase 2 / Kinzi micro-fixes).

It does **not** open PDFs, run OCR, or ship font binaries.

---

## Install

```bash
pip install -e ".[detect]"
```

`myanmartools` (Google myanmar-tools) is optional but recommended for Zawgyi auto-detect.

---

## Quick start

```python
from myanmar_uni_convert import convert, convert_with_stats

# Named legacy font
unicode_text = convert(raw_text, font="WinInnwa")

# Zawgyi / auto
unicode_text = convert(raw_text, auto=True)

# With diagnostics
result = convert_with_stats(raw_text, font="Academy")
print(result.branch, result.kind, result.zawgyi_score)
print(result.text)
```

### CLI

```bash
myanmar-uni-convert input.txt -o out.txt --font WinInnwa
myanmar-uni-convert input.txt -o out.txt --auto --stats
python -m myanmar_uni_convert input.txt --kind zawgyi
```

---

## What it supports

| Input | How |
| --- | --- |
| WinInnwa family | Burglish OE map + WinInnwa syllable converter |
| Academy, CE, MyaZedi, Metrix, Gandamar, King, Wwin, MSHeavy, Kannaka, MMyanmar | Burglish OE tables |
| Zawgyi | Rabbit rules + quality-gated Phase 1 |
| Already Unicode | Optional residual scrub + visual-order Phase 2 |

Pipeline:

```text
text (+ optional font/kind)
   → legacy map  OR  Zawgyi/auto path
   → Phase 1 scrub / guarded Rabbit
   → Phase 2 visual-order repair
   → Kinzi micro-fix
   → light NFC cleanup
   → Unicode out
```

---

## License

**Apache License 2.0** for this project’s original code.

Third-party components (Rabbit, Burglish tables, WinInnwa converter, optional myanmar-tools) remain under their own licenses. See [`NOTICE`](NOTICE) and [`THIRD_PARTY.md`](THIRD_PARTY.md).

### Publishing notes

- Safe to publish: conversion **tables** and converter **code** (MIT / Apache sources, attributed).
- Do **not** add proprietary `.ttf` / `.otf` font files or copyrighted book corpora to this repo.
- Font names are identifiers only; this project is not affiliated with font vendors.
- Conversion is best-effort; legacy encodings are lossy and not guaranteed 100% correct.

---

## Develop

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

---

## Related

Extracted from a local Level-1 Myanmar PDF text pipeline. This package is the standalone **encoding → Unicode** piece only.
