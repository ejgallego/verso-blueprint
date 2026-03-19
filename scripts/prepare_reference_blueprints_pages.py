#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
from pathlib import Path
import shutil


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a GitHub Pages site for the generated reference blueprints."
    )
    parser.add_argument(
        "--input-root",
        default="_out/reference-blueprints",
        help="Directory containing generated reference blueprint outputs.",
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


def main() -> int:
    args = parse_args()
    input_root = Path(args.input_root).resolve()
    output_root = Path(args.output_root).resolve()
    publish_root = output_root / "reference-blueprints"

    if not input_root.exists():
        raise SystemExit(f"missing reference blueprint output root: {input_root}")

    if output_root.exists():
        shutil.rmtree(output_root)
    publish_root.mkdir(parents=True, exist_ok=True)

    projects: list[str] = []
    for project_dir in sorted(path for path in input_root.iterdir() if path.is_dir()):
        site_dir = project_dir / "html-multi"
        if not site_dir.exists():
            continue
        shutil.copytree(site_dir, publish_root / project_dir.name)
        projects.append(project_dir.name)

    index = output_root / "index.html"
    index.write_text(
        "\n".join(
            [
                "<!doctype html>",
                "<html lang=\"en\">",
                "<meta charset=\"utf-8\">",
                "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
                "<title>Verso Blueprint Reference Blueprints</title>",
                "<body>",
                "<h1>Verso Blueprint Reference Blueprints</h1>",
                "<p>Generated reference sites assembled from the current workflow run.</p>",
                "<ul>",
                *[html_link(project_id) for project_id in projects],
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
