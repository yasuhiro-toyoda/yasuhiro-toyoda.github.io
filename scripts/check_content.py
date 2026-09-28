"""Validate changed post metadata and all existing thumbnail references."""

import argparse
import datetime as dt
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

import yaml

JST = dt.timezone(dt.timedelta(hours=9))
REQUIRED = ("title", "description", "date", "category", "tags", "excerpt")


def read_post(path):
    parts = path.read_text(encoding="utf-8-sig").split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError("YAML front matter is required")
    data = yaml.safe_load(parts[1])
    if not isinstance(data, dict):
        raise ValueError("front matter must be a mapping")
    return data


def validate_post(path, data, categories, tags, now=None):
    errors = []
    for key in REQUIRED:
        value = data.get(key)
        if not value or (isinstance(value, str) and not value.strip()):
            errors.append(f"{key} is required")
    if not isinstance(data.get("category"), str) or data["category"] not in categories:
        errors.append("category must be a registered label")
    post_tags = data.get("tags")
    if not isinstance(post_tags, list) or not post_tags:
        errors.append("tags must be a nonempty list")
    elif any(not isinstance(tag, str) or tag not in tags for tag in post_tags):
        errors.append("tags must contain registered slugs only")
    pattern = re.fullmatch(r"_posts/(\d{4})/(\d{2})/(\d{4}-\d{2}-\d{2})-.+\.md", path.as_posix())
    if not pattern:
        errors.append("post path must be _posts/YYYY/MM/YYYY-MM-DD-slug.md")
    try:
        value = data.get("date")
        date = value if isinstance(value, dt.datetime) else dt.datetime.fromisoformat(str(value))
        if date.tzinfo is None or date.utcoffset() != dt.timedelta(hours=9):
            errors.append("date must include the +09:00 timezone")
        elif date > (now or dt.datetime.now(JST)):
            errors.append("future date would hide this post from publication")
        if pattern and (pattern[3] != date.strftime("%Y-%m-%d")
                        or pattern[1] != date.strftime("%Y")
                        or pattern[2] != date.strftime("%m")):
            errors.append("filename, directory and date must match")
    except (TypeError, ValueError):
        errors.append("date must be a valid timestamp")
    if data.get("thumbnail") and not str(data.get("thumbnail_alt") or "").strip():
        errors.append("thumbnail_alt is required when thumbnail is set")
    return errors


def validate_thumbnail(root, data):
    image = data.get("thumbnail")
    if not image:
        return []
    if not isinstance(image, str):
        return ["thumbnail must be a path string"]
    url = urlsplit(image)
    if url.scheme or url.netloc or not image.startswith("/assets/"):
        return ["thumbnail must be a local /assets/ path"]
    target = (root / unquote(url.path).lstrip("/")).resolve()
    if not target.is_relative_to(root.resolve()) or not target.is_file():
        return [f"thumbnail file does not exist: {image}"]
    return []


def check(root, changed_paths):
    categories = {row["label"] for row in yaml.safe_load((root / "_data/blog_categories.yml").read_text(encoding="utf-8"))}
    tags = {row["slug"] for row in yaml.safe_load((root / "_data/blog_tags.yml").read_text(encoding="utf-8"))}
    changed = set(changed_paths)
    errors = []
    for path in sorted((root / "_posts").rglob("*.md")):
        relative = path.relative_to(root)
        try:
            data = read_post(path)
            findings = validate_thumbnail(root, data)
            if relative.as_posix() in changed:
                findings += validate_post(relative, data, categories, tags)
            errors.extend(f"{relative}: {message}" for message in findings)
        except (ValueError, TypeError, yaml.YAMLError) as exc:
            errors.append(f"{relative}: {exc}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="PR base commit SHA")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    # HEAD is the tested PR merge result: base..HEAD is the proposed change.
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=AMR", "-z", args.base, "HEAD", "--", "_posts"],
        cwd=root, check=True, capture_output=True,
    )
    paths = result.stdout.decode("utf-8").rstrip("\0").split("\0")
    errors = check(root, paths)
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 1
    print("Changed post metadata and all thumbnail references passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
