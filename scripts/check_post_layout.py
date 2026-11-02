"""Check the generated common article layout without third-party dependencies."""

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit


class Element:
    def __init__(self, tag, attrs=(), parent=None):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.children = []
        self.text = ""

    def walk(self):
        for child in self.children:
            yield child
            yield from child.walk()

    def find(self, *, tag=None, css_class=None):
        return [element for element in self.walk()
                if (tag is None or element.tag == tag)
                and (css_class is None or css_class in element.attrs.get("class", "").split())]


class Document(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.root = Element("document")
        self.current = self.root
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        element = Element(tag, attrs, self.current)
        self.current.children.append(element)
        if tag not in self.VOID:
            self.current = element

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        element = self.current
        while element.parent is not None:
            if element.tag == tag:
                self.current = element.parent
                return
            element = element.parent

    def handle_data(self, data):
        element = self.current
        while element is not None:
            element.text += data
            element = element.parent


def check_article(root, site):
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    headers, bodies = root.find(css_class="post-header"), root.find(css_class="post-body")
    require(len(headers) == len(bodies) == 1, "one article header and body are required")
    if not headers or not bodies:
        return errors
    header, body = headers[0], bodies[0]
    previous_level = 1
    for element in body.walk():
        if element.tag in {"h2", "h3", "h4", "h5", "h6"}:
            level = int(element.tag[1])
            require(level <= previous_level + 1, "article headings must not skip a level")
            previous_level = level
    require(len(root.find(tag="h1")) == 1 and len(header.find(tag="h1")) == 1,
            "H1 must be the article title only")
    require(not header.find(css_class="post-lead"), "the standalone excerpt must be hidden")
    require(header.children and header.children[0].tag == "h1", "the title must appear first")
    require(len(header.children) >= 2 and "post-header__meta" in header.children[1].attrs.get("class", ""),
            "metadata must follow the title")
    heroes = header.find(css_class="post-hero-media")
    require(not heroes or (len(header.children) >= 3 and header.children[2] is heroes[0]),
            "the eyecatch must follow metadata")
    descriptions = [element for element in root.find(tag="meta") if element.attrs.get("name") == "description"]
    require(descriptions and descriptions[0].attrs.get("content", "").strip(), "meta description must be retained")
    headings, toc = body.find(tag="h2"), body.find(css_class="post-toc")
    require(len(toc) == (1 if len(headings) >= 3 else 0), "TOC must appear only for at least three H2s")
    if toc:
        links = toc[0].find(tag="a")
        require([unquote(link.attrs.get("href", "").removeprefix("#")) for link in links]
                == [heading.attrs.get("id") for heading in headings],
                "TOC links must match the actual H2 IDs in order")
        require(all(link.text.strip() for link in links), "TOC labels must not be empty")
        require("open" not in toc[0].attrs, "TOC must initially be collapsed")
        require(body.children.index(toc[0]) < body.children.index(headings[0]), "TOC must precede article sections")
    introductions = body.find(css_class="post-intro")
    require(not introductions or body.children[0] is introductions[0], "introduction must precede TOC and sections")
    ids = [element.attrs["id"] for element in root.walk() if "id" in element.attrs]
    require(len(ids) == len(set(ids)), "element IDs must be unique")
    footers = root.find(css_class="blog-post__footer")
    require(len(footers) == 1, "article footer is required")
    if footers:
        footer = footers[0]
        back = footer.find(css_class="post-back")
        back_links = back[0].find(tag="a") if back else []
        require(back and footer.children[-1] is back[0], "blog return link must finish the article footer")
        require(back_links and back_links[0].attrs.get("href", "").endswith("/blog/"), "return link must point to blog index")
        related = footer.find(css_class="post-related")
        require(not related or (footer.children[0] is related[0] and 1 <= len(related[0].find(tag="a")) <= 3),
                "up to three related articles may precede the return link")
        for nav in related:
            for link in nav.find(tag="a"):
                target = site / unquote(urlsplit(link.attrs.get("href", "")).path).lstrip("/") / "index.html"
                require(target.is_file(), "related article must exist in the generated site")
    return errors


def check_internal_links(root, site, page_path):
    """Resolve all article links, including inline and bookmark-card links."""
    errors = []
    canonical = next((e.attrs.get("href") for e in root.find(tag="link")
                      if e.attrs.get("rel") == "canonical"), None)
    base = canonical or "https://musashistudio.com/" + page_path.relative_to(site).as_posix()
    host = urlsplit(base).netloc
    for link in root.find(tag="a"):
        href = link.attrs.get("href", "")
        target_url = urlsplit(urljoin(base, href))
        if not href or target_url.scheme not in {"http", "https"} or target_url.netloc != host:
            continue
        target = (site / unquote(target_url.path).lstrip("/")).resolve()
        if not target.is_relative_to(site.resolve()):
            errors.append(f"internal link escapes the site: {href}")
            continue
        if target.is_dir():
            target /= "index.html"
        if not target.is_file():
            errors.append(f"internal link target does not exist: {href}")
        elif target_url.fragment:
            target_root = root if target == page_path.resolve() else Document(target.read_text(encoding="utf-8")).root
            ids = {e.attrs.get("id") for e in target_root.walk()}
            if unquote(target_url.fragment) not in ids:
                errors.append(f"internal link fragment does not exist: {href}")
    return errors


def check_index_card(card):
    images = card.find(tag="img")
    if card.attrs.get("data-thumbnail") == "none":
        if images or card.find(css_class="post-card__media"):
            return ["text-only blog cards must not retain an image or empty media frame"]
    elif not images:
        return ["blog index cards must retain an image unless explicitly text-only"]
    if not (card.find(tag="h2") and card.find(css_class="post-card__excerpt") and card.find(tag="time")):
        return ["blog index cards must retain title, excerpt and date"]
    return []


def check_site(site):
    errors, count = [], 0
    for path in sorted((site / "blog").rglob("index.html")):
        root = Document(path.read_text(encoding="utf-8")).root
        if root.find(css_class="post-layout"):
            count += 1
            errors += [f"{path.relative_to(site)}: {error}" for error in check_article(root, site)]
            errors += [f"{path.relative_to(site)}: {error}" for error in check_internal_links(root, site, path)]
    index = site / "blog/index.html"
    if index.is_file():
        cards = Document(index.read_text(encoding="utf-8")).root.find(css_class="post-card")
        for card in cards:
            errors += check_index_card(card)
    if not count:
        errors.append("no generated article pages were found")
    return errors, count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=Path("_site"))
    findings, total = check_site(parser.parse_args().site)
    for finding in findings:
        print(finding)
    if findings:
        raise SystemExit(1)
    print(f"Generated article layout passed for {total} articles and the blog index.")
