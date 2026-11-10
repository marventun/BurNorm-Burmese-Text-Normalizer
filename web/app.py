"""Local webpage for trying BurNorm.

Paste Burmese text extracted from PDFs (legacy fonts / Zawgyi / Unicode)
and convert or normalize it in the browser.

Usage (from repo root, with the package installed):

    python web/app.py
    # then open http://127.0.0.1:8765
"""
from __future__ import annotations

import json
import mimetypes
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8765

# Allow `python web/app.py` without requiring PYTHONPATH hacks when installed editable.
try:
    from burnorm import convert_with_stats, normalize_with_stats
except ImportError:
    sys.path.insert(0, str(ROOT.parent))
    from burnorm import convert_with_stats, normalize_with_stats


FONTS = [
    {"value": "", "label": "Auto (detect)"},
    {"value": "WinInnwa", "label": "WinInnwa"},
    {"value": "Academy", "label": "Academy"},
    {"value": "CE", "label": "CE / Computer Eain"},
    {"value": "MyaZedi", "label": "MyaZedi"},
    {"value": "Metrix", "label": "Metrix"},
    {"value": "Gandamar", "label": "Gandamar"},
    {"value": "King", "label": "King"},
    {"value": "WwinBurmese", "label": "Wwin Burmese"},
    {"value": "MSHEAVY", "label": "MS Heavy"},
    {"value": "Kannaka", "label": "Kannaka"},
    {"value": "MMyanmar1", "label": "MMyanmar"},
    {"value": "Zawgyi-One", "label": "Zawgyi"},
    {"value": "Pyidaungsu", "label": "Unicode (no convert)"},
]

# Curated demos: mode + font settings + input text (verified round-trips where possible).
EXAMPLES = [
    {
        "id": "auto-zawgyi",
        "group": "Convert · Auto / Zawgyi",
        "title": "Zawgyi greeting (auto)",
        "blurb": "Detect Zawgyi → Unicode မင်္ဂလာပါ",
        "mode": "convert",
        "font": "",
        "auto": True,
        "text": "မဂၤလာပါ",
        "expect": "မင်္ဂလာပါ",
    },
    {
        "id": "zawgyi-font",
        "group": "Convert · Auto / Zawgyi",
        "title": "Zawgyi with font hint",
        "blurb": "Same greeting, font=Zawgyi-One",
        "mode": "convert",
        "font": "Zawgyi-One",
        "auto": False,
        "text": "မဂၤလာပါ",
        "expect": "မင်္ဂလာပါ",
    },
    {
        "id": "zawgyi-ocr",
        "group": "Convert · Auto / Zawgyi",
        "title": "Zawgyi PDF extract glitches",
        "blurb": "Spaces + ေတကြ repaired before Rabbit",
        "mode": "convert",
        "font": "",
        "auto": True,
        "text": (
            "Artificial Neural Network အေၾကာင္းန႔ ဲ ပတ္သက္လို႔ အရင္ကလဲ "
            "ဟိုတစ္စ ဒီတစ္စ ေရးခ့ဖဲ ူးျပီးပါျပီ...\n"
            "ဒါေပမယ့္ အ့ဒဲ ါေတကြ ANN ရ႔ ဲ အတြင္းပိုင္းက "
            "အလုပ္လုပ္ပုံေတကြ ို ေျပာထားတာေတကြ မ်ားပါတယ္..."
        ),
        "expect": "အကြောင်းနဲ့ … တွေကို",
    },
    {
        "id": "wininnwa",
        "group": "Convert · Legacy fonts",
        "title": "WinInnwa",
        "blurb": "ASCII WinInnwa → မြန်မာစာ",
        "mode": "convert",
        "font": "WinInnwa",
        "auto": False,
        "text": "jrefrmpm",
        "expect": "မြန်မာစာ",
    },
    {
        "id": "academy",
        "group": "Convert · Legacy fonts",
        "title": "Academy",
        "blurb": "Academy map → မြန်မာစာ",
        "mode": "convert",
        "font": "Academy",
        "auto": False,
        "text": "r]efrmpm",
        "expect": "မြန်မာစာ",
    },
    {
        "id": "ce",
        "group": "Convert · Legacy fonts",
        "title": "CE / Computer Eain",
        "blurb": "CE map → မြန်မာစာ",
        "mode": "convert",
        "font": "CE",
        "auto": False,
        "text": "r_efrmpm",
        "expect": "မြန်မာစာ",
    },
    {
        "id": "myazedi",
        "group": "Convert · Legacy fonts",
        "title": "MyaZedi",
        "blurb": "MyaZedi → ကောင်းသောနေ့",
        "mode": "convert",
        "font": "MyaZedi",
        "auto": False,
        "text": "ကောင္းသောနေ့",
        "expect": "ကောင်းသောနေ့",
    },
    {
        "id": "metrix",
        "group": "Convert · Legacy fonts",
        "title": "Metrix",
        "blurb": "Metrix → မြန်မာစာ",
        "mode": "convert",
        "font": "Metrix",
        "auto": False,
        "text": "rjefrmpm",
        "expect": "မြန်မာစာ",
    },
    {
        "id": "gandamar",
        "group": "Convert · Legacy fonts",
        "title": "Gandamar",
        "blurb": "Gandamar → မြန်မာစာ",
        "mode": "convert",
        "font": "Gandamar",
        "auto": False,
        "text": "r]efrmpm",
        "expect": "မြန်မာစာ",
    },
    {
        "id": "king",
        "group": "Convert · Legacy fonts",
        "title": "King",
        "blurb": "King → မြန်မာစာ",
        "mode": "convert",
        "font": "King",
        "auto": False,
        "text": "r-efrmpm",
        "expect": "မြန်မာစာ",
    },
    {
        "id": "wwin",
        "group": "Convert · Legacy fonts",
        "title": "Wwin Burmese",
        "blurb": "Wwin → မြန်မာစာ",
        "mode": "convert",
        "font": "WwinBurmese",
        "auto": False,
        "text": "rMefrmpm",
        "expect": "မြန်မာစာ",
    },
    {
        "id": "msheavy",
        "group": "Convert · Legacy fonts",
        "title": "MS Heavy",
        "blurb": "MS Heavy → မြန်မာစာ",
        "mode": "convert",
        "font": "MSHEAVY",
        "auto": False,
        "text": "r-efrmpm",
        "expect": "မြန်မာစာ",
    },
    {
        "id": "kannaka",
        "group": "Convert · Legacy fonts",
        "title": "Kannaka",
        "blurb": "Kannaka → မြန်မာစာ",
        "mode": "convert",
        "font": "Kannaka",
        "auto": False,
        "text": "m®n\\masa",
        "expect": "မြန်မာစာ",
    },
    {
        "id": "mmyanmar",
        "group": "Convert · Legacy fonts",
        "title": "MMyanmar",
        "blurb": "MMyanmar → မြန်မာစာ",
        "mode": "convert",
        "font": "MMyanmar1",
        "auto": False,
        "text": "rjefrmpm",
        "expect": "မြန်မာစာ",
    },
    {
        "id": "unicode-passthrough",
        "group": "Convert · Unicode",
        "title": "Already Unicode",
        "blurb": "Clean Unicode — convert path still normalizes",
        "mode": "convert",
        "font": "Pyidaungsu",
        "auto": False,
        "text": "မင်္ဂလာပါ",
        "expect": "မင်္ဂလာပါ",
    },
    {
        "id": "norm-orphan-ya",
        "group": "Normalize only",
        "title": "Fix orphan ြ",
        "blurb": "ဟောြပော → ဟောပြော",
        "mode": "normalize",
        "font": "",
        "auto": False,
        "text": "ဟောြပော",
        "expect": "ဟောပြော",
    },
    {
        "id": "norm-kinzi-e",
        "group": "Normalize only",
        "title": "Fix kinzi + ေ",
        "blurb": "သင်္ေကတ → သင်္ကေတ",
        "mode": "normalize",
        "font": "",
        "auto": False,
        "text": "သင်္ေကတ",
        "expect": "သင်္ကေတ",
    },
    {
        "id": "norm-e-vowel",
        "group": "Normalize only",
        "title": "Fix ေ vowel shift",
        "blurb": "တွကေို → တွေကို",
        "mode": "normalize",
        "font": "",
        "auto": False,
        "text": "တွကေို",
        "expect": "တွေကို",
    },
    {
        "id": "norm-cleanup",
        "group": "Normalize only",
        "title": "Cleanup ZWSP / dup marks",
        "blurb": "Strip zero-width space + collapse ််",
        "mode": "normalize",
        "font": "",
        "auto": False,
        "text": "မင်္ဂလာပါ\u200b မာ််",
        "expect": "မင်္ဂလာပါ မာ်",
    },
    {
        "id": "norm-clean",
        "group": "Normalize only",
        "title": "Clean Unicode (no change)",
        "blurb": "Control: already-correct text stays put",
        "mode": "normalize",
        "font": "",
        "auto": False,
        "text": "မင်္ဂလာပါ",
        "expect": "မင်္ဂလာပါ",
    },
]


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, payload: dict) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send(code, data, "application/json; charset=utf-8")

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            html = (ROOT / "index.html").read_bytes()
            self._send(200, html, "text/html; charset=utf-8")
            return
        if path == "/api/meta":
            self._json(200, {"fonts": FONTS, "examples": EXAMPLES})
            return
        # Optional static files next to index.html
        rel = path.lstrip("/").replace("\\", "/")
        if ".." in rel.split("/"):
            self._json(400, {"error": "bad path"})
            return
        file_path = (ROOT / rel).resolve()
        if not str(file_path).startswith(str(ROOT)) or not file_path.is_file():
            self._json(404, {"error": "not found"})
            return
        ctype = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        self._send(200, file_path.read_bytes(), ctype)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/convert":
            self._json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid JSON"})
            return

        text = payload.get("text") or ""
        font = (payload.get("font") or "").strip() or None
        kind = (payload.get("kind") or "").strip() or None
        mode = (payload.get("mode") or "convert").strip().lower()
        auto = bool(payload.get("auto", True))
        cleanup = bool(payload.get("cleanup", True))
        try:
            zawgyi_min = float(payload.get("zawgyi_min", 0.5))
        except (TypeError, ValueError):
            zawgyi_min = 0.5

        try:
            if mode == "normalize":
                result = normalize_with_stats(text, cleanup=cleanup)
            else:
                result = convert_with_stats(
                    text,
                    font=font,
                    kind=kind,
                    auto=auto,
                    zawgyi_min=zawgyi_min,
                    cleanup=cleanup,
                )
        except Exception as exc:  # noqa: BLE001 — surface to the tester UI
            self._json(500, {"error": str(exc)})
            return

        self._json(
            200,
            {
                "text": result.text,
                "kind": result.kind,
                "branch": result.branch,
                "zawgyi_score": result.zawgyi_score,
                "stats": result.stats,
            },
        )


def main() -> int:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"BurNorm tester → http://{HOST}:{PORT}", flush=True)
    print("Press Ctrl+C to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
