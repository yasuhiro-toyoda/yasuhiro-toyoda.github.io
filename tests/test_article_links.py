import tempfile
from pathlib import Path
import unittest

from scripts.check_post_layout import Document, check_article, check_internal_links


class ArticleLinksTests(unittest.TestCase):
    def test_inline_bookmark_query_and_fragment_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            (site / "blog/existing").mkdir(parents=True)
            (site / "blog/existing/index.html").write_text('<h1 id="section">Target</h1>')
            root = Document('''<a href="/blog/existing/?category=test#section">Valid</a>
                <a class="bookmark-card" href="/blog/missing/">Broken card</a>
                <p><a href="https://musashistudio.com/blog/missing-inline/">Broken inline</a></p>
                <a href="https://external.example/missing/">External</a>
                <a href="mailto:hello@example.com">Mail</a>''').root
            errors = check_internal_links(root, site, site / "index.html")
            self.assertEqual(2, len(errors))
            self.assertTrue(any("missing-inline" in e for e in errors))
            self.assertTrue(any("/blog/missing/" in e for e in errors))

    def test_missing_fragment_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            (site / "index.html").write_text('<h1 id="existing">Title</h1>')
            root = Document('<h1 id="existing">Title</h1><a href="#absent">Broken</a>').root
            self.assertTrue(check_internal_links(root, site, site / "index.html"))

    def test_skipped_heading_is_rejected_but_normal_hierarchy_is_allowed(self):
        for headings, expected in [("<h2>A</h2><h4>B</h4>", True),
                                   ("<h2>A</h2><h3>B</h3><h2>C</h2>", False)]:
            root = Document('<header class="post-header"></header><div class="post-body">'
                            + headings + '</div>').root
            errors = check_article(root, Path("_site"))
            self.assertEqual(expected, any("skip a level" in e for e in errors))
