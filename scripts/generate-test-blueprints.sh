#!/usr/bin/env bash

set -euo pipefail

package_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$package_root"

output_root="$(python3 - <<'PY'
from pathlib import Path
from scripts.blueprint_harness_paths import detect_harness_layout

layout = detect_harness_layout(Path.cwd())
print(layout.test_blueprint_output_root)
PY
)"

standalone_slugs=("preview_runtime_showcase")

generate_preview_runtime_showcase() {
  local project_dir="$package_root/tests/test_blueprints/preview_runtime_showcase"
  local output_dir="$output_root/preview_runtime_showcase"
  local manifest="$project_dir/lake-manifest.json"

  mkdir -p "$output_dir"

  (
    set -euo pipefail
    backup="$(mktemp)"
    cp "$manifest" "$backup"
    restore() {
      cp "$backup" "$manifest"
      rm -f "$backup"
    }
    trap restore EXIT

    cd "$project_dir"
    "$package_root/scripts/lean-low-priority" lake update VersoBlueprint
    "$package_root/scripts/lean-low-priority" lake build
    "$package_root/scripts/lean-low-priority" lake exe blueprint-gen --output "$output_dir"
  )
}

if [ "$#" -eq 0 ]; then
  mapfile -t docs < <(./scripts/lean-low-priority lake exe blueprint-test-docs --list)
  standalone=("${standalone_slugs[@]}")
  output_root="$output_root" python3 - <<'PY'
import os
from pathlib import Path

root = Path(os.environ["output_root"])
expected = set()
for line in os.popen("./scripts/lean-low-priority lake exe blueprint-test-docs --list"):
    slug = line.strip()
    if slug:
        expected.add(slug)
for slug in ("preview_runtime_showcase",):
    expected.add(slug)
if root.exists():
    for child in root.iterdir():
        if child.is_dir() and child.name not in expected:
            import shutil
            shutil.rmtree(child)
PY
else
  docs=()
  standalone=()
  for target in "$@"; do
    case "$target" in
      preview_runtime_showcase)
        standalone+=("$target")
        ;;
      *)
        docs+=("$target")
        ;;
    esac
  done
fi

for doc in "${docs[@]}"; do
  ./scripts/lean-low-priority lake exe blueprint-test-docs "$doc" --output "$output_root/$doc"
done

for project in "${standalone[@]}"; do
  case "$project" in
    preview_runtime_showcase)
      generate_preview_runtime_showcase
      ;;
  esac
done

output_root="$output_root" selected_docs="$(printf '%s\n' "${docs[@]}")" selected_standalone="$(printf '%s\n' "${standalone[@]}")" python3 - <<'PY'
from collections import OrderedDict
import json
import os
from pathlib import Path

root = Path(os.environ["output_root"])
root.mkdir(parents=True, exist_ok=True)
selected = [line.strip() for line in os.environ["selected_docs"].splitlines() if line.strip()]
selected += [line.strip() for line in os.environ["selected_standalone"].splitlines() if line.strip()]
meta = json.loads(os.popen("./scripts/lean-low-priority lake exe blueprint-test-docs --list-json").read())
meta_by_slug = {entry["slug"]: entry for entry in meta}
meta_by_slug["preview_runtime_showcase"] = {
    "slug": "preview_runtime_showcase",
    "title": "Preview Runtime Showcase",
    "category": "Preview Runtime",
    "summary": "Standalone browser-regression showcase with summary, graph, panel, and inline preview pages.",
}
entries = [meta_by_slug[slug] for slug in selected if slug in meta_by_slug]

cards_by_category = OrderedDict()
for entry in entries:
    category = entry.get("category", "Uncategorized")
    slug = entry["slug"]
    title = entry["title"]
    summary = entry["summary"]
    cards_by_category.setdefault(category, []).append(
        f"""
        <article class="card">
          <h2><a href="./{slug}/html-multi/">{title}</a></h2>
          <p class="category">{category}</p>
          <p class="slug"><code>{slug}</code></p>
          <p>{summary}</p>
          <p><a href="./{slug}/html-multi/">Open site</a></p>
        </article>
        """
    )

nav_links = []
sections = []
for category, cards in cards_by_category.items():
    anchor = category.lower().replace(" ", "-")
    nav_links.append(f'<a class="chip" href="#{anchor}">{category}</a>')
    sections.append(
        f"""
        <section class="category_section" id="{anchor}">
          <div class="category_header">
            <h2>{category}</h2>
            <p>{len(cards)} site{'s' if len(cards) != 1 else ''}</p>
          </div>
          <div class="grid">
            {''.join(cards)}
          </div>
        </section>
        """
    )

html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Curated Test Blueprints</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f8fafc;
        --panel: #ffffff;
        --text: #0f172a;
        --muted: #475569;
        --border: #cbd5e1;
        --accent: #0f766e;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: ui-sans-serif, system-ui, sans-serif;
        background: linear-gradient(180deg, #f8fafc, #eef2ff 45%, #f8fafc);
        color: var(--text);
      }}
      main {{
        width: min(70rem, calc(100% - 2rem));
        margin: 0 auto;
        padding: 2rem 0 3rem;
      }}
      header {{
        margin-bottom: 1.5rem;
      }}
      h1 {{
        margin: 0 0 0.5rem;
        font-size: clamp(2rem, 4vw, 2.75rem);
      }}
      .lede {{
        margin: 0;
        max-width: 54rem;
        color: var(--muted);
        line-height: 1.5;
      }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(18rem, 1fr));
        gap: 1rem;
      }}
      .chip_row {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin: 1.1rem 0 1.6rem;
      }}
      .chip {{
        display: inline-flex;
        align-items: center;
        border: 1px solid var(--border);
        border-radius: 999px;
        background: var(--panel);
        padding: 0.35rem 0.7rem;
        font-size: 0.92rem;
        font-weight: 600;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
      }}
      .category_section + .category_section {{
        margin-top: 1.8rem;
      }}
      .category_header {{
        display: flex;
        flex-wrap: wrap;
        align-items: baseline;
        justify-content: space-between;
        gap: 0.5rem 1rem;
        margin-bottom: 0.9rem;
      }}
      .category_header h2 {{
        margin: 0;
        font-size: 1.2rem;
      }}
      .category_header p {{
        margin: 0;
        color: var(--muted);
        font-size: 0.92rem;
      }}
      .card {{
        border: 1px solid var(--border);
        border-radius: 1rem;
        background: var(--panel);
        padding: 1rem 1.05rem;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
      }}
      .card h2 {{
        margin: 0 0 0.4rem;
        font-size: 1.05rem;
      }}
      .category {{
        margin: 0.25rem 0 0;
        color: var(--accent);
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
      }}
      .card p {{
        margin: 0.45rem 0 0;
        line-height: 1.45;
      }}
      .slug {{
        color: var(--muted);
        font-size: 0.9rem;
      }}
      a {{
        color: var(--accent);
        text-decoration: none;
      }}
      a:hover {{
        text-decoration: underline;
      }}
    </style>
  </head>
  <body>
    <main>
      <header>
        <h1>Curated Test Blueprints</h1>
        <p class="lede">Generated inspection sites for in-repo Blueprint test fixtures. Use these pages to review graph, summary, preview, hover, and metadata behavior in a real browser without reaching for external reference projects first.</p>
      </header>
      <nav class="chip_row">
        {''.join(nav_links)}
      </nav>
      {''.join(sections)}
    </main>
  </body>
</html>
"""

(root / "index.html").write_text(html, encoding="utf-8")
PY
