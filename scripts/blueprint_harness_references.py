from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

from scripts.blueprint_harness_projects import HarnessProject
from scripts.blueprint_harness_utils import lean_low_priority_command, run


OFFICIAL_BLUEPRINT_REQUIRE = 'require VersoBlueprint from git "https://github.com/leanprover/verso-blueprint"@"main"'
OFFICIAL_BLUEPRINT_URL_PATTERNS = (
    r"https://github\.com/leanprover/verso-blueprint(?:\.git)?",
    r"git@github\.com:leanprover/verso-blueprint\.git",
    r"ssh://git@github\.com/leanprover/verso-blueprint\.git",
)

def output_dir_for(project: HarnessProject, output_root: Path) -> Path:
    return output_root / project.project_id


def site_dir_for(project: HarnessProject, output_root: Path) -> Path:
    return output_dir_for(project, output_root) / project.site_subdir


def reference_cache_checkout_dir(layout, project: HarnessProject) -> Path:
    return layout.reference_project_cache_root / project.project_id


def reference_local_checkout_dir(layout, project: HarnessProject) -> Path:
    return layout.reference_project_checkout_root / project.project_id


def use_shared_reference_checkout() -> bool:
    return os.getenv("BP_REFERENCE_CHECKOUT_MODE") == "shared"


def format_external_command(
    command: tuple[str, ...],
    *,
    project: HarnessProject,
    package_root: Path,
    checkout_root: Path,
    project_dir: Path,
    output_dir: Path,
) -> list[str]:
    site_dir = site_dir_for(project, output_dir.parent)
    placeholders = {
        "checkout_root": str(checkout_root),
        "package_root": str(package_root),
        "project_dir": str(project_dir),
        "output_dir": str(output_dir),
        "project_id": project.project_id,
        "site_dir": str(site_dir),
    }
    return [part.format(**placeholders) for part in command]


def clone_git_project(project: HarnessProject, destination: Path, *, cwd: Path, source: str | None = None) -> Path:
    command = ["git", "clone"]
    if source is None:
        command.extend(["--depth", "1"])
    if project.ref and source is None:
        command.extend(["--branch", project.ref])
    command.extend([source or project.repository or "", str(destination)])
    run(command, cwd=cwd)
    return destination


def update_git_checkout(project: HarnessProject, checkout_root: Path) -> None:
    if project.ref is None:
        return
    run(["git", "fetch", "--depth", "1", "origin", project.ref], cwd=checkout_root)
    run(["git", "checkout", "--detach", "FETCH_HEAD"], cwd=checkout_root)
    # Harness-managed clones are disposable; keep them clean even if a previous
    # run rewrote tracked files such as `lakefile.lean`.
    run(["git", "reset", "--hard", "FETCH_HEAD"], cwd=checkout_root)


def rewrite_local_blueprint_dependency(project_dir: Path, package_root: Path) -> Path:
    lakefile = project_dir / "lakefile.lean"
    if not lakefile.exists():
        raise SystemExit(f"[blueprint-harness] missing lakefile for cloned project: {lakefile}")

    relative_path = os.path.relpath(package_root, start=project_dir)
    replacement = f'require VersoBlueprint from "{relative_path}"'
    text = lakefile.read_text(encoding="utf-8")
    # Lake package overrides are not applied during the initial `lake update`
    # manifest bootstrap path on a fresh clone, so the harness patches the
    # cloned dependency declaration before the first update.
    require_pattern = re.compile(
        r'^\s*require\s+VersoBlueprint\s+from\s+git\s+"(?P<url>[^"]+)"(?:\s*@\s*"[^"]+")?\s*$',
        re.MULTILINE,
    )
    match = next(
        (
            candidate
            for candidate in require_pattern.finditer(text)
            if any(re.fullmatch(pattern, candidate.group("url")) for pattern in OFFICIAL_BLUEPRINT_URL_PATTERNS)
        ),
        None,
    )
    if match is None:
        raise SystemExit(
            "[blueprint-harness] expected the cloned project to declare `VersoBlueprint` in "
            "`lakefile.lean` from an official `leanprover/verso-blueprint` Git source; "
            "cannot inject the local path override automatically."
        )
    rewritten = text[: match.start()] + replacement + text[match.end() :]
    lakefile.write_text(rewritten, encoding="utf-8")
    return lakefile


def maybe_rewrite_in_repo_blueprint_dependency(project_dir: Path, package_root: Path) -> tuple[Path | None, str | None]:
    lakefile = project_dir / "lakefile.lean"
    if not lakefile.exists():
        return None, None

    text = lakefile.read_text(encoding="utf-8")
    if 'require VersoBlueprint from "' in text:
        return None, None
    if "require VersoBlueprint from git" not in text:
        return None, None

    rewrite_local_blueprint_dependency(project_dir, package_root)
    return lakefile, text


def sync_reference_cache_checkout(layout, project: HarnessProject, *, warm_build: bool) -> Path:
    cache_dir = reference_cache_checkout_dir(layout, project)
    cache_dir.parent.mkdir(parents=True, exist_ok=True)
    if not cache_dir.exists():
        clone_git_project(project, cache_dir, cwd=layout.package_root)
    else:
        update_git_checkout(project, cache_dir)
    project_dir = cache_dir / project.project_root
    cache_lakefile = project_dir / "lakefile.lean"
    original_text = cache_lakefile.read_text(encoding="utf-8")
    rewrite_local_blueprint_dependency(project_dir, layout.repo_root)
    try:
        run(lean_low_priority_command(layout.package_root, "lake", "update"), cwd=project_dir)
        if warm_build and project.build_command is not None:
            run(lean_low_priority_command(layout.package_root, *project.build_command), cwd=project_dir)
    finally:
        cache_lakefile.write_text(original_text, encoding="utf-8")
    return cache_dir


def prime_reference_checkout_from_root_lake_cache(layout, project_dir: Path) -> None:
    if shutil.which("rsync") is None:
        return

    shared_build_roots = [
        layout.package_root / ".lake" / "packages" / "mathlib" / ".lake" / "build",
        layout.package_root / ".lake" / "packages" / "verso" / ".lake" / "build",
    ]
    target_build_roots = [
        project_dir / ".lake" / "packages" / "mathlib" / ".lake" / "build",
        project_dir / ".lake" / "packages" / "verso" / ".lake" / "build",
    ]

    for source_root, target_root in zip(shared_build_roots, target_build_roots):
        if not source_root.exists():
            continue
        target_root.parent.mkdir(parents=True, exist_ok=True)
        run(["rsync", "-a", f"{source_root}/", f"{target_root}/"], cwd=layout.package_root)


def sync_reference_local_checkout(layout, project: HarnessProject, cache_dir: Path) -> Path:
    local_dir = reference_local_checkout_dir(layout, project)
    local_dir.parent.mkdir(parents=True, exist_ok=True)
    if not local_dir.exists():
        clone_git_project(project, local_dir, cwd=layout.package_root, source=str(cache_dir))
    else:
        update_git_checkout(project, local_dir)

    cache_lake = cache_dir / ".lake"
    if cache_lake.exists():
        run(["rsync", "-a", "--delete", f"{cache_lake}/", f"{local_dir / '.lake'}/"], cwd=layout.package_root)
    return local_dir


def generate_in_repo_command_project(layout, output_root: Path, project: HarnessProject, *, skip_build: bool) -> None:
    project_dir = layout.package_root / project.project_root
    if not project_dir.exists():
        raise SystemExit(f"[blueprint-harness] missing in-repo project root for `{project.project_id}`: {project_dir}")

    output_dir = output_dir_for(project, output_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    rewritten_lakefile, original_lakefile_text = maybe_rewrite_in_repo_blueprint_dependency(project_dir, layout.package_root)
    if rewritten_lakefile is not None:
        print(f"[blueprint-harness] local package override: rewrote {rewritten_lakefile}")
    try:
        run(lean_low_priority_command(layout.package_root, "lake", "update"), cwd=project_dir)
        if not skip_build and project.build_command is not None:
            run(
                lean_low_priority_command(
                    layout.package_root,
                    *format_external_command(
                        project.build_command,
                        project=project,
                        package_root=layout.package_root,
                        checkout_root=project_dir,
                        project_dir=project_dir,
                        output_dir=output_dir,
                    ),
                ),
                cwd=project_dir,
            )
        run(
            lean_low_priority_command(
                layout.package_root,
                *format_external_command(
                    project.generate_command or (),
                    project=project,
                    package_root=layout.package_root,
                    checkout_root=project_dir,
                    project_dir=project_dir,
                    output_dir=output_dir,
                ),
            ),
            cwd=project_dir,
        )
    finally:
        if rewritten_lakefile is not None and original_lakefile_text is not None:
            rewritten_lakefile.write_text(original_lakefile_text, encoding="utf-8")


def generate_git_project(layout, output_root: Path, project: HarnessProject, *, skip_build: bool) -> None:
    cache_dir = sync_reference_cache_checkout(layout, project, warm_build=not skip_build)
    checkout_root = cache_dir if use_shared_reference_checkout() else sync_reference_local_checkout(layout, project, cache_dir)
    project_dir = checkout_root / project.project_root
    prime_reference_checkout_from_root_lake_cache(layout, project_dir)
    output_dir = output_dir_for(project, output_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    original_text = (project_dir / "lakefile.lean").read_text(encoding="utf-8") if use_shared_reference_checkout() else None
    try:
        rewritten_lakefile = rewrite_local_blueprint_dependency(project_dir, layout.package_root)
        print(f"[blueprint-harness] local package override: rewrote {rewritten_lakefile}")
        run(lean_low_priority_command(layout.package_root, "lake", "update"), cwd=project_dir)
        if not skip_build and project.build_command is not None:
            run(
                lean_low_priority_command(
                    layout.package_root,
                    *format_external_command(
                        project.build_command,
                        project=project,
                        package_root=layout.package_root,
                        checkout_root=checkout_root,
                        project_dir=project_dir,
                        output_dir=output_dir,
                    ),
                ),
                cwd=project_dir,
            )
        run(
            lean_low_priority_command(
                layout.package_root,
                *format_external_command(
                    project.generate_command or (),
                    project=project,
                    package_root=layout.package_root,
                    checkout_root=checkout_root,
                    project_dir=project_dir,
                    output_dir=output_dir,
                ),
            ),
            cwd=project_dir,
        )
    finally:
        if original_text is not None:
            (project_dir / "lakefile.lean").write_text(original_text, encoding="utf-8")


def sync_reference_blueprints(layout, projects: list[HarnessProject], *, warm_build: bool, prepare_local_checkout: bool) -> None:
    git_projects = [project for project in projects if project.git_checkout]
    if not git_projects:
        return
    if shutil.which("rsync") is None:
        raise SystemExit("[blueprint-harness] `rsync` is required for reference blueprint cache sync.")
    for project in git_projects:
        cache_dir = sync_reference_cache_checkout(layout, project, warm_build=warm_build)
        if prepare_local_checkout:
            local_dir = sync_reference_local_checkout(layout, project, cache_dir)
            print(f"[blueprint-harness] prepared local reference checkout: {local_dir}")


def reference_prune_plan(active_worktree_names: set[str], project_ids: set[str], cache_root: Path, checkout_root: Path) -> list[Path]:
    removals: list[Path] = []
    if cache_root.exists():
        for path in sorted(child for child in cache_root.iterdir() if child.is_dir()):
            if path.name not in project_ids:
                removals.append(path)
    if checkout_root.exists():
        for namespace_dir in sorted(child for child in checkout_root.iterdir() if child.is_dir()):
            if namespace_dir.name not in active_worktree_names:
                removals.append(namespace_dir)
                continue
            for project_dir in sorted(child for child in namespace_dir.iterdir() if child.is_dir()):
                if project_dir.name not in project_ids:
                    removals.append(project_dir)
    return removals
