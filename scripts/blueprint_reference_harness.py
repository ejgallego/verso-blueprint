from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
import sys

from scripts.blueprint_harness_paths import detect_harness_layout, resolve_output_root
from scripts.blueprint_harness_projects import HarnessProject, load_projects_manifest, resolve_manifest_path
from scripts.blueprint_harness_references import (
    generate_in_repo_command_project,
    generate_git_project,
    output_dir_for,
    prepare_reference_edit_checkout,
    reference_prune_plan,
    site_dir_for,
    sync_reference_blueprints,
)
from scripts.blueprint_harness_utils import format_command, lean_low_priority_command, run
from scripts.blueprint_harness_worktrees import git_worktrees


@dataclass(frozen=True)
class StepFailure:
    step: str
    detail: str


def run_capturing_failure(step: str, command: list[str], *, cwd: Path) -> StepFailure | None:
    try:
        run(command, cwd=cwd)
        return None
    except subprocess.CalledProcessError as err:
        return StepFailure(step=step, detail=f"exit code {err.returncode}: {format_command(command)}")


def selected_projects(catalog: list[HarnessProject], values: list[str] | None) -> list[HarnessProject]:
    if not values:
        return list(catalog)
    by_id = {project.project_id: project for project in catalog}
    seen: set[str] = set()
    result: list[HarnessProject] = []
    for value in values:
        if value not in by_id:
            known = ", ".join(sorted(by_id))
            raise SystemExit(f"[blueprint-reference-harness] unknown project `{value}`; known projects: {known}")
        if value not in seen:
            result.append(by_id[value])
            seen.add(value)
    return result


def load_project_catalog(manifest_path: Path) -> list[HarnessProject]:
    try:
        return load_projects_manifest(manifest_path)
    except (FileNotFoundError, ValueError) as err:
        raise SystemExit(f"[blueprint-reference-harness] {err}") from err


def should_use_local_build(layout, allow_local_build: bool) -> bool:
    return (not layout.in_linked_worktree) or allow_local_build


def print_failure_summary(failures: list[StepFailure]) -> int:
    if not failures:
        print("[blueprint-reference-harness] validation summary: all requested steps passed")
        return 0

    print("[blueprint-reference-harness] validation summary: failures detected", file=sys.stderr)
    for failure in failures:
        print(f"[blueprint-reference-harness]   {failure.step}: {failure.detail}", file=sys.stderr)
    return 1


def executable_path(package_root: Path, exe_name: str) -> Path:
    return package_root / ".lake" / "build" / "bin" / exe_name


def ensure_prebuilt_executable(package_root: Path, exe_name: str) -> Path:
    path = executable_path(package_root, exe_name)
    if not path.exists():
        raise SystemExit(
            f"[blueprint-reference-harness] missing prebuilt executable `{exe_name}` at {path}. "
            "Refresh this worktree with `python3 -m scripts.blueprint_harness sync-root-lake` "
            "after building from the root checkout, or rerun with `--allow-local-build`."
        )
    return path


def find_test_driver_binary(package_root: Path) -> Path | None:
    for candidate in ("verso-tests", "verso-blueprint-tests"):
        path = executable_path(package_root, candidate)
        if path.exists():
            return path
    return None


def resolve_repo_relative_path(package_root: Path, path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return package_root / path


def build_in_repo_projects(package_root: Path, projects: list[HarnessProject]) -> None:
    targets = [project.build_target for project in projects if project.build_target is not None]
    if targets:
        run(lean_low_priority_command(package_root, "lake", "build", *targets), cwd=package_root)


def render_in_repo_projects(package_root: Path, output_root: Path, projects: list[HarnessProject], serial: bool) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    if serial:
        for project in projects:
            output_dir = output_dir_for(project, output_root)
            run(
                lean_low_priority_command(
                    package_root,
                    str(ensure_prebuilt_executable(package_root, project.generator or project.project_id)),
                    "--output",
                    str(output_dir),
                ),
                cwd=package_root,
            )
        return

    procs: list[tuple[str, subprocess.Popen[bytes]]] = []
    try:
        for project in projects:
            output_dir = output_dir_for(project, output_root)
            output_dir.mkdir(parents=True, exist_ok=True)
            command = lean_low_priority_command(
                package_root,
                str(ensure_prebuilt_executable(package_root, project.generator or project.project_id)),
                "--output",
                str(output_dir),
            )
            print(f"[blueprint-reference-harness] launching {project.project_id} -> {output_dir}", flush=True)
            procs.append((project.project_id, subprocess.Popen(command, cwd=package_root)))

        failures: list[str] = []
        for project_id, proc in procs:
            if proc.wait() == 0:
                print(f"[blueprint-reference-harness] finished {project_id}")
            else:
                failures.append(project_id)
        if failures:
            raise SystemExit(f"[blueprint-reference-harness] project render failed: {', '.join(failures)}")
    finally:
        for _, proc in procs:
            if proc.poll() is None:
                proc.kill()


def generate_projects(
    layout,
    output_root: Path,
    projects: list[HarnessProject],
    *,
    skip_build: bool,
    serial: bool,
    allow_local_build: bool,
) -> None:
    in_repo_projects = [project for project in projects if project.in_repo_example]
    in_repo_target_projects = [project for project in in_repo_projects if project.in_repo_target_project]
    in_repo_command_projects = [project for project in in_repo_projects if project.in_repo_command_project]
    git_projects = [project for project in projects if project.git_checkout]

    if in_repo_target_projects:
        print(f"[blueprint-reference-harness] package root: {layout.package_root}")
        use_local_build = should_use_local_build(layout, allow_local_build)
        if layout.in_linked_worktree:
            print(f"[blueprint-reference-harness] linked worktree output root: {output_root}")
            if not use_local_build:
                print(
                    "[blueprint-reference-harness] using the current worktree `.lake/`; "
                    "run `sync-root-lake` explicitly when you want to refresh from the root checkout"
                )
        else:
            print(f"[blueprint-reference-harness] output root: {output_root}")

        if not skip_build and use_local_build:
            build_in_repo_projects(layout.package_root, in_repo_target_projects)
        elif not skip_build and not use_local_build:
            for project in in_repo_target_projects:
                ensure_prebuilt_executable(layout.package_root, project.generator or project.project_id)
        render_in_repo_projects(layout.package_root, output_root, in_repo_target_projects, serial)

    if in_repo_command_projects:
        print(f"[blueprint-reference-harness] package root: {layout.package_root}")
        if layout.in_linked_worktree:
            print(f"[blueprint-reference-harness] linked worktree output root: {output_root}")
        else:
            print(f"[blueprint-reference-harness] output root: {output_root}")
        for project in in_repo_command_projects:
            print(f"[blueprint-reference-harness] in-repo project: {project.project_id} ({project.project_root})")
            generate_in_repo_command_project(layout, output_root, project, skip_build=skip_build)

    for project in git_projects:
        print(f"[blueprint-reference-harness] reference checkout: {project.project_id}")
        generate_git_project(layout, output_root, project, skip_build=skip_build)


def panel_regression_command(package_root: Path, project: HarnessProject, site_dir: Path) -> list[str]:
    return [
        sys.executable,
        str(resolve_repo_relative_path(package_root, project.panel_regression_script or "")),
        "--site-dir",
        str(site_dir),
    ]


def browser_test_command(package_root: Path, project: HarnessProject, site_dir: Path, pytest_args: list[str]) -> list[str]:
    tests_path = resolve_repo_relative_path(package_root, project.browser_tests_path or "")
    if shutil.which("uv"):
        command = [
            "env",
            "UV_CACHE_DIR=/tmp/verso-blueprint-uv-cache",
            "uv",
            "run",
            "--project",
            str(tests_path),
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
        str(tests_path),
        "-q",
        "--browser",
        "chromium",
        "--site-dir",
        str(site_dir),
        *pytest_args,
    ]


def command_generate(args: argparse.Namespace) -> int:
    layout = detect_harness_layout(Path(__file__))
    output_root = resolve_output_root(args.output_root, Path(__file__))
    manifest_path = resolve_manifest_path(args.manifest, layout.package_root)
    projects = selected_projects(load_project_catalog(manifest_path), args.project)

    generate_projects(
        layout,
        output_root,
        projects,
        skip_build=args.skip_build,
        serial=args.serial,
        allow_local_build=args.allow_local_build,
    )

    print(f"[blueprint-reference-harness] project manifest: {manifest_path}")
    print("[blueprint-reference-harness] generated project outputs:")
    for project in projects:
        print(output_dir_for(project, output_root))
    return 0


def command_validate(args: argparse.Namespace) -> int:
    layout = detect_harness_layout(Path(__file__))
    output_root = resolve_output_root(args.output_root, Path(__file__))
    manifest_path = resolve_manifest_path(args.manifest, layout.package_root)
    projects = selected_projects(load_project_catalog(manifest_path), args.project)
    failures: list[StepFailure] = []

    print(f"[blueprint-reference-harness] validation output root: {output_root}")
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
                        "no prebuilt test driver found in the current worktree `.lake/`; "
                        "run `python3 -m scripts.blueprint_harness sync-root-lake` after "
                        "building from the root checkout, or use `--allow-local-build`",
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
        generate_projects(
            layout,
            output_root,
            projects,
            skip_build=False,
            serial=args.serial,
            allow_local_build=args.allow_local_build,
        )
    except SystemExit as err:
        failures.append(StepFailure("generate projects", str(err)))
        return print_failure_summary(failures)

    for project in projects:
        site_dir = site_dir_for(project, output_root)
        if project.panel_regression_script is not None and not args.skip_panel_regression:
            failure = run_capturing_failure(
                f"{project.project_id} panel regression",
                panel_regression_command(layout.package_root, project, site_dir),
                cwd=layout.package_root,
            )
            if failure is not None:
                failures.append(failure)
                if args.stop_on_first_failure:
                    return print_failure_summary(failures)

        if project.browser_tests_path is not None and not args.skip_browser_tests:
            failure = run_capturing_failure(
                f"{project.project_id} browser tests",
                browser_test_command(layout.package_root, project, site_dir, args.pytest_arg),
                cwd=layout.package_root,
            )
            if failure is not None:
                failures.append(failure)
                if args.stop_on_first_failure:
                    return print_failure_summary(failures)

    return print_failure_summary(failures)


def command_projects(args: argparse.Namespace) -> int:
    layout = detect_harness_layout(Path(__file__))
    manifest_path = resolve_manifest_path(args.manifest, layout.package_root)
    projects = load_project_catalog(manifest_path)
    print(f"project_manifest={manifest_path}")
    for project in projects:
        if project.in_repo_example:
            source = f"in_repo:{project.project_root}"
        else:
            source = f"git:{project.repository}@{project.ref}"
        validations: list[str] = []
        if project.panel_regression_script is not None:
            validations.append("panel")
        if project.browser_tests_path is not None:
            validations.append("browser")
        validation_text = ",".join(validations) if validations else "none"
        print(f"{project.project_id}\tsource={source}\tvalidations={validation_text}")
    return 0


def command_reference_sync(args: argparse.Namespace) -> int:
    layout = detect_harness_layout(Path(__file__))
    manifest_path = resolve_manifest_path(args.manifest, layout.package_root)
    projects = selected_projects(load_project_catalog(manifest_path), args.project)
    sync_reference_blueprints(
        layout,
        projects,
        warm_build=not args.skip_build,
        prepare_local_checkout=not args.skip_local_checkout,
    )
    print(f"[blueprint-reference-harness] reference cache root: {layout.reference_project_cache_root}")
    print(f"[blueprint-reference-harness] reference checkout root: {layout.reference_project_checkout_root}")
    return 0


def command_reference_edit(args: argparse.Namespace) -> int:
    layout = detect_harness_layout(Path(__file__))
    manifest_path = resolve_manifest_path(args.manifest, layout.package_root)
    project = selected_projects(load_project_catalog(manifest_path), [args.project])[0]
    edit_dir, branch, base_ref = prepare_reference_edit_checkout(
        layout,
        project,
        branch=args.branch,
        base_ref=args.base,
    )
    print(f"[blueprint-reference-harness] editable reference checkout: {edit_dir}")
    print(f"[blueprint-reference-harness] branch: {branch}")
    print(f"[blueprint-reference-harness] base ref: {base_ref}")
    print(
        "[blueprint-reference-harness] note: editable reference checkouts are separate from the "
        "disposable validation clones used by `sync` and `generate`."
    )
    return 0


def command_reference_prune(args: argparse.Namespace) -> int:
    layout = detect_harness_layout(Path(__file__))
    manifest_path = resolve_manifest_path(args.manifest, layout.package_root)
    projects = load_project_catalog(manifest_path)
    active_names = {worktree.name for worktree in git_worktrees(layout.repo_root)}
    project_ids = {project.project_id for project in projects if project.git_checkout}
    removals = reference_prune_plan(
        active_names,
        project_ids,
        layout.reference_project_cache_root,
        layout.reference_project_root / "by-worktree",
    )
    if not removals:
        print("[blueprint-reference-harness] reference prune: no stale cached checkouts found")
        return 0
    for path in removals:
        print(path)
    if args.dry_run:
        return 0
    for path in removals:
        shutil.rmtree(path)
    print(f"[blueprint-reference-harness] reference prune: removed {len(removals)} path(s)")
    return 0


def add_output_root_argument(command_parser: argparse.ArgumentParser) -> None:
    command_parser.add_argument("output_root", nargs="?", default=None)


def add_project_selection_argument(
    command_parser: argparse.ArgumentParser,
    *,
    help_text: str,
    include_example_alias: bool = True,
) -> None:
    command_parser.add_argument(
        "--project",
        *(("--example",) if include_example_alias else ()),
        dest="project",
        action="append",
        help=help_text,
    )


def add_manifest_argument(command_parser: argparse.ArgumentParser) -> None:
    command_parser.add_argument(
        "--manifest",
        default=None,
        help="Path to the project manifest. Defaults to tests/harness/projects.json.",
    )


def add_serial_argument(command_parser: argparse.ArgumentParser) -> None:
    command_parser.add_argument(
        "--serial",
        action="store_true",
        help="Render selected projects serially instead of in parallel where supported.",
    )


def add_allow_local_build_argument(command_parser: argparse.ArgumentParser, *, help_text: str) -> None:
    command_parser.add_argument(
        "--allow-local-build",
        action="store_true",
        help=help_text,
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
