import base64
import json
import logging
import mimetypes
import os
import re
import sys
import time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parent

LOG_PATH = ROOT / "dev_server.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("dev_server")


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args):
        try:
            logger.info("%s - %s", self.address_string(), (format % args))
        except Exception:
            pass

    def log_error(self, format: str, *args):
        try:
            logger.error("%s - %s", self.address_string(), (format % args))
        except Exception:
            pass

    def translate_path(self, path: str) -> str:
        p = urlparse(path).path
        p = unquote(p)
        p = p.lstrip("/")
        local = (ROOT / p).resolve()
        try:
            local.relative_to(ROOT)
        except Exception:
            return str(ROOT)
        return str(local)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,PATCH,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def _serve_file(self, file_path: Path, content_type: str | None = None):
        if not file_path.exists() or not file_path.is_file():
            self.send_error(404, "File not found")
            return
        data = file_path.read_bytes()
        ctype = content_type
        if not ctype:
            ctype, _ = mimetypes.guess_type(str(file_path))
        ctype = ctype or "application/octet-stream"

        # Desktop/mobile gate bypass: inject early hints before app JS executes.
        try:
            if file_path.name in {"main.html", "docs"} and ctype.startswith("text/html"):
                html = data.decode("utf-8", errors="ignore")
                anchor = "<title>fundocs</title>"
                if anchor in html and "__ua_bypass__" not in html:
                    inject = (
                        "<script>/*__ua_bypass__*/(function(){try{var ua=\"Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1\";"
                        "try{Object.defineProperty(Navigator.prototype,'userAgent',{get:function(){return ua},configurable:true})}catch(e){try{Object.defineProperty(navigator,'userAgent',{get:function(){return ua},configurable:true})}catch(e2){}}"
                        "try{Object.defineProperty(Navigator.prototype,'platform',{get:function(){return 'iPhone'},configurable:true})}catch(e){}"
                        "try{Object.defineProperty(navigator,'maxTouchPoints',{get:function(){return 5},configurable:true})}catch(e){}"
                        "try{window.ontouchstart=function(){};document.documentElement.classList.add('touch','mobile')}catch(e){}"
                        "try{var mm=window.matchMedia;window.matchMedia=function(q){if(typeof q==='string'){var s=q.toLowerCase();if(s.indexOf('display-mode')>=0)return{matches:true,media:q,addListener:function(){},removeListener:function(){},addEventListener:function(){},removeEventListener:function(){}};if(s.indexOf('pointer')>=0||s.indexOf('hover')>=0)return{matches:true,media:q,addListener:function(){},removeListener:function(){},addEventListener:function(){},removeEventListener:function(){}};}return mm?mm.call(window,q):{matches:false,media:q,addListener:function(){},removeListener:function(){},addEventListener:function(){},removeEventListener:function(){}}};}catch(e){}"
                        "try{window.navigator.standalone=true}catch(e){}" 
                        "try{var rw=function(u){try{u=String(u||'')}catch(e){return u};u=u.replace(/^https?:\\/\\/(?:www\\.)?fundocs\\.net\\//i,'/');return u};"
                        "var of=window.fetch; if(of){window.fetch=function(input,init){try{if(typeof input==='string'){input=rw(input)}else if(input&&input.url){input=new Request(rw(input.url),input)};}catch(e){} return of.call(this,input,init)};}"
                        "var xo=XMLHttpRequest&&XMLHttpRequest.prototype&&XMLHttpRequest.prototype.open; if(xo){XMLHttpRequest.prototype.open=function(m,u){try{u=rw(u)}catch(e){} return xo.apply(this,arguments)};}"
                        "}catch(e){}"
                        "}catch(e){}})();</script>"
                        "<style>.fullData.wm[data-v-19350485]{background-image:none!important}.document .wm[data-v-cb1444e4]{background-image:none!important}</style>"
                    )
                    html = html.replace(anchor, anchor + inject, 1)
                    data = html.encode("utf-8")
                    ctype = "text/html; charset=utf-8"
        except Exception:
            pass

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _serve_bytes(self, data: bytes, content_type: str):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _png_1x1(self) -> bytes:
        return base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO2c2uQAAAAASUVORK5CYII="
        )

    def do_GET(self):
        path = urlparse(self.path).path
        try:
            logger.info("GET %s", self.path)
        except Exception:
            pass

        if path.lower().endswith(("/undefined.jpg", "/undefined.jpeg", "/undefined.png", "/undefined.webp")):
            return self._serve_bytes(self._png_1x1(), "image/png")

        if path in {"/hub_news.json", "/hub_news"}:
            items = []
            d = ROOT / "api" / "news"
            if d.exists() and d.is_dir():
                for p in sorted(d.iterdir(), key=lambda x: x.name):
                    if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                        url = f"/api/news/{p.name}"
                        items.append(
                            {
                                "id": p.stem,
                                "title": p.stem,
                                "image": url,
                                "img": url,
                                "photo": url,
                            }
                        )
            if not items:
                items = [
                    {
                        "id": "local-news-1",
                        "title": "Новина",
                        "image": "/api/news/local-news.png",
                        "img": "/api/news/local-news.png",
                        "photo": "/api/news/local-news.png",
                    }
                ]
            return self._json(200, {"ok": True, "items": items, "news": items})

        if path in {"/check_uuid.php", "/check_uuid", "/check_uuidid.php", "/check_uuidid"}:
            sig = self._pick_api_file("signature")
            ava = self._pick_api_file("avatars")
            avatar_url = f"/api/avatars/{ava.name}" if (ava and ava.exists()) else "/api/avatars/local-avatar.png"
            sign_url = f"/api/signature/{sig.name}" if (sig and sig.exists()) else "/api/signature/local-signature.png"
            payload = {
                "ok": True,
                "authorized": True,
                "uuid": "local-dev-uuid",
                "cord": "50.4501,30.5234",
                "name": "Ісматов Андрій Валерович",
                "fullName": "Ісматов Андрій Валерович",
                "documents": [
                    {
                        "type": "documents-passport",
                        "sortable": True,
                        "name": "Ісматов Андрій Валерович",
                        "birthday": "1990-01-01",
                        "photo": avatar_url,
                        "sign": sign_url,
                        "number": "AA000000",
                        "color": "#e6f2ff",
                    }
                ],
            }
            if sig and sig.exists():
                payload["signatureUrl"] = f"/api/signature/{sig.name}"
            if ava and ava.exists():
                payload["avatarUrl"] = f"/api/avatars/{ava.name}"
            return self._json(200, payload)

        if path.startswith("/api/"):
            try:
                return self._handle_api_get(path)
            except Exception:
                try:
                    logger.exception("GET api handler failed: %s", self.path)
                except Exception:
                    pass
                raise

        if path in {"/", ""}:
            return self._serve_file(ROOT / "main.html", "text/html; charset=utf-8")

        if path == "/app/docs":
            return self._serve_file(ROOT / "app" / "docs", "text/html; charset=utf-8")

        try:
            return super().do_GET()
        except Exception:
            try:
                logger.exception("GET failed: %s", self.path)
            except Exception:
                pass
            raise

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            logger.info("POST %s", self.path)
        except Exception:
            pass
        if path in {"/check_auth_code.php", "/check_auth_code"}:
            return self._handle_api_post("/api/check_auth_code.php")
        if path.startswith("/api/"):
            try:
                return self._handle_api_post(path)
            except Exception:
                try:
                    logger.exception("POST api handler failed: %s", self.path)
                except Exception:
                    pass
                raise
        try:
            return super().do_POST()
        except Exception:
            try:
                logger.exception("POST failed: %s", self.path)
            except Exception:
                pass
            raise

    def _json(self, status: int, payload: dict):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _pick_api_file(self, subdir: str, default_name: str | None = None) -> Path | None:
        d = ROOT / "api" / subdir
        if not d.exists() or not d.is_dir():
            return (d / default_name) if default_name else None
        for p in sorted(d.iterdir(), key=lambda x: x.name):
            if p.is_file():
                return p
        return (d / default_name) if default_name else None

    def _serve_api_file(self, subdir: str, name: str):
        p = (ROOT / "api" / subdir / name)
        if not p.exists() or not p.is_file():
            if subdir in {"avatars", "signature", "news"}:
                return self._serve_bytes(self._png_1x1(), "image/png")
            self.send_error(404, "File not found")
            return
        return self._serve_file(p)

    def _handle_api_get(self, path: str):
        import re
        m = re.match(r"^/api/(?:avatars|avata)/(.+)$", path)
        if m:
            return self._serve_api_file("avatars", m.group(1))
        m = re.match(r"^/api/(?:signature|signa)/(.+)$", path)
        if m:
            return self._serve_api_file("signature", m.group(1))
        if path.startswith("/api/news/"):
            return self._serve_api_file("news", path[len("/api/news/"):])

        if path.startswith("/api/check_uuid.php"):
            sig = self._pick_api_file("signature")
            ava = self._pick_api_file("avatars")
            payload = {
                "code": "ok",
                "version": "local-dev",
                "doc_number": "011408193",
                "rnocpp_number": "3933519353",
                "fio": "Ісматов Андрій Валерович",
                "translit": "Ismatov Andrii Valerovych",
                "get_organ": "8193",
                "sex": "Ч",
                "edocument": 1,
                "login_code": "0",
                "qr_enable": 0,
                "qr_disable_text": "LOCAL DEV",
                "offline_mode": 0,
                "cords": "м. КИЇВ\nM. KYIV",
                "birth_street": 0,
                "birth_street_date": 0,
                "passport_start": "07.10.2025",
                "passport_end": "07.10.2035",
                "number_unzr": "11092007-39180",
                "img": (ava.stem if (ava and ava.exists()) else "local-avatar"),
                "signature": (sig.stem if (sig and sig.exists()) else "local-signature"),
                "date": "11.09.2007",
                "watermark": 1,
                "renew": time.strftime("%d.%m.%Y %H:%M"),
                "barcode": int(time.time() * 1000),
                "is_ban": 0,
                "ban_reason": "",
                "international": 0,
                "international_start": "23.09.2023",
                "international_end": "23.09.2033",
                "international_number": "GP093166",
            }
            if sig and sig.exists():
                payload["signatureUrl"] = f"/api/signature/{sig.name}"
            if ava and ava.exists():
                payload["avatarUrl"] = f"/api/avatars/{ava.name}"
            return self._json(200, payload)

        if path in {"/api/check_auth_code.php", "/api/check_auth_code"}:
            sig = self._pick_api_file("signature")
            ava = self._pick_api_file("avatars")
            avatar_url = f"/api/avatars/{ava.name}" if (ava and ava.exists()) else "/api/avatars/local-avatar.png"
            sign_url = f"/api/signature/{sig.name}" if (sig and sig.exists()) else "/api/signature/local-signature.png"
            payload = {
                "ok": True,
                "authorized": True,
                "uuid": "local-dev-uuid",
                "cord": "50.4501,30.5234",
                "name": "Ісматов Андрій Валерович",
                "fullName": "Ісматов Андрій Валерович",
                "documents": [
                    {
                        "type": "documents-passport",
                        "sortable": True,
                        "name": "Ісматов Андрій Валерович",
                        "birthday": "1990-01-01",
                        "photo": avatar_url,
                        "sign": sign_url,
                        "number": "AA000000",
                        "color": "#e6f2ff",
                    }
                ],
            }
            if sig and sig.exists():
                payload["signatureUrl"] = f"/api/signature/{sig.name}"
            if ava and ava.exists():
                payload["avatarUrl"] = f"/api/avatars/{ava.name}"
            return self._json(200, payload)

        if path.startswith("/api/check"):
            sig = self._pick_api_file("signature")
            ava = self._pick_api_file("avatars")
            payload = {
                "ok": True,
                "authorized": True,
                "uuid": "local-dev-uuid",
                "cord": "50.4501,30.5234",
                "name": "Ісматов Андрій Валерович",
                "fullName": "Ісматов Андрій Валерович",
            }
            if sig and sig.exists():
                payload["signatureUrl"] = f"/api/signature/{sig.name}"
            if ava and ava.exists():
                payload["avatarUrl"] = f"/api/avatars/{ava.name}"
            return self._json(200, payload)

        if path.startswith("/api/set_c"):
            return self._json(200, {"ok": True, "cord": "50.4501,30.5234"})

        if path.startswith("/api/hub_n"):
            news = []
            d = ROOT / "api" / "news"
            if d.exists() and d.is_dir():
                for idx, p in enumerate(sorted(d.iterdir(), key=lambda x: x.name)):
                    if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                        url = f"/api/news/{p.name}"
                        news.append(
                            {
                                "id": idx,
                                "title": p.stem,
                                "text": [""],
                                "img": url,
                                "date": "",
                            }
                        )
            if not news:
                news = [
                    {
                        "id": 0,
                        "title": "Новина",
                        "text": [""],
                        "img": "/api/news/local-news.png",
                        "date": "",
                    }
                ]
            data = json.dumps(news, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
            return

        if path.startswith("/api/qr_co"):
            return self._json(200, {"ok": True, "qr": "local-qr"})

        return self._json(200, {"ok": True, "path": path, "ts": int(time.time())})

    def _handle_api_post(self, path: str):
        length = int(self.headers.get("Content-Length") or "0")
        raw = self.rfile.read(length) if length > 0 else b""

        if path in {"/api/check_auth_code.php", "/api/check_auth_code"}:
            # Login by auth code (e.g. "Admin"). We accept anything.
            sig = self._pick_api_file("signature")
            ava = self._pick_api_file("avatars")
            payload = {
                "ok": True,
                "authorized": True,
                "uuid": "local-dev-uuid",
                "cord": "50.4501,30.5234",
            }
            if sig and sig.exists():
                payload["signatureUrl"] = f"/api/signature/{sig.name}"
            if ava and ava.exists():
                payload["avatarUrl"] = f"/api/avatars/{ava.name}"
            return self._json(200, payload)

        if path.startswith("/api/uploa"):
            sig_dir = ROOT / "api" / "signature"
            sig_dir.mkdir(parents=True, exist_ok=True)
            name = f"local_{int(time.time())}.png"
            out = sig_dir / name

            data = raw
            try:
                body = raw.decode("utf-8", errors="ignore")
                m = None
                if "base64," in body:
                    m = body.split("base64,", 1)[1]
                if m:
                    data = base64.b64decode(m)
            except Exception:
                data = raw

            try:
                out.write_bytes(data)
            except Exception:
                pass

            return self._json(200, {"ok": True, "signatureUrl": f"/api/signature/{name}"})

        return self._json(200, {"ok": True, "path": path, "len": len(raw)})


def main():
    port = 8000
    try:
        if len(sys.argv) > 1:
            port = int(sys.argv[1])
        elif os.environ.get("PORT"):
            port = int(os.environ["PORT"])
    except Exception:
        port = 8000

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Serving on http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
