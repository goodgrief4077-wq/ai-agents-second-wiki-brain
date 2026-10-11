#!/usr/bin/env python3
"""fetch_record.py: helper that fetches ONE public URL and prints raw-record fields.

stdlib only, Python 3.8+. Run: python3 -I scripts/fetch_record.py <url> [--save]
Prints metadata fields only (never page text or <title>). The fetched body is saved to a
temp file OUTSIDE the repo; its path is printed as a '# body_file:' comment line.
Exit codes: 0 record printed, 1 refused (no fields printed), 2 usage/internal error.

Safety: http/https only; every resolved address must be globally routable (loopback,
private, link-local, CGNAT 100.64.0.0/10, multicast, 0.0.0.0, IPv4-mapped IPv6 refused);
the connection is pinned to the checked address and re-checked on every redirect hop;
HTTP(S)_PROXY is IGNORED (http.client does not read it; never switch to urllib's opener).
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import http.client
import io
import ipaddress
import json
import os
import socket
import ssl
import sys
import tempfile
import threading
import time
from collections import namedtuple
from urllib.parse import quote, urljoin, urlsplit, urlunsplit

MAX_BYTES = 5 * 1024 * 1024
DEADLINE_S = 30
MAX_HOPS = 5
UA = "ai-agents-second-wiki-brain-fetch-record/1 (+https://github.com/goodgrief4077-wq)"
CGNAT = ipaddress.ip_network("100.64.0.0/10")
NAT64 = ipaddress.ip_network("64:ff9b::/96")
FetchResult = namedtuple("FetchResult", "final_url status ctype body source_kind")


class Refused(Exception):
    pass


def _host_allowed(host, allow_private):
    if isinstance(allow_private, bool):
        return allow_private
    return host in allow_private  # test-only container of hostnames


def resolve_public(host, port, resolver=socket.getaddrinfo, allow_private=False):
    """Resolve all A/AAAA; refuse if ANY address is not global. Returns addresses to pin."""
    try:
        infos = resolver(host, port, 0, socket.SOCK_STREAM)
    except OSError as e:
        raise Refused("resolve failed: %s" % e)
    addrs = []
    for info in infos:
        addr = info[4][0].split("%")[0]
        ip = ipaddress.ip_address(addr)
        if ip.version == 6 and ip.ipv4_mapped is not None:
            ip = ip.ipv4_mapped
        if not _host_allowed(host, allow_private):
            if ip in CGNAT or (ip.version == 6 and ip in NAT64) or not ip.is_global:
                raise Refused("address not allowed for %s: %s" % (host, ip))
        addrs.append(addr)
    if not addrs:
        raise Refused("no addresses for " + host)
    return addrs


class _PinnedHTTP(http.client.HTTPConnection):
    def __init__(self, host, port, ip, timeout):
        super().__init__(host, port, timeout=timeout)
        self._ip = ip

    def connect(self):
        self.sock = socket.create_connection((self._ip, self.port), self.timeout)


class _PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self, host, port, ip, timeout):
        super().__init__(host, port, timeout=timeout, context=ssl.create_default_context())
        self._ip = ip

    def connect(self):
        sock = socket.create_connection((self._ip, self.port), self.timeout)
        self.sock = self._context.wrap_socket(sock, server_hostname=self.host)


def _get(url, resolver, allow_private, deadline_s, max_bytes):
    """GET with manual redirects. Returns (final_url, status, headers(lowercase), body)."""
    end = time.monotonic() + deadline_s
    for _ in range(MAX_HOPS + 1):
        u = urlsplit(url)
        if u.scheme not in ("http", "https") or not u.hostname:
            raise Refused("only http/https URLs are allowed")
        https = u.scheme == "https"
        port = u.port or (443 if https else 80)
        ips = resolve_public(u.hostname, port, resolver, allow_private)
        cls = _PinnedHTTPS if https else _PinnedHTTP
        rem = end - time.monotonic()
        if rem <= 0:
            raise Refused("deadline exceeded")
        conn = cls(u.hostname, port, ips[0], min(rem, 5))

        def _kill(c=conn):  # hard stop at the total deadline, even for a trickling server
            try:
                if c.sock is not None:
                    c.sock.shutdown(socket.SHUT_RDWR)
                    c.sock.close()
            except OSError:
                pass

        timer = threading.Timer(rem, _kill)
        timer.daemon = True
        timer.start()
        try:
            path = urlunsplit(("", "", u.path or "/", u.query, ""))
            conn.request("GET", path, headers={"Accept-Encoding": "identity", "User-Agent": UA,
                                               "Connection": "close"})
            resp = conn.getresponse()
            headers = {k.lower(): v for k, v in resp.getheaders()}
            if resp.status in (301, 302, 303, 307, 308):
                loc = headers.get("location")
                if not loc:
                    raise Refused("redirect without Location")
                url = urljoin(url, loc)
                continue
            if headers.get("content-encoding", "identity").lower() != "identity":
                raise Refused("Content-Encoding other than identity")
            cl = headers.get("content-length")
            if cl and cl.isdigit() and int(cl) > max_bytes:
                raise Refused("body larger than cap")
            chunks, total = [], 0
            while True:
                rem = end - time.monotonic()
                if rem <= 0:
                    raise Refused("deadline exceeded")
                if conn.sock is not None:
                    conn.sock.settimeout(min(rem, 5))
                chunk = resp.read1(8192)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise Refused("body larger than cap")
                chunks.append(chunk)
            return url, resp.status, headers, b"".join(chunks)
        except (socket.timeout, TimeoutError):
            raise Refused("timeout")
        except (http.client.HTTPException, ConnectionError, ssl.SSLError, OSError) as e:
            if isinstance(e, Refused):
                raise
            raise Refused("connection error: %s" % type(e).__name__)
        finally:
            timer.cancel()
            conn.close()
    raise Refused("too many redirects")


def fetch_page(url, resolver=socket.getaddrinfo, allow_private=False, deadline_s=DEADLINE_S,
               max_bytes=MAX_BYTES):
    """Fetch the PAGE. Any non-2xx, timeout, 429, 5xx or unsupported type is REFUSED."""
    final, status, headers, body = _get(url, resolver, allow_private, deadline_s, max_bytes)
    if not 200 <= status < 300:
        raise Refused("status %d" % status)
    ctype = headers.get("content-type", "").split(";")[0].strip().lower()
    if ctype == "application/pdf":
        kind = "pdf"
    elif ctype in ("text/html", "application/xhtml+xml") or ctype.startswith("text/"):
        kind = "web"
    else:
        raise Refused("unsupported content-type: %r" % ctype)
    return FetchResult(final, status, ctype, body, kind)


def _default_opener(resolver=socket.getaddrinfo):
    def opener(url):
        final, status, _h, body = _get(url, resolver, False, 30, 1024 * 1024)
        return status, body, final
    return opener


def _iso_from_wayback(ts):
    if len(ts) < 14 or not ts[:14].isdigit():
        return None
    return "%s-%s-%sT%s:%s:%s+00:00" % (ts[0:4], ts[4:6], ts[6:8], ts[8:10], ts[10:12], ts[12:14])


def wayback_lookup(url, opener=None):
    """Read-only availability lookup. Returns (archive_status, archive_url, timestamp).

    429/5xx/timeout/any failure => ('failed', None, None). No snapshot => ('none', ...).
    """
    opener = opener or _default_opener()
    try:
        status, body, _f = opener("https://archive.org/wayback/available?url=" + quote(url, safe=""))
        if status != 200:
            return "failed", None, None
        snap = json.loads(body.decode("utf-8")).get("archived_snapshots", {}).get("closest")
    except (Refused, OSError, ValueError, TimeoutError, AttributeError):
        return "failed", None, None
    if snap and snap.get("available") and snap.get("url"):
        ts = _iso_from_wayback(str(snap.get("timestamp", "")))
        if ts:
            return "saved", snap["url"], ts
    return "none", None, None


def wayback_save(url, opener=None):
    """Opt-in (--save): ask Wayback to save, then look up. Best effort; failures => lookup."""
    opener = opener or _default_opener()
    try:
        opener("https://web.archive.org/save/" + url)
    except (Refused, OSError, ValueError, TimeoutError):
        return "failed", None, None
    return wayback_lookup(url, opener)


def record_fields(url, res, wb, retrieved):
    out = [("source_kind", res.source_kind), ("url", url)]
    if res.final_url != url:
        out.append(("final_url", res.final_url))
    out.append(("retrieved", retrieved))
    status, aurl, ats = wb
    out.append(("archive_status", status))
    if status == "saved":
        out.append(("archive_url", aurl))
        out.append(("archive_timestamp", ats))
    out.append(("body_sha256", hashlib.sha256(res.body).hexdigest()))
    if res.source_kind == "web":
        out.append(("read_via", "raw"))
    return out


def main(argv=None, resolver=socket.getaddrinfo, opener=None, allow_private=False,
         deadline_s=DEADLINE_S, max_bytes=MAX_BYTES):
    """resolver/opener/allow_private/deadline_s/max_bytes are internal test parameters,
    never CLI flags or environment variables."""
    ap = argparse.ArgumentParser(description="fetch one URL and print raw-record fields")
    ap.add_argument("url")
    ap.add_argument("--save", action="store_true", help="ask Wayback to save (opt-in)")
    args = ap.parse_args(argv)  # exits 2 on usage error
    try:
        res = fetch_page(args.url, resolver, allow_private, deadline_s, max_bytes)
    except Refused as e:
        print("fetch_record: refused: %s" % e, file=sys.stderr)
        return 1
    op = opener or _default_opener(resolver)
    wb = wayback_save(args.url, op) if args.save else wayback_lookup(args.url, op)
    retrieved = __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds")
    tmp = tempfile.mkdtemp(prefix="fetch-record-")
    body_path = os.path.join(tmp, "body.pdf" if res.source_kind == "pdf" else "body.html")
    with open(body_path, "wb") as f:
        f.write(res.body)
    for k, v in record_fields(args.url, res, wb, retrieved):
        print("%s: %s" % (k, v))
    print("# body_file: " + body_path)
    return 0


# ---- selftest (no network: 127.0.0.1 server + injected resolver/opener) ----

def _selftest():
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    BODY = b"<html><body>hello</body></html>"

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, code, ctype="text/html", body=b"", extra=()):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            for k, v in extra:
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            p = self.path
            if p == "/ok":
                self._send(200, body=BODY)
            elif p == "/pdf":
                self._send(200, "application/pdf", b"%PDF-1.4 fake")
            elif p == "/redir":
                self._send(302, extra=[("Location", "/ok")])
            elif p == "/loop":
                self._send(302, extra=[("Location", "/loop")])
            elif p == "/to-private":
                self._send(302, extra=[("Location", "http://private.test/ok")])
            elif p in ("/404", "/429", "/500"):
                self._send(int(p[1:]), body=b"error page")
            elif p == "/slow":
                time.sleep(2)
                self._send(200, body=BODY)
            elif p == "/trickle":
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", "100000")
                self.end_headers()
                try:
                    for _ in range(60):
                        self.wfile.write(b"x")
                        self.wfile.flush()
                        time.sleep(0.2)
                except OSError:
                    pass
            elif p == "/big":
                self._send(200, body=b"x" * 5000)
            elif p == "/gzip":
                self._send(200, body=b"\x1f\x8b", extra=[("Content-Encoding", "gzip")])
            elif p == "/json":
                self._send(200, "application/json", b"{}")
            else:
                self._send(404)

    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    srv.daemon_threads = True
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    def res_to(ip):
        return lambda host, p, *a: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, p))]

    def res_multi(*ips):
        return lambda host, p, *a: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (i, p)) for i in ips]

    def res_mapped(ip6):
        return lambda host, p, *a: [(socket.AF_INET6, socket.SOCK_STREAM, 6, "", (ip6, p, 0, 0))]

    def local(host, p, *a):  # every name resolves to the local test server
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", p))]

    def fake_opener(status=200, body=b"", exc=None):
        def op(url):
            if exc:
                raise exc
            return status, body, url
        return op

    snap = json.dumps({"archived_snapshots": {"closest": {
        "available": True, "url": "https://web.archive.org/web/20260101000000/https://x.test/",
        "timestamp": "20260101000000", "status": "200"}}}).encode()
    nosnap = json.dumps({"archived_snapshots": {}}).encode()
    base = "http://ok.test:%d" % port
    NONE_OP = fake_opener(200, nosnap)
    allow = frozenset({"ok.test"})
    results = []

    def run(name, argv, want_rc, expect_in=(), expect_out_empty=False, **kw):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            try:
                rc = main(argv, **kw)
            except SystemExit as e:
                rc = e.code
        out = buf.getvalue()
        ok = rc == want_rc and all(s in out for s in expect_in)
        if expect_out_empty:
            ok = ok and out == ""
        results.append(ok)
        print("%s %s (rc %s)" % ("PASS" if ok else "FAIL", name, rc))
        return out

    sha = hashlib.sha256(BODY).hexdigest()
    out = run("ok page prints record", [base + "/ok"], 0,
              ["source_kind: web", "body_sha256: " + sha, "archive_status: none", "read_via: raw", "# body_file: "],
              resolver=local, opener=NONE_OP, allow_private=allow)
    run("pdf has no read_via", [base + "/pdf"], 0, ["source_kind: pdf"], resolver=local, opener=NONE_OP, allow_private=allow)
    if "read_via" in run("pdf no read_via check", [base + "/pdf"], 0, resolver=local, opener=NONE_OP, allow_private=allow):
        results.append(False)
        print("FAIL pdf printed read_via")
    run("redirect prints final_url", [base + "/redir"], 0, ["final_url: " + base + "/ok"], resolver=local,
        opener=NONE_OP, allow_private=allow)
    for code in ("404", "429", "500"):
        run("page %s refused, no fields" % code, [base + "/" + code], 1, expect_out_empty=True, resolver=local,
            opener=NONE_OP, allow_private=allow)
    run("page timeout refused", [base + "/slow"], 1, expect_out_empty=True, resolver=local, opener=NONE_OP,
        allow_private=allow, deadline_s=0.5)
    t0 = time.monotonic()
    run("trickle refused at total deadline", [base + "/trickle"], 1, expect_out_empty=True, resolver=local,
        opener=NONE_OP, allow_private=allow, deadline_s=1.0)
    took = time.monotonic() - t0
    results.append(took < 2.0)
    print("%s trickle returned within deadline+1s (%.2fs)" % ("PASS" if took < 2.0 else "FAIL", took))
    run("oversized refused", [base + "/big"], 1, expect_out_empty=True, resolver=local, opener=NONE_OP,
        allow_private=allow, max_bytes=1000)
    run("gzip refused", [base + "/gzip"], 1, expect_out_empty=True, resolver=local, opener=NONE_OP, allow_private=allow)
    run("json content-type refused", [base + "/json"], 1, expect_out_empty=True, resolver=local, opener=NONE_OP,
        allow_private=allow)
    run("redirect loop refused", [base + "/loop"], 1, expect_out_empty=True, resolver=local, opener=NONE_OP,
        allow_private=allow)
    run("redirect to private refused", [base + "/to-private"], 1, expect_out_empty=True, resolver=local,
        opener=NONE_OP, allow_private=allow)
    run("file:// refused", ["file:///etc/passwd"], 1, expect_out_empty=True, opener=NONE_OP)
    run("ftp:// refused", ["ftp://example.org/x"], 1, expect_out_empty=True, opener=NONE_OP)
    for label, r in (("loopback", res_to("127.0.0.1")), ("private 10/8", res_to("10.0.0.5")),
                     ("private 192.168", res_to("192.168.1.9")), ("link-local", res_to("169.254.169.254")),
                     ("CGNAT/Tailscale", res_to("100.64.0.5")), ("unspecified", res_to("0.0.0.0")),
                     ("multicast", res_to("224.0.0.1")), ("ipv4-mapped private", res_mapped("::ffff:10.0.0.5")),
                     ("ipv6 loopback", res_mapped("::1")),
                     ("NAT64", res_mapped("64:ff9b::a00:5")),
                     ("multi-A one private", res_multi("93.184.216.34", "10.0.0.5"))):
        run("refuse " + label, ["http://example.org/x"], 1, expect_out_empty=True, resolver=r, opener=NONE_OP)
    # Wayback only: failures degrade, page fields still printed, exit 0
    run("wayback 429 => failed", [base + "/ok"], 0, ["archive_status: failed", "body_sha256: "], resolver=local,
        opener=fake_opener(429), allow_private=allow)
    run("wayback 500 => failed", [base + "/ok"], 0, ["archive_status: failed"], resolver=local,
        opener=fake_opener(500), allow_private=allow)
    run("wayback timeout => failed", [base + "/ok"], 0, ["archive_status: failed"], resolver=local,
        opener=fake_opener(exc=TimeoutError()), allow_private=allow)
    run("wayback garbage => failed", [base + "/ok"], 0, ["archive_status: failed"], resolver=local,
        opener=fake_opener(200, b"not json"), allow_private=allow)
    run("wayback snapshot => saved", [base + "/ok"], 0,
        ["archive_status: saved", "archive_url: https://web.archive.org/web/2026", "archive_timestamp: 2026-01-01T00:00:00+00:00"],
        resolver=local, opener=fake_opener(200, snap), allow_private=allow)
    run("usage error => 2", [], 2)
    srv.shutdown()
    print("selftest: %d/%d passed" % (sum(results), len(results)))
    return 0 if all(results) and results else 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        sys.exit(_selftest())
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # internal error: exit 2, no fields
        print("fetch_record: internal error: %r" % (e,), file=sys.stderr)
        sys.exit(2)
