#!/usr/bin/env python3
"""
Servidor HTTP de demo (stdlib): POST /api/analyze-repo → clone + ``app_sinaplint check --json``.

Uso (na raiz do Core_SinapUm)::

    python3 tools/sinaplint-demo-server/server.py

Requer: ``git`` no PATH. O repositório clonado deve conter o pacote ``app_sinaplint`` na raiz.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

# Apenas repositórios públicos GitHub (HTTPS).
_GH = re.compile(r"^https://github\.com/[\w.-]+/[\w.-]+/?$")


def _json_response(handler: BaseHTTPRequestHandler, status: int, body: dict) -> None:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()
    handler.wfile.write(data)


def _cors_preflight(handler: BaseHTTPRequestHandler) -> None:
    handler.send_response(204)
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()


def _run_check(clone_dir: Path, timeout: int = 300) -> tuple[int, str, str]:
    out = clone_dir / "_sinaplint_out.json"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "app_sinaplint",
            "check",
            "--json",
            "-o",
            str(out),
        ],
        cwd=str(clone_dir),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    if out.is_file():
        return proc.returncode, out.read_text(encoding="utf-8"), stderr + stdout
    return proc.returncode, "", stderr + stdout


class DemoHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        sys.stderr.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format % args))

    def do_OPTIONS(self) -> None:
        _cors_preflight(self)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/analyze-repo":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            _json_response(self, 400, {"ok": False, "error": "JSON inválido"})
            return

        repo = (payload.get("repo") or "").strip()
        if not repo or not _GH.match(repo.rstrip("/")):
            _json_response(
                self,
                400,
                {
                    "ok": False,
                    "error": "URL inválida. Use https://github.com/dono/repo (HTTPS).",
                },
            )
            return

        url = repo.rstrip("/") + ".git"
        tmp = tempfile.mkdtemp(prefix="sinaplint-demo-")
        try:
            cl = subprocess.run(
                ["git", "clone", "--depth", "1", url, str(Path(tmp) / "repo")],
                capture_output=True,
                text=True,
                timeout=180,
            )
            if cl.returncode != 0:
                _json_response(
                    self,
                    500,
                    {
                        "ok": False,
                        "error": "Falha ao clonar",
                        "detail": (cl.stderr or cl.stdout or "")[:2000],
                    },
                )
                return
            clone_dir = Path(tmp) / "repo"
            if not (clone_dir / "app_sinaplint").is_dir():
                _json_response(
                    self,
                    400,
                    {
                        "ok": False,
                        "error": "Este repositório não contém app_sinaplint na raiz (projeto SinapLint).",
                    },
                )
                return
            code, report_json, log = _run_check(clone_dir)
            try:
                report = json.loads(report_json) if report_json.strip() else {}
            except json.JSONDecodeError:
                report = {"parse_error": True, "raw": report_json[:4000]}
            report["_demo_exit_code"] = code
            report["_demo_log"] = log[-4000:]
            _json_response(self, 200, report)
        except subprocess.TimeoutExpired:
            _json_response(self, 504, {"ok": False, "error": "Timeout na análise ou clone."})
        except OSError as e:
            _json_response(self, 500, {"ok": False, "error": str(e)})
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


def main() -> None:
    host = os.environ.get("SINAPLINT_DEMO_HOST", "127.0.0.1")
    port = int(os.environ.get("SINAPLINT_DEMO_PORT", "8765"))
    httpd = HTTPServer((host, port), DemoHandler)
    print(f"SinapLint demo server em http://{host}:{port}", file=sys.stderr)
    print("POST /api/analyze-repo  JSON: {\"repo\":\"https://github.com/...\"}", file=sys.stderr)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
