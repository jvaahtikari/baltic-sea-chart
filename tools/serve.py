#!/usr/bin/env python3
"""Local static server with HTTP Range support (PMTiles needs it). Usage: python3 tools/serve.py [dir] [port]"""
import os
import re
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class Handler(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".mjs": "text/javascript", ".js": "text/javascript",
                      ".pbf": "application/x-protobuf", ".pmtiles": "application/octet-stream"}

    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_GET(self):
        r = self.headers.get("Range")
        path = self.translate_path(self.path.split("?")[0])
        m = re.match(r"bytes=(\d*)-(\d*)$", r or "")
        if not m or not os.path.isfile(path):
            return super().do_GET()
        size = os.path.getsize(path)
        a, b = m.groups()
        start, end = (max(0, size - int(b)), size - 1) if a == "" else (int(a), min(int(b) if b else size - 1, size - 1))
        if start > end:
            self.send_response(416)
            self.send_header("Content-Range", "bytes */%d" % size)
            self.end_headers()
            return
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, size))
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        with open(path, "rb") as f:
            f.seek(start)
            n = end - start + 1
            while n > 0:
                chunk = f.read(min(1 << 20, n))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return
                n -= len(chunk)


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "dist"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=root)).serve_forever()
