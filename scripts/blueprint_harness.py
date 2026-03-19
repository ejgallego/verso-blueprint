from __future__ import annotations

import argparse
from dataclasses import dataclass
import shutil
import subprocess
import sys
from pathlib import Path

from scripts.blueprint_harness_paths import canonical_example_site_dir, detect_harness_layout, resolve_output_root
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
from scripts.blueprint_harness_worktrees import (
    GitWorktree,
    git_worktrees,
    resolve_worktree_name,
    sync_worktree_registry,
    update_worktree_record,
    worktree_record_map,
)


@dataclass(frozen=True)
class StepFailure:
    step: str
    detail: str


@dataclass(frozen=True)
class RefSyncStatus:
    local_ref: str
    upstream_ref: str
    local_oid: str | None
    upstream_oid: str | None
    relationship: str


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
            raise SystemExit(f"[blueprint-harness] unknown project `{value}`; known projects: {known}")
        if value not in seen:
            result.append(by_id[value])
            seen.add(value)
    return result


def load_project_catalog(manifest_path: Path) -> list[HarnessProject]:
    try:
        return load_projects_manifest(manifest_path)
    except (FileNotFoundError, ValueError) as err:
        raise SystemExit(f"[blueprint-harness] {err}") from err

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


def create_worktree_sync_policy(args: argparse.Namespace) -> tuple[bool, bool]:
    return (args.skip_sync or args.lightweight, args.skip_reference_sync or args.lightweight)


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
            print(f"[blueprint-harness] launching {project.project_id} -> {output_dir}", flush=True)
            procs.append((project.project_id, subprocess.Popen(command, cwd=package_root)))

        failures: list[str] = []
        for project_id, proc in procs:
            if proc.wait() == 0:
                print(f"[blueprint-harness] finished {project_id}")
            else:
                failures.append(project_id)
        if failures:
            raise SystemExit(f"[blueprint-harness] project render failed: {', '.join(failures)}")
    finally:
        for _, proc in procs:
            if proc.poll() is None:
                proc.kill()


def preferred_main_ref(repo_root: Path) -> str:
    if (
        subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", "refs/remotes/origin/main"],
            cwd=repo_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    ):
        return "origin/main"
    return "main"


def current_branch_name(repo_root: Path) -> str | None:
    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    return branch or None


def ref_oid(repo_root: Path, ref: str) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", ref],
        cwd=repo_root,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    oid = result.stdout.strip()
    return oid or None


def ref_sync_status(repo_root: Path, local_ref: str, upstream_ref: str) -> RefSyncStatus:
    local_oid = ref_oid(repo_root, local_ref)
    upstream_oid = ref_oid(repo_root, upstream_ref)

    if local_oid is None:
        relationship = "missing_local"
    elif upstream_oid is None:
        relationship = "missing_upstream"
    elif local_oid == upstream_oid:
        relationship = "in_sync"
    elif (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", local_ref, upstream_ref],
            cwd=repo_root,
            check=False,
        ).returncode
        == 0
    ):
        relationship = "behind"
    elif (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", upstream_ref, local_ref],
            cwd=repo_root,
            check=False,
        ).returncode
        == 0
    ):
        relationship = "ahead"
    else:
        relationship = "diverged"

    return RefSyncStatus(
        local_ref=local_ref,
        upstream_ref=upstream_ref,
        local_oid=local_oid,
        upstream_oid=upstream_oid,
        relationship=relationship,
    )


def main_sync_status(repo_root: Path) -> RefSyncStatus:
    upstream_ref = preferred_main_ref(repo_root)
    return ref_sync_status(repo_root, "main", upstream_ref)


def is_ancestor(repo_root: Path, ancestor: str, descendant: str) -> bool:
    return (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            cwd=repo_root,
            check=False,
        ).returncode
        == 0
    )


def resolve_create_worktree_base(layout, requested_base: str | None) -> str:
    preferred_base = preferred_main_ref(layout.repo_root)
    if requested_base is None:
        requested_base = preferred_base

    if requested_base == "main" and preferred_base != "main":
        status = main_sync_status(layout.repo_root)
        if status.relationship != "in_sync":
            raise SystemExit(
                f"[blueprint-harness] local `main` is {status.relationship} relative to `{status.upstream_ref}`; "
                "refusing to use local `main` as the worktree base. Rebase local `main` first or pass "
                f"`--base {status.upstream_ref}` explicitly."
            )
    return requested_base


def ref_merged_into_main(repo_root: Path, ref: str) -> bool:
    return is_ancestor(repo_root, ref, preferred_main_ref(repo_root))


def merged_clean_worktree_candidates(repo_root: Path, current_path: Path) -> list[tuple[str, Path, str]]:
    candidates: list[tuple[str, Path, str]] = []
    for worktree in git_worktrees(repo_root):
        if worktree.root_checkout or worktree.path.resolve() == current_path.resolve():
            continue
        if worktree.branch is None or worktree.branch == "main":
            continue
        if not ref_merged_into_main(repo_root, worktree.branch):
            continue
        status = subprocess.run(
            ["git", "status", "--short"],
            cwd=worktree.path,
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
        if status:
            continue
        candidates.append((worktree.name, worktree.path, worktree.branch))
    return candidates


def git_worktree_map(repo_root: Path) -> dict[str, GitWorktree]:
    return {worktree.name: worktree for worktree in git_worktrees(repo_root)}


def local_branch_ref(repo_root: Path, branch: str) -> str | None:
    ref = f"refs/heads/{branch}"
    if ref_oid(repo_root, ref) is None:
        return None
    return branch


def origin_branch_exists(repo_root: Path, branch: str) -> bool:
    return (
        subprocess.run(
            ["git", "ls-remote", "--exit-code", "--heads", "origin", branch],
            cwd=repo_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    )


def branch_worktrees(repo_root: Path, branch: str) -> list[GitWorktree]:
    return [worktree for worktree in git_worktrees(repo_root) if worktree.branch == branch]


def worktree_is_clean(path: Path) -> bool:
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=path,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    return not status


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
        print(f"[blueprint-harness] package root: {layout.package_root}")
        use_local_build = should_use_local_build(layout, allow_local_build)
        if layout.in_linked_worktree:
            print(f"[blueprint-harness] linked worktree output root: {output_root}")
            if not use_local_build:
                print(
                    "[blueprint-harness] using the current worktree `.lake/`; run `sync-root-lake` explicitly when you want to refresh from the root checkout"
                )
        else:
            print(f"[blueprint-harness] output root: {output_root}")

        if not skip_build and use_local_build:
            build_in_repo_projects(layout.package_root, in_repo_target_projects)
        elif not skip_build and not use_local_build:
            for project in in_repo_target_projects:
                ensure_prebuilt_executable(layout.package_root, project.generator or project.project_id)
        render_in_repo_projects(layout.package_root, output_root, in_repo_target_projects, serial)

    if in_repo_command_projects:
        print(f"[blueprint-harness] package root: {layout.package_root}")
        if layout.in_linked_worktree:
            print(f"[blueprint-harness] linked worktree output root: {output_root}")
        else:
            print(f"[blueprint-harness] output root: {output_root}")
        for project in in_repo_command_projects:
            print(f"[blueprint-harness] in-repo project: {project.project_id} ({project.project_root})")
            generate_in_repo_command_project(layout, output_root, project, skip_build=skip_build)

    for project in git_projects:
        print(f"[blueprint-harness] reference checkout: {project.project_id}")
        generate_git_project(layout, output_root, project, skip_build=skip_build)


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

    print(f"[blueprint-harness] project manifest: {manifest_path}")
    print("[blueprint-harness] generated project outputs:")
    for project in projects:
        print(output_dir_for(project, output_root))
    return 0


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


def command_validate(args: argparse.Namespace) -> int:
    layout = detect_harness_layout(Path(__file__))
    output_root = resolve_output_root(args.output_root, Path(__file__))
    manifest_path = resolve_manifest_path(args.manifest, layout.package_root)
    projects = selected_projects(load_project_catalog(manifest_path), args.project)
    failures: list[StepFailure] = []

    print(f"[blueprint-harness] validation output root: {output_root}")
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
    base_ref = resolve_create_worktree_base(layout, args.base)
    skip_sync, skip_reference_sync = create_worktree_sync_policy(args)

    if destination.exists():
        raise SystemExit(f"[blueprint-harness] worktree path already exists: {destination}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    if branch_exists(layout.repo_root, branch):
        command = ["git", "worktree", "add", str(destination), branch]
    else:
        command = ["git", "worktree", "add", "-b", branch, str(destination), base_ref]
    run(command, cwd=layout.repo_root)

    new_layout = detect_harness_layout(destination)
    if not skip_sync:
        sync_root_worktree_lake(new_layout)
    if not skip_reference_sync:
        manifest_path = resolve_manifest_path(None, new_layout.package_root)
        projects = load_project_catalog(manifest_path)
        sync_reference_blueprints(new_layout, projects, warm_build=True, prepare_local_checkout=True)

    print(f"[blueprint-harness] worktree path: {destination}")
    print(f"[blueprint-harness] branch: {branch}")
    print(f"[blueprint-harness] base ref: {base_ref}")
    print(f"[blueprint-harness] artifact root: {new_layout.artifact_root}")
    return 0


def command_main_status(args: argparse.Namespace) -> int:
    layout = detect_harness_layout(Path(__file__))
    status = main_sync_status(layout.repo_root)
    print(f"current_branch={current_branch_name(layout.repo_root) or ''}")
    print(f"preferred_main_ref={status.upstream_ref}")
    print(f"main_oid={status.local_oid or ''}")
    print(f"{status.upstream_ref}_oid={status.upstream_oid or ''}")
    print(f"relationship={status.relationship}")
    if args.require_sync and status.relationship != "in_sync":
        print(
            f"[blueprint-harness] local `main` is {status.relationship} relative to `{status.upstream_ref}`",
            file=sys.stderr,
        )
        return 1
    return 0


def cleanup_source_branch(layout, branch: str, *, delete_remote: bool) -> None:
    worktrees = [worktree for worktree in branch_worktrees(layout.repo_root, branch) if not worktree.root_checkout]
    if len(worktrees) > 1:
        names = ", ".join(sorted(worktree.name for worktree in worktrees))
        raise SystemExit(
            f"[blueprint-harness] branch `{branch}` is checked out in multiple linked worktrees: {names}; "
            "clean them up manually."
        )
    if worktrees:
        worktree = worktrees[0]
        if not worktree_is_clean(worktree.path):
            raise SystemExit(
                f"[blueprint-harness] linked worktree `{worktree.name}` for branch `{branch}` has local modifications"
            )
        run(["git", "worktree", "remove", str(worktree.path)], cwd=layout.repo_root)
        print(f"[blueprint-harness] removed worktree `{worktree.name}`")

    if local_branch_ref(layout.repo_root, branch) is not None:
        run(["git", "branch", "-d", branch], cwd=layout.repo_root)
        print(f"[blueprint-harness] deleted local branch `{branch}`")

    if delete_remote and origin_branch_exists(layout.repo_root, branch):
        run(["git", "push", "origin", "--delete", branch], cwd=layout.repo_root)
        print(f"[blueprint-harness] deleted remote branch `{branch}`")


def command_land_main(args: argparse.Namespace) -> int:
    layout = detect_harness_layout(Path(__file__))
    if layout.in_linked_worktree:
        raise SystemExit("[blueprint-harness] run `land-main` from the root checkout, not from a linked worktree")
    if current_branch_name(layout.repo_root) != "main":
        raise SystemExit("[blueprint-harness] root checkout must be on `main` before landing changes")
    if not worktree_is_clean(layout.package_root):
        raise SystemExit("[blueprint-harness] root checkout has local modifications; commit or stash them first")

    status = main_sync_status(layout.repo_root)
    if status.relationship != "in_sync":
        raise SystemExit(
            f"[blueprint-harness] local `main` is {status.relationship} relative to `{status.upstream_ref}`; "
            "sync `main` before landing additional changes"
        )

    source_ref = args.source
    if ref_oid(layout.repo_root, source_ref) is None:
        raise SystemExit(f"[blueprint-harness] unknown source ref `{source_ref}`")
    if source_ref in {"main", status.upstream_ref}:
        raise SystemExit("[blueprint-harness] source ref must not be `main` itself")
    if not is_ancestor(layout.repo_root, "main", source_ref):
        raise SystemExit(
            f"[blueprint-harness] source ref `{source_ref}` is not a fast-forward descendant of local `main`; "
            "rebase or merge it first"
        )

    run(["git", "merge", "--ff-only", source_ref], cwd=layout.repo_root)
    print(f"[blueprint-harness] landed `{source_ref}` onto local `main`")

    if preferred_main_ref(layout.repo_root) == "origin/main" and not args.no_push:
        run(["git", "push", "origin", "main"], cwd=layout.repo_root)
        print("[blueprint-harness] pushed `main` to origin")

    if args.cleanup:
        cleanup_branch = None
        if local_branch_ref(layout.repo_root, source_ref) is not None:
            cleanup_branch = source_ref
        elif source_ref.startswith("origin/"):
            cleanup_branch = source_ref.removeprefix("origin/")

        if cleanup_branch is None:
            print(
                "[blueprint-harness] cleanup skipped: source ref is not a branch name tracked locally or under origin"
            )
        elif cleanup_branch == "main":
            print("[blueprint-harness] cleanup skipped: refusing to clean up `main`")
        else:
            cleanup_source_branch(layout, cleanup_branch, delete_remote=not args.keep_remote)

    return 0


def command_paths(_: argparse.Namespace) -> int:
    layout = detect_harness_layout(Path(__file__))
    manifest_path = resolve_manifest_path(None, layout.package_root)
    projects = load_project_catalog(manifest_path)
    print(f"package_root={layout.package_root}")
    print(f"repo_root={layout.repo_root}")
    print(f"worktree_name={layout.worktree_name or ''}")
    print(f"artifact_root={layout.artifact_root}")
    print(f"project_manifest={resolve_manifest_path(None, layout.package_root)}")
    print("local_override_strategy=ephemeral_lakefile_rewrite")
    print(f"preferred_main_ref={preferred_main_ref(layout.repo_root)}")
    print(f"root_lake={layout.repo_root / '.lake'}")
    print(f"reference_output_root={layout.reference_output_root}")
    print(f"reference_cache_root={layout.reference_project_cache_root}")
    print(f"reference_checkout_root={layout.reference_project_checkout_root}")
    print(f"reference_edit_root={layout.reference_project_edit_root}")
    for project in projects:
        canonical_site = canonical_example_site_dir(project.project_id, Path(__file__))
        print(f"{project.project_id}_site={canonical_site}")
    return 0


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
    print(f"[blueprint-harness] reference cache root: {layout.reference_project_cache_root}")
    print(f"[blueprint-harness] reference checkout root: {layout.reference_project_checkout_root}")
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
    print(f"[blueprint-harness] editable reference checkout: {edit_dir}")
    print(f"[blueprint-harness] branch: {branch}")
    print(f"[blueprint-harness] base ref: {base_ref}")
    print(
        "[blueprint-harness] note: editable reference checkouts are separate from the "
        "disposable validation clones used by `reference-sync` and `generate`."
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
        print("[blueprint-harness] reference prune: no stale cached checkouts found")
        return 0
    for path in removals:
        print(path)
    if args.dry_run:
        return 0
    for path in removals:
        shutil.rmtree(path)
    print(f"[blueprint-harness] reference prune: removed {len(removals)} path(s)")
    return 0


def command_worktree_prune_candidates(_: argparse.Namespace) -> int:
    layout = detect_harness_layout(Path(__file__))
    candidates = merged_clean_worktree_candidates(layout.repo_root, layout.package_root)
    if not candidates:
        print("[blueprint-harness] worktree prune candidates: none")
        return 0
    for name, path, branch in candidates:
        print(f"{name}\tbranch={branch}\tpath={path}")
    return 0


def command_worktree_retire(args: argparse.Namespace) -> int:
    layout = detect_harness_layout(Path(__file__))
    name = resolve_worktree_name(layout.worktree_name, args.name)
    worktrees = git_worktree_map(layout.repo_root)
    if name not in worktrees:
        raise SystemExit(f"[blueprint-harness] unknown worktree `{name}`")
    worktree = worktrees[name]
    path = worktree.path
    branch = worktree.branch
    if worktree.root_checkout:
        raise SystemExit("[blueprint-harness] cannot retire the root checkout")
    if path.resolve() == layout.package_root.resolve():
        raise SystemExit("[blueprint-harness] cannot retire the current active worktree from inside itself")
    if branch == "main":
        raise SystemExit("[blueprint-harness] cannot retire a linked worktree attached to `main`")
    merge_subject = branch or worktree.head
    if not ref_merged_into_main(layout.repo_root, merge_subject):
        if branch is None:
            raise SystemExit(
                f"[blueprint-harness] detached worktree `{name}` is at `{worktree.head}` "
                "which is not merged into the preferred main ref"
            )
        raise SystemExit(f"[blueprint-harness] branch `{branch}` is not merged into the preferred main ref")
    if not worktree_is_clean(path):
        raise SystemExit(f"[blueprint-harness] worktree `{name}` has local modifications")

    print(f"name={name}")
    print(f"path={path}")
    print(f"branch={branch or ''}")
    print(f"head={worktree.head}")
    if args.dry_run:
        return 0

    run(["git", "worktree", "remove", str(path)], cwd=layout.repo_root)
    if branch is not None:
        run(["git", "branch", "-d", branch], cwd=layout.repo_root)

    manifest_path = resolve_manifest_path(None, layout.package_root)
    projects = load_project_catalog(manifest_path)
    active_names = {worktree.name for worktree in git_worktrees(layout.repo_root)}
    project_ids = {project.project_id for project in projects if project.git_checkout}
    removals = reference_prune_plan(
        active_names,
        project_ids,
        layout.reference_project_cache_root,
        layout.reference_project_root / "by-worktree",
    )
    for stale_path in removals:
        shutil.rmtree(stale_path)
    print(f"[blueprint-harness] retired worktree `{name}`")
    if removals:
        print(f"[blueprint-harness] removed {len(removals)} stale reference path(s)")
    return 0


def command_worktree_sync(_: argparse.Namespace) -> int:
    layout = detect_harness_layout(Path(__file__))
    records, registry = sync_worktree_registry(layout.repo_root)
    print(f"worktree_registry={registry}")
    for record in records:
        print(f"{record.name}\tbranch={record.branch or ''}\tstatus={record.status}\towner={record.owner or ''}")
    return 0


def command_worktree_list(_: argparse.Namespace) -> int:
    layout = detect_harness_layout(Path(__file__))
    records, registry = sync_worktree_registry(layout.repo_root)
    print(f"worktree_registry={registry}")
    for record in records:
        scope = ",".join(record.write_scope) if record.write_scope else ""
        print(
            f"{record.name}\tbranch={record.branch or ''}\tstatus={record.status}\t"
            f"owner={record.owner or ''}\tissue={record.issue or ''}\tscope={scope}"
        )
    return 0


def command_worktree_status(args: argparse.Namespace) -> int:
    layout = detect_harness_layout(Path(__file__))
    name = resolve_worktree_name(layout.worktree_name, args.name)
    records, registry = worktree_record_map(layout.repo_root)
    if name not in records:
        raise SystemExit(f"[blueprint-harness] unknown worktree `{name}`")
    record = records[name]
    print(f"worktree_registry={registry}")
    print(f"name={record.name}")
    print(f"path={record.path}")
    print(f"branch={record.branch or ''}")
    print(f"status={record.status}")
    print(f"owner={record.owner or ''}")
    print(f"issue={record.issue or ''}")
    print(f"task_id={record.task_id or ''}")
    print(f"summary={record.summary or ''}")
    print(f"write_scope={','.join(record.write_scope)}")
    print(f"updated_at={record.updated_at or ''}")
    print(f"last_seen_at={record.last_seen_at or ''}")
    return 0


def command_worktree_claim(args: argparse.Namespace) -> int:
    layout = detect_harness_layout(Path(__file__))
    name = resolve_worktree_name(layout.worktree_name, args.name)
    record, record_path, registry = update_worktree_record(
        layout.repo_root,
        name,
        owner=args.owner,
        issue=args.issue,
        task_id=args.task_id,
        summary=args.summary,
        status=args.status,
        write_scope=args.scope,
    )
    print(f"worktree_registry={registry}")
    print(f"worktree_record={record_path}")
    print(f"name={record.name}")
    print(f"status={record.status}")
    print(f"owner={record.owner or ''}")
    print(f"summary={record.summary or ''}")
    print(f"write_scope={','.join(record.write_scope)}")
    return 0


def command_worktree_release(args: argparse.Namespace) -> int:
    layout = detect_harness_layout(Path(__file__))
    name = resolve_worktree_name(layout.worktree_name, args.name)
    record, record_path, registry = update_worktree_record(
        layout.repo_root,
        name,
        status=args.status,
        summary=args.summary,
        write_scope=[],
    )
    print(f"worktree_registry={registry}")
    print(f"worktree_record={record_path}")
    print(f"name={record.name}")
    print(f"status={record.status}")
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


def add_optional_worktree_name_argument(command_parser: argparse.ArgumentParser) -> None:
    command_parser.add_argument("name", nargs="?", default=None, help="Worktree name. Defaults to the current worktree.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python3 -m scripts.blueprint_harness",
        description="Worktree-aware local harness for blueprint project generation and validation.",
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

    sync_root_lake = subparsers.add_parser(
        "sync-root-lake",
        help="Sync `.lake/` from the root checkout into the current linked worktree.",
    )
    sync_root_lake.set_defaults(func=command_sync_root_lake)

    main_status = subparsers.add_parser(
        "main-status",
        help="Show whether local `main` is in sync with the preferred main ref.",
    )
    main_status.add_argument(
        "--require-sync",
        action="store_true",
        help="Exit nonzero when local `main` is not in sync with the preferred main ref.",
    )
    main_status.set_defaults(func=command_main_status)

    land_main = subparsers.add_parser(
        "land-main",
        help="Fast-forward land one reviewed source ref onto root `main`, optionally push, and clean up the source branch.",
    )
    land_main.add_argument("source", help="Source ref to land onto `main`. This must be a fast-forward descendant of local `main`.")
    land_main.add_argument(
        "--no-push",
        action="store_true",
        help="Update local `main` but do not push `origin/main` afterward.",
    )
    land_main.add_argument(
        "--cleanup",
        action="store_true",
        help="After landing, remove the source worktree and delete the source branch when it can be identified safely.",
    )
    land_main.add_argument(
        "--keep-remote",
        action="store_true",
        help="With `--cleanup`, keep the remote source branch instead of deleting it.",
    )
    land_main.set_defaults(func=command_land_main)

    create_worktree = subparsers.add_parser(
        "create-worktree",
        help=(
            "Create a linked worktree under `.worktrees/<name>`, then by default "
            "sync the root `.lake/` and warm the reference blueprint clones."
        ),
    )
    create_worktree.add_argument("name", help="Worktree directory name under `.worktrees/`.")
    create_worktree.add_argument(
        "--branch",
        default=None,
        help="Branch to attach to the new worktree. Defaults to `feat/<name>`.",
    )
    create_worktree.add_argument(
        "--base",
        default=None,
        help="Base ref used when creating a new branch. Defaults to `origin/main` when available, else `main`.",
    )
    create_worktree.add_argument(
        "--skip-sync",
        action="store_true",
        help="Do not sync `.lake/` from the root checkout after creating the worktree.",
    )
    create_worktree.add_argument(
        "--skip-reference-sync",
        action="store_true",
        help="Do not warm the shared and per-worktree reference blueprint clones after creating the worktree.",
    )
    create_worktree.add_argument(
        "--lightweight",
        action="store_true",
        help="Create only the git worktree and skip both `.lake/` sync and reference-cache warm-up.",
    )
    create_worktree.set_defaults(func=command_create_worktree)

    projects = subparsers.add_parser(
        "projects",
        help="List the configured harness projects from the active manifest.",
    )
    add_manifest_argument(projects)
    projects.set_defaults(func=command_projects)

    reference_sync = subparsers.add_parser(
        "reference-sync",
        help="Warm shared reference blueprint caches and prepare local clones for the current checkout.",
    )
    add_manifest_argument(reference_sync)
    add_project_selection_argument(
        reference_sync,
        help_text="Restrict sync to the selected project. Repeat to select more.",
        include_example_alias=False,
    )
    reference_sync.add_argument(
        "--skip-build",
        action="store_true",
        help="Update and clone the reference projects without warming their build artifacts.",
    )
    reference_sync.add_argument(
        "--skip-local-checkout",
        action="store_true",
        help="Warm only the shared cache checkout and skip preparing the current checkout's local clones.",
    )
    reference_sync.set_defaults(func=command_reference_sync)

    reference_edit = subparsers.add_parser(
        "reference-edit",
        help="Prepare or reuse one editable external reference checkout for manual changes.",
    )
    add_manifest_argument(reference_edit)
    reference_edit.add_argument("project", help="External git-checkout project id to open for editing.")
    reference_edit.add_argument(
        "--branch",
        default=None,
        help="Editable branch name. Defaults to `wip/<project-id>`.",
    )
    reference_edit.add_argument(
        "--base",
        default=None,
        help="Base ref used when creating the editable branch. Defaults to `origin/<project-ref>`.",
    )
    reference_edit.set_defaults(func=command_reference_edit)

    reference_prune = subparsers.add_parser(
        "reference-prune",
        help="Remove stale harness-managed reference blueprint caches and checkout clones.",
    )
    add_manifest_argument(reference_prune)
    reference_prune.add_argument(
        "--dry-run",
        action="store_true",
        help="List stale paths without deleting them.",
    )
    reference_prune.set_defaults(func=command_reference_prune)

    worktree_prune_candidates = subparsers.add_parser(
        "worktree-prune-candidates",
        help="List merged clean linked worktrees that are good prune candidates.",
    )
    worktree_prune_candidates.set_defaults(func=command_worktree_prune_candidates)

    worktree_retire = subparsers.add_parser(
        "worktree-retire",
        help="Retire one merged clean linked worktree and prune its stale reference clones.",
    )
    add_optional_worktree_name_argument(worktree_retire)
    worktree_retire.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the target worktree without deleting it.",
    )
    worktree_retire.set_defaults(func=command_worktree_retire)

    worktree_sync = subparsers.add_parser(
        "worktree-sync",
        help="Sync local worktree coordination metadata under .worktrees/.",
    )
    worktree_sync.set_defaults(func=command_worktree_sync)

    worktree_list = subparsers.add_parser(
        "worktree-list",
        help="List local worktree coordination metadata.",
    )
    worktree_list.set_defaults(func=command_worktree_list)

    worktree_status = subparsers.add_parser(
        "worktree-status",
        help="Show local coordination metadata for one worktree.",
    )
    add_optional_worktree_name_argument(worktree_status)
    worktree_status.set_defaults(func=command_worktree_status)

    worktree_claim = subparsers.add_parser(
        "worktree-claim",
        help="Set or update local coordination metadata for one worktree.",
    )
    add_optional_worktree_name_argument(worktree_claim)
    worktree_claim.add_argument("--owner", default=None, help="Owner or agent responsible for the worktree.")
    worktree_claim.add_argument("--issue", default=None, help="GitHub issue number or identifier.")
    worktree_claim.add_argument("--task-id", default=None, help="Local task identifier.")
    worktree_claim.add_argument("--summary", default=None, help="Short summary of the worktree purpose.")
    worktree_claim.add_argument("--status", default="active", help="Status label such as active, blocked, review, done, or wip.")
    worktree_claim.add_argument("--scope", action="append", default=None, help="Writable scope path. Repeat for multiple scopes.")
    worktree_claim.set_defaults(func=command_worktree_claim)

    worktree_release = subparsers.add_parser(
        "worktree-release",
        help="Mark a worktree as done or otherwise retired in local coordination metadata.",
    )
    add_optional_worktree_name_argument(worktree_release)
    worktree_release.add_argument("--status", default="done", help="Final status label.")
    worktree_release.add_argument("--summary", default=None, help="Optional final summary.")
    worktree_release.set_defaults(func=command_worktree_release)

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
