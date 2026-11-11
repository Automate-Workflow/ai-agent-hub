"""Verify external URLs across CSV datasets with retries, rate limiting, and bot-gate reporting."""

from __future__ import annotations

import argparse
import collections
import concurrent.futures
import datetime as _dt
import json
import pathlib
import ssl
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import (
    REPORTS_DIR,
    configure_stdio,
    read_csv_rows,
    write_text_lf,
)

USER_AGENT = "Mozilla/5.0 (compatible; ai-agent-hub-link-checker/1.0; +https://github.com/Automate-Workflow/ai-agent-hub)"

# Hosts/prefixes verified live in browser/search that block automated HTTP clients (403/429/cookie-loop).
KNOWN_BOT_GATED = (
    "https://openai.com/",
    "https://milvus.io/docs",
    "https://docs.vllm.ai",
    "https://www.iso.org/",
    "https://genai.owasp.org/",
)

URL_SOURCES = (
    ("sources", "url"),
    ("frameworks_tools", "repo_or_docs_url"),
    ("protocols_standards", "spec_url"),
    ("resources", "url"),
)


def is_known_bot_gated(url: str) -> bool:
    """Return True if the URL matches an audited bot-protected endpoint."""
    return any(url.startswith(prefix) for prefix in KNOWN_BOT_GATED)


def collect_urls() -> dict[str, list[str]]:
    """Map each unique URL to sorted citing references 'dataset:row_id'."""
    url_refs: dict[str, list[str]] = collections.defaultdict(list)
    for ds_name, col in URL_SOURCES:
        _, rows = read_csv_rows(ds_name)
        for row in rows:
            u = row.get(col, "").strip()
            if u:
                url_refs[u].append(f"{ds_name}:{row.get('id', '')}")
    return {u: sorted(set(refs)) for u, refs in sorted(url_refs.items())}


class DomainLimiter:
    """Thread-safe per-host polite interval limiter."""

    def __init__(self, delay: float) -> None:
        self.delay = delay
        self._lock = threading.Lock()
        self._last_hit: dict[str, float] = {}

    def wait(self, url: str) -> None:
        if self.delay <= 0:
            return
        host = urllib.parse.urlparse(url).netloc.lower()
        with self._lock:
            now = time.monotonic()
            prev = self._last_hit.get(host, 0.0)
            gap = self.delay - (now - prev)
            if gap > 0:
                time.sleep(gap)
            self._last_hit[host] = time.monotonic()


def check_one_url(
    url: str,
    limiter: DomainLimiter,
    timeout: float,
    retries: int,
) -> dict[str, object]:
    """Check one URL using HEAD then GET fallback with retries."""
    ctx = ssl.create_default_context()
    last_status: int | None = None
    last_final = url
    last_err: str | None = None

    for attempt in range(retries + 1):
        if attempt > 0:
            time.sleep(0.5 * (2 ** (attempt - 1)))
        for method in ("HEAD", "GET"):
            limiter.wait(url)
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method=method)
            try:
                with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                    if method == "GET":
                        resp.read(1024)
                    last_status = int(resp.status)
                    last_final = resp.geturl()
                    last_err = None
                    if 200 <= last_status < 400:
                        redirected = last_final.rstrip("/") != url.rstrip("/")
                        state = "redirected" if redirected else "ok"
                        return {
                            "url": url,
                            "state": state,
                            "status": last_status,
                            "final_url": last_final,
                            "error": None,
                        }
            except urllib.error.HTTPError as exc:
                last_status = int(exc.code)
                last_final = url
                last_err = f"HTTP {exc.code}"
                if method == "HEAD":
                    continue
                if exc.code in (403, 429) or (exc.code == 302 and "milvus.io" in url):
                    if is_known_bot_gated(url):
                        return {
                            "url": url,
                            "state": "gated",
                            "status": last_status,
                            "final_url": last_final,
                            "error": last_err,
                        }
                if 400 <= exc.code < 500 and exc.code not in (429,):
                    break
            except Exception as exc:
                last_status = None
                last_err = str(exc)[:160]
                if method == "HEAD":
                    continue
        if is_known_bot_gated(url) and last_status in (302, 403, 429):
            return {
                "url": url,
                "state": "gated",
                "status": last_status,
                "final_url": last_final,
                "error": last_err,
            }

    state = "gated" if (is_known_bot_gated(url) and last_status in (302, 403, 429)) else "broken"
    return {
        "url": url,
        "state": state,
        "status": last_status,
        "final_url": last_final,
        "error": last_err,
    }


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(description="Check all external URLs across CSV datasets.")
    parser.add_argument("--workers", type=int, default=8, help="Concurrent worker count.")
    parser.add_argument("--timeout", type=float, default=12.0, help="Request timeout in seconds.")
    parser.add_argument("--retries", type=int, default=2, help="Retries after transient failure.")
    parser.add_argument("--delay", type=float, default=0.15, help="Per-domain minimum interval (s).")
    parser.add_argument("--max-urls", type=int, default=0, help="Optional cap for smoke tests (0=all).")
    args = parser.parse_args(argv)

    url_refs = collect_urls()
    urls = list(url_refs.keys())
    if args.max_urls > 0:
        urls = urls[: args.max_urls]

    limiter = DomainLimiter(args.delay)
    results: list[dict[str, object]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        future_map = {
            pool.submit(check_one_url, u, limiter, args.timeout, args.retries): u for u in urls
        }
        for fut in concurrent.futures.as_completed(future_map):
            res = fut.result()
            res["cited_by"] = url_refs[str(res["url"])]
            results.append(res)

    results.sort(key=lambda r: str(r["url"]))
    counts = collections.Counter(str(r["state"]) for r in results)
    generated_at = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    payload = {
        "generated_at": generated_at,
        "total_urls": len(results),
        "summary": {
            "ok": counts.get("ok", 0),
            "redirected": counts.get("redirected", 0),
            "gated": counts.get("gated", 0),
            "broken": counts.get("broken", 0),
        },
        "results": results,
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    write_text_lf(REPORTS_DIR / "link_report.json", json.dumps(payload, indent=2) + "\n")

    lines = [
        "# Link Check Report",
        "",
        f"Checked: **{len(results)}** unique URLs",
        "",
        "| Status | Count |",
        "|---|---:|",
        f"| `ok` | {counts.get('ok', 0)} |",
        f"| `redirected` | {counts.get('redirected', 0)} |",
        f"| `gated` (`known_bot_gated`) | {counts.get('gated', 0)} |",
        f"| `broken` | {counts.get('broken', 0)} |",
        "",
    ]
    broken = [r for r in results if r["state"] == "broken"]
    if broken:
        lines.extend(["## Broken Links", "", "| Status/Error | URL | Cited By |", "|---|---|---|"])
        for r in broken:
            lines.append(f"| {r['status'] or r['error']} | {r['url']} | {', '.join(r['cited_by'])} |")
        lines.append("")

    redirected = [r for r in results if r["state"] == "redirected"]
    if redirected:
        lines.extend(["## Redirects", "", "| Original URL | Final URL | Cited By |", "|---|---|---|"])
        for r in redirected:
            lines.append(f"| {r['url']} | {r['final_url']} | {', '.join(r['cited_by'])} |")
        lines.append("")

    gated = [r for r in results if r["state"] == "gated"]
    if gated:
        lines.extend(["## Known Bot-Gated URLs", "", "| Status | URL | Cited By |", "|---|---|---|"])
        for r in gated:
            lines.append(f"| {r['status']} | {r['url']} | {', '.join(r['cited_by'])} |")
        lines.append("")

    write_text_lf(REPORTS_DIR / "link_report.md", "\n".join(lines))
    print(
        f"Links checked: {len(results)} | ok={counts.get('ok',0)} redirected={counts.get('redirected',0)} gated={counts.get('gated',0)} broken={counts.get('broken',0)}"
    )
    return 1 if counts.get("broken", 0) > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
