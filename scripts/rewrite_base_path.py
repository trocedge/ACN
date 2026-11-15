#!/usr/bin/env python3
"""Rewrite root-absolute URLs in a built site so it can live under a sub-path.

GitHub Pages serves project sites from ``https://<owner>.github.io/<repo>/``.
Assets referenced as ``/site.css`` would resolve against the domain root and
404 there, so every root-absolute reference in the generated HTML/CSS/JS is
prefixed with the base path. Root-domain deployments pass an empty base path
and the files are left untouched.
"""

import argparse
import re
from pathlib import Path

TEXT_SUFFIXES = {".html", ".htm", ".css", ".js"}

HTML_ATTRIBUTE = re.compile(
    r'(?P<pre>\b(?:href|src|action|poster|content)=")(?P<url>/(?!/))')
CSS_URL = re.compile(r'(?P<pre>url\(\s*[\'"]?)(?P<url>/(?!/))')
JS_FETCH = re.compile(r'(?P<pre>\bfetch\(\s*[\'"])(?P<url>/(?!/))')


def normalise_base(base_path: str) -> str:
    base_path = (base_path or "").strip()
    if not base_path or base_path == "/":
        return ""
    return "/" + base_path.strip("/")


def prefix_references(text: str, base_path: str) -> tuple[str, int]:
    replaced = 0

    def substitute(match: re.Match[str]) -> str:
        nonlocal replaced
        url = match.group("url")
        if url == f"{base_path}/" or url.startswith(f"{base_path}/"):
            return match.group(0)
        replaced += 1
        return f"{match.group('pre')}{base_path}{url}"

    for pattern in (HTML_ATTRIBUTE, CSS_URL, JS_FETCH):
        text = pattern.sub(substitute, text)
    return text, replaced


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="Built site directory, e.g. dist")
    parser.add_argument("--base-path", default="", help="Sub-path such as /ACN")
    args = parser.parse_args()

    base_path = normalise_base(args.base_path)
    if not base_path:
        print("No base path requested; nothing to rewrite.")
        return

    changed_files = 0
    changed_references = 0
    for path in sorted(args.directory.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        original = path.read_text(encoding="utf-8")
        updated, replaced = prefix_references(original, base_path)
        if replaced:
            path.write_text(updated, encoding="utf-8")
            changed_files += 1
            changed_references += replaced

    print(f"Prefixed {changed_references} references in {changed_files} files with {base_path}.")


if __name__ == "__main__":
    main()
