from __future__ import annotations

import argparse

from scripts.blueprint_harness import (
    add_allow_local_build_argument,
    add_manifest_argument,
    add_output_root_argument,
    add_project_selection_argument,
    add_serial_argument,
    command_generate,
    command_projects,
    command_reference_edit,
    command_reference_prune,
    command_reference_sync,
    command_validate,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python3 -m scripts.blueprint_reference_harness",
        description="Reference blueprint generation, validation, and checkout lifecycle CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser(
        "generate",
        help="Build the selected blueprint harness projects.",
    )
    add_output_root_argument(generate)
    add_project_selection_argument(generate, help_text="Render only the selected project. Repeat to render more than one.")
    add_manifest_argument(generate)
    generate.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip project builds and only run already-built or command-only generation steps.",
    )
    add_serial_argument(generate)
    add_allow_local_build_argument(
        generate,
        help_text="Permit `lake build` in a linked worktree instead of requiring synced root executables.",
    )
    generate.set_defaults(func=command_generate)

    validate = subparsers.add_parser(
        "validate",
        help="Generate selected projects and run configured regressions.",
    )
    add_output_root_argument(validate)
    add_project_selection_argument(validate, help_text="Restrict generation to the selected project. Repeat to select more.")
    add_manifest_argument(validate)
    validate.add_argument(
        "--run-lean-tests",
        action="store_true",
        help="Also run this repository's Lean tests before project generation.",
    )
    validate.add_argument(
        "--skip-panel-regression",
        action="store_true",
        help="Skip configured static panel regression checks.",
    )
    validate.add_argument(
        "--skip-browser-tests",
        action="store_true",
        help="Skip configured Playwright browser regression suites.",
    )
    add_serial_argument(validate)
    validate.add_argument(
        "--pytest-arg",
        action="append",
        default=[],
        help="Extra argument forwarded to pytest. Repeat for multiple arguments.",
    )
    add_allow_local_build_argument(
        validate,
        help_text="Permit `lake build` and `lake test` in a linked worktree instead of requiring synced root artifacts.",
    )
    validate.add_argument(
        "--stop-on-first-failure",
        action="store_true",
        help="Stop validation as soon as one phase fails instead of collecting later failures.",
    )
    validate.set_defaults(func=command_validate)

    projects = subparsers.add_parser(
        "projects",
        help="List the configured harness projects from the active manifest.",
    )
    add_manifest_argument(projects)
    projects.set_defaults(func=command_projects)

    sync = subparsers.add_parser(
        "sync",
        help="Warm shared reference blueprint caches and prepare local clones for the current checkout.",
    )
    add_manifest_argument(sync)
    add_project_selection_argument(
        sync,
        help_text="Restrict sync to the selected project. Repeat to select more.",
        include_example_alias=False,
    )
    sync.add_argument(
        "--skip-build",
        action="store_true",
        help="Update and clone the reference projects without warming their build artifacts.",
    )
    sync.add_argument(
        "--skip-local-checkout",
        action="store_true",
        help="Warm only the shared cache checkout and skip preparing the current checkout's local clones.",
    )
    sync.set_defaults(func=command_reference_sync)

    edit = subparsers.add_parser(
        "edit",
        help="Prepare or reuse one editable external reference checkout for manual changes.",
    )
    add_manifest_argument(edit)
    edit.add_argument("project", help="External git-checkout project id to open for editing.")
    edit.add_argument(
        "--branch",
        default=None,
        help="Editable branch name. Defaults to `wip/<project-id>`.",
    )
    edit.add_argument(
        "--base",
        default=None,
        help="Base ref used when creating the editable branch. Defaults to `origin/<project-ref>`.",
    )
    edit.set_defaults(func=command_reference_edit)

    prune = subparsers.add_parser(
        "prune",
        help="Remove stale harness-managed reference blueprint caches and checkout clones.",
    )
    add_manifest_argument(prune)
    prune.add_argument(
        "--dry-run",
        action="store_true",
        help="List stale paths without deleting them.",
    )
    prune.set_defaults(func=command_reference_prune)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
