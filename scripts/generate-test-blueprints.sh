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
    "summary": "Standalone browser-regression showcase with summary, graph, panel, and inline preview pages.",
}
entries = [meta_by_slug[slug] for slug in selected if slug in meta_by_slug]

cards = []
for entry in entries:
    slug = entry["slug"]
    title = entry["title"]
    summary = entry["summary"]
    cards.append(
        f"""
        <article class="card">
          <h2><a href="./{slug}/html-multi/">{title}</a></h2>
          <p class="slug"><code>{slug}</code></p>
          <p>{summary}</p>
          <p><a href="./{slug}/html-multi/">Open site</a></p>
        </article>
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
      <section class="grid">
        {''.join(cards)}
      </section>
    </main>
  </body>
</html>
"""

(root / "index.html").write_text(html, encoding="utf-8")
PY
