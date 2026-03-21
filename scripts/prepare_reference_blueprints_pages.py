#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
from pathlib import Path
import shutil


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a GitHub Pages site for the generated reference and test blueprints."
    )
    parser.add_argument(
        "--reference-root",
        default="_out/reference-blueprints",
        help="Directory containing generated reference blueprint outputs.",
    )
    parser.add_argument(
        "--test-root",
        default="_out/test-blueprints",
        help="Directory containing generated test blueprint outputs.",
    )
    parser.add_argument(
        "--output-root",
        default="_site",
        help="Directory to populate with the Pages artifact.",
    )
    return parser.parse_args()


def html_link(project_id: str) -> str:
    label = html.escape(project_id)
    href = f"reference-blueprints/{label}/"
    return f'<li><a href="{href}">{label}</a></li>'


def html_test_link(slug: str) -> str:
    label = html.escape(slug)
    href = f"test-blueprints/{label}/html-multi/"
    return f'<li><a href="{href}">{label}</a></li>'


def main() -> int:
    args = parse_args()
    reference_root = Path(args.reference_root).resolve()
    test_root = Path(args.test_root).resolve()
    output_root = Path(args.output_root).resolve()
    publish_reference_root = output_root / "reference-blueprints"
    publish_test_root = output_root / "test-blueprints"

    if not reference_root.exists():
        raise SystemExit(f"missing reference blueprint output root: {reference_root}")
    if not test_root.exists():
        raise SystemExit(f"missing test blueprint output root: {test_root}")

    if output_root.exists():
        shutil.rmtree(output_root)
    publish_reference_root.mkdir(parents=True, exist_ok=True)
    publish_test_root.mkdir(parents=True, exist_ok=True)

    reference_projects: list[str] = []
    for project_dir in sorted(path for path in reference_root.iterdir() if path.is_dir()):
        site_dir = project_dir / "html-multi"
        if not site_dir.exists():
            continue
        shutil.copytree(site_dir, publish_reference_root / project_dir.name)
        reference_projects.append(project_dir.name)

    test_blueprints: list[str] = []
    for test_dir in sorted(path for path in test_root.iterdir() if path.is_dir()):
        if not (test_dir / "html-multi").exists():
            continue
        shutil.copytree(test_dir, publish_test_root / test_dir.name)
        test_blueprints.append(test_dir.name)
    test_index = test_root / "index.html"
    if test_index.exists():
        shutil.copy2(test_index, publish_test_root / "index.html")

    index = output_root / "index.html"
    index.write_text(
        "\n".join(
            [
                "<!doctype html>",
                "<html lang=\"en\">",
                "<meta charset=\"utf-8\">",
                "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
                "<title>Verso Blueprint Rendered Artifacts</title>",
                "<body>",
                "<h1>Verso Blueprint Rendered Artifacts</h1>",
                "<p>Generated reference and test sites assembled from the current workflow run.</p>",
                "<h2>Reference Blueprints</h2>",
                "<ul>",
                *[html_link(project_id) for project_id in reference_projects],
                "</ul>",
                "<h2>Test Blueprints</h2>",
                "<p><a href=\"test-blueprints/\">Open categorized test blueprint index</a></p>",
                "<ul>",
                *[html_test_link(slug) for slug in test_blueprints],
                "</ul>",
                "</body>",
                "</html>",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
