"""Regression checks for intentionally text-only blog index cards."""
import unittest
from scripts.check_post_layout import Document, check_index_card


class PostIndexTests(unittest.TestCase):
    def check(self, attributes="", media="", content=None):
        if content is None:
            content = '<h2>Title</h2><p class="post-card__excerpt">Excerpt</p><time>2026-10-14</time>'
        root = Document(f'<article class="post-card" {attributes}>{media}{content}</article>').root
        return check_index_card(root.find(css_class="post-card")[0])

    def test_regular_card_keeps_image(self):
        self.assertEqual([], self.check(media='<a class="post-card__media"><img src="image.png"></a>'))

    def test_regular_card_missing_image_is_rejected(self):
        self.assertTrue(self.check())

    def test_explicit_text_only_card(self):
        self.assertEqual([], self.check('data-thumbnail="none"'))

    def test_text_only_card_cannot_keep_image(self):
        self.assertTrue(self.check('data-thumbnail="none"', '<img src="image.png">'))

    def test_text_only_card_cannot_keep_empty_frame(self):
        self.assertTrue(self.check('data-thumbnail="none"', '<a class="post-card__media"></a>'))

    def test_text_only_card_still_requires_content(self):
        self.assertTrue(self.check('data-thumbnail="none"', content='<h2>Title</h2>'))

    def test_unrecognized_opt_out_does_not_hide_errors(self):
        self.assertTrue(self.check('data-thumbnail="false"'))
