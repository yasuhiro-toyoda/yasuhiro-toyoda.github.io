#!/usr/bin/env python3
"""Browser regression checks against a locally built Jekyll site (Issue #32)."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from functools import partial
from hashlib import sha256
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from threading import Thread
from urllib.parse import quote, unquote, urlsplit

from playwright.sync_api import Page, sync_playwright

WIDTHS = (320, 375, 390, 430, 768, 1039, 1040, 1041, 1440)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


@contextmanager
def serve(site: Path):
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(site)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def require(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def visit(page: Page, url: str):
    response = page.goto(url, wait_until="load")
    require(response is not None and response.ok, f"Page failed: {url}")
    # Load local lazy images before measuring positions. Never call production analytics.
    page.locator("img").evaluate_all("imgs => imgs.forEach(img => img.loading = 'eager')")
    page.wait_for_function("""() => Array.from(document.images).filter(img =>
        new URL(img.currentSrc || img.src).origin === location.origin
    ).every(img => img.complete)""")
    page.evaluate("() => document.fonts.ready")
    broken = page.locator("img").evaluate_all("""imgs => imgs.filter(img =>
        new URL(img.currentSrc || img.src).origin === location.origin && !img.naturalWidth
    ).map(img => img.getAttribute('src'))""")
    require(not broken, f"Broken local images: {broken}")


def geometry(page: Page) -> dict:
    return page.evaluate("""() => {
      const rect = selector => {
        const e = document.querySelector(selector);
        if (!e) throw new Error('Missing ' + selector);
        const r = e.getBoundingClientRect();
        return {left:r.left, right:r.right, top:r.top, bottom:r.bottom, width:r.width};
      };
      const g = document.querySelector('.blog-post__grid');
      return {
        viewport: document.documentElement.clientWidth,
        scrollWidth: document.documentElement.scrollWidth,
        columns: getComputedStyle(g).gridTemplateColumns,
        areas: getComputedStyle(g).gridTemplateAreas,
        header: rect('.blog-post__header'), body: rect('.blog-post__body'),
        footer: rect('.blog-post__footer'),
        overflow: [document.documentElement, document.body].map(e => getComputedStyle(e).overflowX)
      };
    }""")


def check_geometry(data: dict):
    expected = min(data["viewport"] - 40, 760)
    left = (data["viewport"] - expected) / 2
    require(len(data["columns"].split()) == 1, f"Implicit columns: {data}")
    require(data["areas"] == '"header" "body" "footer"', f"Grid areas: {data}")
    for name in ("header", "body", "footer"):
        rect = data[name]
        require(abs(rect["width"] - expected) <= 1, f"{name} width != {expected}: {data}")
        require(abs(rect["left"] - left) <= 1, f"{name} left != {left}: {data}")
        require(abs(rect["right"] - (left + expected)) <= 1, f"{name} right: {data}")
    require(data["body"]["top"] >= data["header"]["bottom"] - 1, f"Header overlaps body: {data}")
    require(data["footer"]["top"] >= data["body"]["bottom"] - 1, f"Footer before body: {data}")
    require(data["scrollWidth"] <= data["viewport"] + 1, f"Page overflows: {data}")
    require(not any(v in ("hidden", "clip") for v in data["overflow"]), "Page overflow is masked")


def check_content_bounds(page: Page):
    outside = page.locator(".post-body").evaluate("""body => {
      const bounds = body.getBoundingClientRect();
      return Array.from(body.querySelectorAll('img, table, p, .post-toc')).filter(e => {
        const r = e.getBoundingClientRect();
        return r.width && (r.left < bounds.left - 1 || r.right > bounds.right + 1);
      }).map(e => e.tagName);
    }""")
    require(not outside, f"Content outside article: {outside}")


def check_links(page: Page, site: Path):
    links = page.locator(".site-nav a, .brand, .blog-post__footer a").evaluate_all("els => els.map(e => e.href)")
    for href in links:
        parsed = urlsplit(href)
        if parsed.hostname != "127.0.0.1":
            continue
        target = site / unquote(parsed.path).lstrip("/")
        if target.is_dir():
            target /= "index.html"
        require(target.is_file(), f"Broken local navigation: {href}")


def check_toc(page: Page) -> bool:
    toc = page.locator(".post-toc")
    if not toc.count():
        return False
    require(toc.get_attribute("open") is None, "TOC must initially be collapsed")
    toc.locator("summary").click()
    require(toc.get_attribute("open") is not None, "TOC did not open")
    fragments = toc.locator("a").evaluate_all("els => els.map(e => e.hash)")
    require(bool(fragments), "TOC has no links")
    for fragment in fragments:
        require(page.evaluate("hash => !!document.getElementById(decodeURIComponent(hash.slice(1)))", fragment),
                f"Missing TOC target: {fragment}")
    toc.locator("a").first.click()
    page.wait_for_function("hash => decodeURIComponent(location.hash) === decodeURIComponent(hash)", arg=fragments[0])
    page.wait_for_function("""hash => {
      const r = document.getElementById(decodeURIComponent(hash.slice(1))).getBoundingClientRect();
      return r.top >= -1 && r.top < innerHeight;
    }""", arg=fragments[0])
    toc.locator("summary").click()
    require(toc.get_attribute("open") is None, "TOC did not close")
    return True


def check_code_scrolling(page: Page) -> int:
    count = 0
    for pre in page.locator(".post-body pre").all():
        require(pre.evaluate("e => getComputedStyle(e).overflowX") == "auto", "pre horizontal scrolling was overridden")
        extent = pre.evaluate("e => e.scrollWidth - e.clientWidth")
        if extent <= 1:
            continue
        pre.evaluate("e => e.scrollLeft = 0")  # Initial state only; validation uses wheel input.
        pre.hover()
        handle = pre.element_handle()
        page.mouse.wheel(min(250, extent), 0)
        page.wait_for_function("e => e.scrollLeft > 0", arg=handle)
        page.mouse.wheel(extent + 100, 0)
        page.wait_for_function("e => Math.abs(e.scrollLeft - (e.scrollWidth - e.clientWidth)) <= 2", arg=handle)
        page.mouse.wheel(-extent - 100, 0)
        page.wait_for_function("e => e.scrollLeft <= 1", arg=handle)
        require(page.evaluate("window.scrollX") == 0, "Code scrolling moved the page horizontally")
        handle.dispose()
        count += 1
    return count


def expect_detected(check, message: str):
    try:
        check()
    except AssertionError:
        return
    raise AssertionError(message)


def negative_controls(page: Page, origin: str, post: str, highlighted_post: str):
    page.set_viewport_size({"width": 390, "height": 844})
    visit(page, origin + post)
    style = page.add_style_tag(content='@media(max-width:1040px){.blog-post__grid{grid-template-columns:1fr;grid-template-areas:"header" "body" "rail";}}')
    expect_detected(lambda: check_geometry(geometry(page)), "Regression test missed the original Grid bug")
    style.evaluate("e => e.remove()")
    check_geometry(geometry(page))
    visit(page, origin + highlighted_post)
    style = page.add_style_tag(content=".post-body .highlight { overflow: hidden; }")
    pre = page.locator(".post-body pre.highlight").first
    expect_detected(lambda: require(pre.evaluate("e => getComputedStyle(e).overflowX") == "auto", "hidden"),
                    "Regression test missed the original code overflow bug")
    style.evaluate("e => e.remove()")
    require(pre.evaluate("e => getComputedStyle(e).overflowX") == "auto", "Fixed code style did not recover")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=Path("_site"))
    parser.add_argument("--report", type=Path, default=Path("_layout-report"))
    parser.add_argument("--browsers", nargs="+", choices=("chromium", "webkit"), default=["chromium", "webkit"])
    parser.add_argument("--chromium-executable", help="Optional local Chromium path; CI uses pinned Playwright browsers")
    args = parser.parse_args()
    site = args.site.resolve()
    args.report.mkdir(parents=True, exist_ok=True)
    posts, highlighted = [], []
    for path in sorted((site / "blog").rglob("index.html")):
        text = path.read_text(encoding="utf-8")
        if 'class="blog-post__grid"' not in text:
            continue
        url = "/" + quote(path.parent.relative_to(site).as_posix()) + "/"
        posts.append(url)
        if '<pre class="highlight"' in text:
            highlighted.append(url)
    require(bool(posts), "No generated articles found; build Jekyll first")
    require(bool(highlighted), "No Rouge code blocks found for the negative control")
    report = {"articles": len(posts), "widths": WIDTHS, "browsers": {}, "errors": []}
    with serve(site) as origin, sync_playwright() as playwright:
        for name in args.browsers:
            options = {"executable_path": args.chromium_executable} if name == "chromium" and args.chromium_executable else {}
            browser = getattr(playwright, name).launch(**options)
            context = browser.new_context(viewport={"width": 390, "height": 844}, locale="ja-JP", reduced_motion="reduce")
            context.route("**/*", lambda route: route.continue_() if urlsplit(route.request.url).hostname == "127.0.0.1" else route.abort())
            page = context.new_page()
            page.set_default_timeout(10000)
            result = {"version": browser.version, "measurements": [], "scrollable_code_blocks": 0, "toc_pages": 0}
            report["browsers"][name] = result
            try:
                negative_controls(page, origin, posts[0], highlighted[0])
                result["negative_controls"] = "both original defects detected"
                for width in WIDTHS:
                    page.set_viewport_size({"width": width, "height": 844})
                    for url in posts:
                        visit(page, origin + url)
                        data = geometry(page)
                        check_geometry(data)
                        check_content_bounds(page)
                        result["measurements"].append({"url": url, "width": width, **data})
                        if width == 390:
                            stem = sha256(url.encode()).hexdigest()[:12]
                            page.screenshot(path=str(args.report / f"{name}-{stem}-390.png"))
                            check_links(page, site)
                            result["toc_pages"] += int(check_toc(page))
                            result["scrollable_code_blocks"] += check_code_scrolling(page)
                            check_geometry(geometry(page))
                    for url in ("/", "/blog/"):
                        visit(page, origin + url)
                        require(page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1"),
                                f"Home/index overflows at {width}: {url}")
                        check_links(page, site)
                        if width in (390, 1440):
                            label = "home" if url == "/" else "blog"
                            page.screenshot(path=str(args.report / f"{name}-{label}-{width}.png"))
                require(result["scrollable_code_blocks"] > 0, "No real code scrolling was tested")
                require(result["toc_pages"] > 0, "No TOC interaction was tested")
                result["status"] = "passed"
                print(f"{name}: {len(posts)} articles x {len(WIDTHS)} widths; "
                      f"{result['scrollable_code_blocks']} code blocks scrolled; {result['toc_pages']} TOCs checked", flush=True)
            except Exception as error:
                result["status"] = "failed"
                report["errors"].append(f"{name}: {page.url}: {error}")
                print(report["errors"][-1], flush=True)
                try:
                    page.screenshot(path=str(args.report / f"{name}-failure.png"))
                except Exception as screenshot_error:
                    result["screenshot_error"] = str(screenshot_error)
            finally:
                context.close()
                browser.close()
                (args.report / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Report: {args.report / 'report.json'}", flush=True)
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
