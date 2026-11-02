"""Verify JST publication dates and preserve the URLs observed before the timezone fix."""

import argparse
import datetime as dt
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

from check_content import JST, read_post
from check_post_layout import Document


def url_path(url):
    return unquote(urlsplit(url).path)


def check(site, source):
    manifest = json.loads((source / "tests/fixtures/published-post-urls.json").read_text(encoding="utf-8"))
    index = Document((site / "blog/index.html").read_text(encoding="utf-8")).root
    home = Document((site / "index.html").read_text(encoding="utf-8")).root
    cards = index.find(css_class="post-card")
    home_cards = home.find(css_class="post-card")
    errors, expected = [], {}

    def require(condition, message):
        if not condition:
            errors.append(message)

    def check_time(element, date, label):
        visible = f"{date.year}年{date.month}月{date.day}日"
        require(element.text.strip() == visible, f"{label}: displayed publication date must be {visible}")
        try:
            actual = dt.datetime.fromisoformat(element.attrs.get("datetime", ""))
            require(actual == date and actual.utcoffset() == dt.timedelta(hours=9),
                    f"{label}: datetime must retain the source instant in JST")
        except ValueError:
            require(False, f"{label}: valid datetime is required")

    for path, url in manifest["urls"].items():
        data = read_post(source / path)
        value = data["date"]
        date = value if isinstance(value, dt.datetime) else dt.datetime.fromisoformat(value)
        date = date.astimezone(JST)
        expected[url] = date
        output = site / url.lstrip("/") / "index.html"
        if not output.is_file():
            require(False, f"{path}: previously published URL is missing: {url}")
            continue
        root = Document(output.read_text(encoding="utf-8")).root
        headers = root.find(css_class="post-header")
        times = headers[0].find(tag="time") if headers else []
        require(bool(times), f"{url}: publication time is required")
        if times:
            check_time(times[0], date, url)
        canonical = [e.attrs.get("href", "") for e in root.find(tag="link")
                     if e.attrs.get("rel") == "canonical"]
        og_url = [e.attrs.get("content", "") for e in root.find(tag="meta")
                  if e.attrs.get("property") == "og:url"]
        require(len(canonical) == 1 and url_path(canonical[0]) == url, f"{url}: canonical changed")
        require(len(og_url) == 1 and url_path(og_url[0]) == url, f"{url}: og:url changed")
        matched = [c for c in cards if any(url_path(a.attrs.get("href", "")) == url for a in c.find(tag="a"))]
        require(len(matched) == 1, f"{url}: blog index must link to the preserved URL exactly once")
        if matched:
            times = matched[0].find(tag="time")
            require(bool(times), f"{url}: blog index publication time is required")
            if times:
                check_time(times[0], date, f"blog index {url}")
        for card in home_cards:
            if any(url_path(a.attrs.get("href", "")) == url for a in card.find(tag="a")):
                visible = f"{date.year}年{date.month}月{date.day}日"
                require(visible in card.text, f"home {url}: publication date differs from source JST")

    ns = {"a": "http://www.w3.org/2005/Atom"}
    entries = ET.parse(site / "feed.xml").getroot().findall("a:entry", ns)
    require(bool(entries), "Atom feed must contain entries")
    for entry in entries:
        link = entry.find("a:link[@rel='alternate']", ns)
        url = url_path(link.get("href", "")) if link is not None else ""
        if url not in expected:
            continue  # New posts are covered by the normal content and boundary checks.
        date = dt.datetime.fromisoformat(entry.findtext("a:published", default="", namespaces=ns))
        require(date == expected[url] and date.utcoffset() == dt.timedelta(hours=9),
                f"feed {url}: publication date must match source JST")
        require(url_path(entry.findtext("a:id", default="", namespaces=ns)) == url.rstrip("/"),
                f"feed {url}: existing entry identity changed")
    return errors, len(expected), len(entries)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=Path("_site"))
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors, articles, entries = check(args.site, args.source)
    for error in errors:
        print(error)
    if errors:
        raise SystemExit(1)
    print(f"JST dates, canonical/OG URLs and {articles} existing article URLs passed; {entries} feed entries checked.")
