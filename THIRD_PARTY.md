# Third-party components

This package redistributes or depends on the following open-source works used
to convert Burmese text extracted from PDFs and other sources (legacy fonts,
Zawgyi, Unicode). Keep these notices when you redistribute.

## Rabbit-Python (MIT)

- Upstream: https://github.com/Rabbit-Converter/Rabbit-Python
- Role: Zawgyi ↔ Unicode conversion rules
- Local path: `burnorm/zawgyi_rabbit.py`

```
MIT License (see upstream repository)
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

## Burglish (MIT)

- Upstream: https://github.com/scriptive/burglish
- Role: OE slot tables for legacy Myanmar fonts (WinInnwa, Academy, CE, …)
- Local path: `burnorm/legacy_maps/burg_fonts.json`

## WinInnwa converter (MIT)

- Copyright (c) 2018 Thura Hlaing
- Role: syllable-aware WinInnwa ↔ Unicode conversion
- Local path: `burnorm/wininnwa/`
- Full MIT license text is retained in the source file headers.

## Google myanmar-tools / myanmartools (Apache-2.0)

- Upstream: https://github.com/google/myanmar-tools
- PyPI: https://pypi.org/project/myanmartools/
- Role: optional Zawgyi detector (`ZawgyiDetector`)
- Not vendored; install via `pip install myanmartools`

---

## What this repo does **not** ship

- Proprietary Myanmar font binaries (`.ttf` / `.otf`)
- Copyrighted book PDFs or training corpora
- PDF extract tooling (bring your own extractor; this repo only converts the text)
