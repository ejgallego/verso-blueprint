from __future__ import annotations

import argparse
from dataclasses import dataclass
import shutil
import subprocess
import sys
from pathlib import Path

from script.blueprint_harness_paths import (
    EXAMPLES,
    canonical_example_site_dir,
    default_example_site_dir,
    detect_harness_layout,
    resolve_output_root,
)


@dataclass(frozen=True)
class StepFailure:
    step: str
    detail: str


def format_command(command: list[str]) -> str:
    return " ".join(command)


def run(command: list[str], *, cwd: Path) -> None:
    print(f"[blueprint-harness] $ {format_command(command)}")
    subprocess.run(command, cwd=cwd, check=True)


def run_capturing_failure(step: str, command: list[str], *, cwd: Path) -> StepFailure | None:
    try:
        run(command, cwd=cwd)
        return None
    except subprocess.CalledProcessError as err:
        return StepFailure(step=step, detail=f"exit code {err.returncode}: {format_command(command)}")


def selected_examples(values: list[str] | None) -> list[str]:
    if not values:
        return list(EXAMPLES)
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result


def lean_low_priority_command(package_root: Path, *args: str) -> list[str]:
    return [str(package_root / "script" / "lean-low-priority"), *args]


def should_use_local_build(layout, allow_local_build: bool) -> bool:
    return (not layout.in_linked_worktree) or allow_local_build


def sync_root_worktree_lake(layout) -> None:
    if not layout.in_linked_worktree:
        return

    source_lake = layout.repo_root / ".lake"
    source_bin_dir = source_lake / "build" / "bin"
    if not source_bin_dir.exists():
        raise SystemExit(
            "[blueprint-harness] root worktree has no prepared `.lake/build/bin` to sync. "
            "Build from the root checkout first; linked worktrees should not bootstrap Mathlib locally."
        )

    if shutil.which("rsync") is None:
        raise SystemExit("[blueprint-harness] `rsync` is required for root-worktree sync.")

    destination_lake = layout.package_root / ".lake"
    destination_lake.mkdir(parents=True, exist_ok=True)
    run(
        [
            "rsync",
            "-a",
            "--delete",
            f"{source_lake}/",
            f"{destination_lake}/",
        ],
        cwd=layout.package_root,
    )


def worktree_path(repo_root: Path, worktree_name: str) -> Path:
    return repo_root / ".worktrees" / worktree_name


def normalize_worktree_name(raw_name: str) -> str:
    name = raw_name.strip()
    if not name:
        raise SystemExit("[blueprint-harness] worktree name must not be empty")
    if Path(name).name != name or name in {".", ".."}:
        raise SystemExit(
            "[blueprint-harness] worktree name must be a single path segment; "
            "the helper always creates linked worktrees under `.worktrees/<name>`."
        )
    return name


def default_branch_name(worktree_name: str) -> str:
    return f"feat/{worktree_name}"


def branch_exists(repo_root: Path, branch: str) -> bool:
    return (
        subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"],
            cwd=repo_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    )


def print_failure_summary(failures: list[StepFailure]) -> int:
    if not failures:
        print("[blueprint-harness] validation summary: all requested steps passed")
        return 0

    print("[blueprint-harness] validation summary: failures detected", file=sys.stderr)
    for failure in failures:
        print(f"[blueprint-harness]   {failure.step}: {failure.detail}", file=sys.stderr)
    return 1


def executable_path(package_root: Path, exe_name: str) -> Path:
    return package_root / ".lake" / "build" / "bin" / exe_name


def ensure_prebuilt_executable(package_root: Path, exe_name: str) -> Path:
    path = executable_path(package_root, exe_name)
    if not path.exists():
        raise SystemExit(
            f"[blueprint-harness] missing prebuilt executable `{exe_name}` at {path}. "
            "Sync from the root worktree after building there, or rerun with `--allow-local-build`."
        )
    return path


def find_test_driver_binary(package_root: Path) -> Path | None:
    for candidate in ("verso-tests", "verso-blueprint-tests"):
        path = executable_path(package_root, candidate)
        if path.exists():
            return path
    return None


def build_examples(package_root: Path, examples: list[str]) -> None:
    run(lean_low_priority_command(package_root, "lake", "build", *examples), cwd=package_root)


def render_examples(package_root: Path, output_root: Path, examples: list[str], serial: bool) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    if serial:
        for example in examples:
            output_dir = output_root / example
            run(
                lean_low_priority_command(
                    package_root,
                    str(ensure_prebuilt_executable(package_root, example)),
                    "--output",
                    str(output_dir),
                ),
                cwd=package_root,
            )
        return

    procs: list[tuple[str, subprocess.Popen[bytes]]] = []
    try:
        for example in examples:
            output_dir = output_root / example
            output_dir.mkdir(parents=True, exist_ok=True)
            command = lean_low_priority_command(
                package_root,
                str(ensure_prebuilt_executable(package_root, example)),
                "--output",
                str(output_dir),
            )
            print(f"[blueprint-harness] launching {example} -> {output_dir}", flush=True)
            procs.append((example, subprocess.Popen(command, cwd=package_root)))

        failures: list[str] = []
        for example, proc in procs:
            if proc.wait() == 0:
                print(f"[blueprint-harness] finished {example}")
            else:
                failures.append(example)
        if failures:
            raise SystemExit(f"[blueprint-harness] example render failed: {', '.join(failures)}")
    finally:
        for _, proc in procs:
            if proc.poll() is None:
                proc.kill()


def command_generate(args: argparse.Namespace) -> int:
    layout = detect_harness_layout(Path(__file__))
    output_root = resolve_output_root(args.output_root, Path(__file__))
    examples = selected_examples(args.example)

    print(f"[blueprint-harness] package root: {layout.package_root}")
    if not getattr(args, "skip_sync", False):
        sync_root_worktree_lake(layout)
    use_local_build = should_use_local_build(layout, args.allow_local_build)
    if layout.in_linked_worktree:
        print(f"[blueprint-harness] linked worktree output root: {output_root}")
        if not use_local_build:
            print(
                "[blueprint-harness] using synced root executables; local Lake builds are disabled by default in linked worktrees"
            )
    else:
        print(f"[blueprint-harness] output root: {output_root}")

    if not args.skip_build and use_local_build:
        build_examples(layout.package_root, examples)
    elif not args.skip_build and not use_local_build:
        for example in examples:
            ensure_prebuilt_executable(layout.package_root, example)
    render_examples(layout.package_root, output_root, examples, args.serial)

    print("[blueprint-harness] generated sites:")
    for example in examples:
        print(output_root / example)
    return 0


def panel_regression_command(package_root: Path, site_dir: Path) -> list[str]:
    return [
        sys.executable,
        str(package_root / "test-projects" / "Noperthedron" / "check_blueprint_code_panels.py"),
        "--site-dir",
        str(site_dir),
    ]


def browser_test_command(package_root: Path, site_dir: Path, pytest_args: list[str]) -> list[str]:
    if shutil.which("uv"):
        command = [
            "env",
            "UV_CACHE_DIR=/tmp/verso-blueprint-uv-cache",
            "uv",
            "run",
            "--project",
            "browser-tests",
            "--extra",
            "test",
            "python",
            "-m",
            "pytest",
        ]
    else:
        command = [sys.executable, "-m", "pytest"]
    return [
        *command,
        "browser-tests",
        "-q",
        "--browser",
        "chromium",
        "--site-dir",
        str(site_dir),
        *pytest_args,
    ]


def command_validate(args: argparse.Namespace) -> int:
    layout = detect_harness_layout(Path(__file__))
    output_root = resolve_output_root(args.output_root, Path(__file__))
    examples = selected_examples(args.example)
    failures: list[StepFailure] = []

    print(f"[blueprint-harness] validation output root: {output_root}")
    sync_root_worktree_lake(layout)
    use_local_build = should_use_local_build(layout, args.allow_local_build)
    if args.run_lean_tests:
        if use_local_build:
            failure = run_capturing_failure(
                "lake test",
                lean_low_priority_command(layout.package_root, "lake", "test"),
                cwd=layout.package_root,
            )
            if failure is not None:
                failures.append(failure)
                if args.stop_on_first_failure:
                    return print_failure_summary(failures)
        else:
            test_driver = find_test_driver_binary(layout.package_root)
            if test_driver is None:
                failures.append(
                    StepFailure(
                        "lean tests",
                        "no prebuilt test driver found in synced root artifacts; rerun from the root checkout or use --allow-local-build",
                    )
                )
                if args.stop_on_first_failure:
                    return print_failure_summary(failures)
            else:
                failure = run_capturing_failure(
                    "lean tests",
                    lean_low_priority_command(layout.package_root, str(test_driver)),
                    cwd=layout.package_root,
                )
                if failure is not None:
                    failures.append(failure)
                    if args.stop_on_first_failure:
                        return print_failure_summary(failures)

    try:
        command_generate(
            argparse.Namespace(
                output_root=str(output_root),
                example=examples,
                skip_build=False,
                serial=args.serial,
                allow_local_build=args.allow_local_build,
                skip_sync=True,
            )
        )
    except SystemExit as err:
        failures.append(StepFailure("generate examples", str(err)))
        return print_failure_summary(failures)

    noperthedron_site = output_root / "noperthedron" / "html-multi"
    if "noperthedron" in examples and not args.skip_panel_regression:
        failure = run_capturing_failure(
            "panel regression",
            panel_regression_command(layout.package_root, noperthedron_site),
            cwd=layout.package_root,
        )
        if failure is not None:
            failures.append(failure)
            if args.stop_on_first_failure:
                return print_failure_summary(failures)

    if "noperthedron" in examples and not args.skip_browser_tests:
        failure = run_capturing_failure(
            "browser tests",
            browser_test_command(layout.package_root, noperthedron_site, args.pytest_arg),
            cwd=layout.package_root,
        )
        if failure is not None:
            failures.append(failure)
            if args.stop_on_first_failure:
                return print_failure_summary(failures)

    return print_failure_summary(failures)


def command_sync_root_lake(_: argparse.Namespace) -> int:
    layout = detect_harness_layout(Path(__file__))
    if not layout.in_linked_worktree:
        print("[blueprint-harness] root checkout detected; no worktree sync needed")
        return 0

    sync_root_worktree_lake(layout)
    print("[blueprint-harness] synced `.lake/` from root worktree")
    return 0


def command_create_worktree(args: argparse.Namespace) -> int:
    layout = detect_harness_layout(Path(__file__))
    worktree_name = normalize_worktree_name(args.name)
    destination = worktree_path(layout.repo_root, worktree_name)
    branch = args.branch or default_branch_name(worktree_name)
    base_ref = args.base

    if destination.exists():
        raise SystemExit(f"[blueprint-harness] worktree path already exists: {destination}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    if branch_exists(layout.repo_root, branch):
        command = ["git", "worktree", "add", str(destination), branch]
    else:
        command = ["git", "worktree", "add", "-b", branch, str(destination), base_ref]
    run(command, cwd=layout.repo_root)

    new_layout = detect_harness_layout(destination)
    if not args.skip_sync:
        sync_root_worktree_lake(new_layout)

    print(f"[blueprint-harness] worktree path: {destination}")
    print(f"[blueprint-harness] branch: {branch}")
    print(f"[blueprint-harness] artifact root: {new_layout.artifact_root}")
    return 0


def command_paths(_: argparse.Namespace) -> int:
    layout = detect_harness_layout(Path(__file__))
    noperthedron_site = canonical_example_site_dir("noperthedron", Path(__file__))
    noperthedron_site_resolved = default_example_site_dir("noperthedron", Path(__file__))
    spherepacking_site = canonical_example_site_dir("spherepackingblueprint", Path(__file__))
    spherepacking_site_resolved = default_example_site_dir("spherepackingblueprint", Path(__file__))
    print(f"package_root={layout.package_root}")
    print(f"repo_root={layout.repo_root}")
    print(f"worktree_name={layout.worktree_name or ''}")
    print(f"artifact_root={layout.artifact_root}")
    print(f"root_lake={layout.repo_root / '.lake'}")
    print(f"example_output_root={layout.example_output_root}")
    print(f"noperthedron_site={noperthedron_site}")
    print(f"noperthedron_site_resolved={noperthedron_site_resolved}")
    print(f"spherepackingblueprint_site={spherepacking_site}")
    print(f"spherepackingblueprint_site_resolved={spherepacking_site_resolved}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python3 -m script.blueprint_harness",
        description="Worktree-aware local harness for blueprint generation and validation.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser(
        "generate",
        help="Build the example blueprint sites.",
    )
    generate.add_argument("output_root", nargs="?", default=None)
    generate.add_argument(
        "--example",
        action="append",
        choices=EXAMPLES,
        help="Render only the selected example. Repeat to render more than one.",
    )
    generate.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip the shared lake build and only run the already-built executables.",
    )
    generate.add_argument(
        "--serial",
        action="store_true",
        help="Render examples serially instead of in parallel.",
    )
    generate.add_argument(
        "--allow-local-build",
        action="store_true",
        help="Permit `lake build` in a linked worktree instead of requiring synced root executables.",
    )
    generate.set_defaults(func=command_generate)

    validate = subparsers.add_parser(
        "validate",
        help="Generate example sites and run static/browser regressions.",
    )
    validate.add_argument("output_root", nargs="?", default=None)
    validate.add_argument(
        "--example",
        action="append",
        choices=EXAMPLES,
        help="Restrict site generation to the selected example. Repeat to select more.",
    )
    validate.add_argument(
        "--run-lean-tests",
        action="store_true",
        help="Also run Lean tests before site generation.",
    )
    validate.add_argument(
        "--skip-panel-regression",
        action="store_true",
        help="Skip the static Noperthedron code-panel regression check.",
    )
    validate.add_argument(
        "--skip-browser-tests",
        action="store_true",
        help="Skip the Playwright browser regression suite.",
    )
    validate.add_argument(
        "--serial",
        action="store_true",
        help="Render examples serially instead of in parallel.",
    )
    validate.add_argument(
        "--pytest-arg",
        action="append",
        default=[],
        help="Extra argument forwarded to pytest. Repeat for multiple arguments.",
    )
    validate.add_argument(
        "--allow-local-build",
        action="store_true",
        help="Permit `lake build` and `lake test` in a linked worktree instead of requiring synced root artifacts.",
    )
    validate.add_argument(
        "--stop-on-first-failure",
        action="store_true",
        help="Stop validation as soon as one phase fails instead of collecting later failures.",
    )
    validate.set_defaults(func=command_validate)

    sync_root_lake = subparsers.add_parser(
        "sync-root-lake",
        help="Sync `.lake/` from the root checkout into the current linked worktree.",
    )
    sync_root_lake.set_defaults(func=command_sync_root_lake)

    create_worktree = subparsers.add_parser(
        "create-worktree",
        help="Create a linked worktree under `.worktrees/<name>` and sync root artifacts into it.",
    )
    create_worktree.add_argument("name", help="Worktree directory name under `.worktrees/`.")
    create_worktree.add_argument(
        "--branch",
        default=None,
        help="Branch to attach to the new worktree. Defaults to `feat/<name>`.",
    )
    create_worktree.add_argument(
        "--base",
        default="main",
        help="Base ref used when creating a new branch. Ignored if `--branch` already exists.",
    )
    create_worktree.add_argument(
        "--skip-sync",
        action="store_true",
        help="Do not sync `.lake/` from the root checkout after creating the worktree.",
    )
    create_worktree.set_defaults(func=command_create_worktree)

    paths = subparsers.add_parser(
        "paths",
        help="Print canonical and resolved worktree-aware harness paths.",
    )
    paths.set_defaults(func=command_paths)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
