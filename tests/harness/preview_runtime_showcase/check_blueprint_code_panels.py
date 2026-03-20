#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

PACKAGE_ROOT = Path(__file__).resolve().parents[3]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from scripts.blueprint_harness_paths import default_test_blueprint_site_dir, resolve_cli_path


def fail(msg: str) -> None:
    print(f"[blueprint-panel-regression] FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def load(path: Path) -> str:
    if not path.exists():
        fail(f"missing file: {path}")
    return path.read_text(encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Static regression checks for generated local code-panel showcase pages."
    )
    parser.add_argument(
        "--site-dir",
        default=None,
        help="Path to the generated preview_runtime_showcase html-multi directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_root = (
        resolve_cli_path(args.site_dir)
        if args.site_dir is not None
        else default_test_blueprint_site_dir("preview_runtime_showcase", Path(__file__))
    )
    code_panels = load(out_root / "Code-Panels" / "index.html")

    if "bp_external_status_badge_summary bp_external_status_ok" not in code_panels:
        fail("missing external summary badge for complete external declarations")
    if "bp_external_status_badge_summary bp_external_status_sorry" not in code_panels:
        fail("missing external warning summary badge for sorry-backed declarations")
    if "External Lean for " in code_panels:
        fail("stale external panel caption still present")
    if "Code for Definition" not in code_panels:
        fail("definition code panel caption missing")
    if "Code for Theorem" not in code_panels:
        fail("theorem code panel caption missing")
    if 'bp_external_status_badge_text">1 theorem<' not in code_panels:
        fail("missing theorem-specific external summary text")
    if 'bp_external_status_badge_text">1 definition<' not in code_panels:
        fail("missing definition-specific external summary text")
    if "bp-renderer-select" in code_panels:
        fail("stale external renderer switcher still present")
    if "bp_code_expand_hint" in code_panels:
        fail("stale expand hint markup still present")

    panel_re = re.compile(r'<details class="bp_code_block bp_code_panel"[^>]*>.*?</details>', re.S)
    external_panels = [p for p in panel_re.findall(code_panels) if "bp_external_status_badge_summary" in p]
    if len(external_panels) < 3:
        fail("expected at least three external code panels in local showcase")

    for i, panel in enumerate(external_panels, start=1):
        if "bp_code_progress" in panel:
            fail(f"external panel #{i} still renders a progress bar")
        if 'class="namedocs"' in panel:
            fail(f"external panel #{i} still includes nested namedocs wrapper")
        if "bp_external_decl_renderer_variant" in panel:
            fail(f"external panel #{i} still includes renderer variants")
        if "data-bp-external-renderer" in panel:
            fail(f"external panel #{i} still includes renderer mode attributes")
        if "bp_external_decl_rendered" not in panel:
            fail(f"external panel #{i} missing rendered external declaration body")
        if "bp_external_decl_stmt" not in panel:
            fail(f"external panel #{i} missing external declaration statement block")

    literate_panels = [p for p in panel_re.findall(code_panels) if "data-bp-proof-fold=" in p]
    if not literate_panels:
        fail("no literate code panels found in local showcase")

    for i, panel in enumerate(literate_panels, start=1):
        if "bp_code_summary_indicator" not in panel:
            fail(f"literate panel #{i} missing summary indicator wrapper")
        if "bp_code_progress" not in panel:
            fail(f"literate panel #{i} missing progress bar")
        if "panelInlineOk" not in panel or "panelInlineSorry" not in panel:
            fail(f"literate panel #{i} missing expected local declarations")

    print(
        "[blueprint-panel-regression] OK:",
        f"external_panels={len(external_panels)}",
        f"literate_panels={len(literate_panels)}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
