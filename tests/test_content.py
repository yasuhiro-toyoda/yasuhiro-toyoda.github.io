import copy
import datetime as dt
from pathlib import Path
import tempfile
import unittest

from scripts.check_content import JST, read_post, validate_post, validate_thumbnail


class ContentTests(unittest.TestCase):
    def setUp(self):
        self.path = Path("_posts/2026/09/2026-09-28-example.md")
        self.now = dt.datetime(2026, 9, 28, 18, tzinfo=JST)
        self.post = dict(title="記事", description="説明", date="2026-09-28 00:00:00 +0900",
                         category="開発", tags=["dev-memo"], excerpt="要約")

    def validate(self, **changes):
        post = copy.deepcopy(self.post)
        post.update(changes)
        return validate_post(self.path, post, {"開発"}, {"dev-memo"}, self.now)

    def test_valid_post(self):
        self.assertEqual([], self.validate())

    def test_missing_required_value(self):
        self.assertIn("description is required", self.validate(description=" "))

    def test_filename_date_mismatch(self):
        self.assertIn("filename, directory and date must match", self.validate(date="2026-09-27 00:00:00 +0900"))

    def test_future_date(self):
        self.assertTrue(any("future date" in e for e in self.validate(date="2026-12-31 00:00:00 +0900")))

    def test_missing_timezone(self):
        self.assertTrue(any("timezone" in e for e in self.validate(date="2026-09-28")))

    def test_unknown_tag_and_category(self):
        self.assertTrue(any("registered slugs" in e for e in self.validate(tags=["unknown"])))
        self.assertTrue(any("registered label" in e for e in self.validate(category="unknown")))

    def test_thumbnail_alt(self):
        self.assertTrue(any("thumbnail_alt" in e for e in self.validate(thumbnail="/assets/a.png")))

    def test_deleted_and_traversal_thumbnail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "assets").mkdir()
            image = root / "assets/a.png"
            image.write_bytes(b"fixture")
            self.assertEqual([], validate_thumbnail(root, {"thumbnail": "/assets/a.png"}))
            image.unlink()
            self.assertTrue(validate_thumbnail(root, {"thumbnail": "/assets/a.png"}))
            self.assertTrue(validate_thumbnail(root, {"thumbnail": "/assets/../../outside.png"}))

    def test_missing_front_matter(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "post.md"
            path.write_text("本文だけ", encoding="utf-8")
            with self.assertRaises(ValueError):
                read_post(path)


if __name__ == "__main__":
    unittest.main()
