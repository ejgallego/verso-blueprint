from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


EXAMPLES: tuple[str, ...] = ("noperthedron", "spherepackingblueprint")


@dataclass(frozen=True)
class HarnessLayout:
    package_root: Path
    repo_root: Path
    artifact_root: Path
    worktree_name: str | None

    @property
    def in_linked_worktree(self) -> bool:
        return self.worktree_name is not None

    @property
    def reference_output_root(self) -> Path:
        return self.artifact_root / "reference-blueprints"

    @property
    def example_output_root(self) -> Path:
        return self.reference_output_root


def find_package_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    current_dir = current if current.is_dir() else current.parent
    for candidate in (current_dir, *current_dir.parents):
        if (candidate / "lakefile.lean").exists() and (candidate / "AGENTS.md").exists():
            return candidate
    raise FileNotFoundError(f"Could not locate package root from {current}")


def detect_harness_layout(start: Path | None = None) -> HarnessLayout:
    package_root = find_package_root(start)
    if package_root.parent.name == ".worktrees":
        repo_root = package_root.parents[1]
        worktree_name = package_root.name
        artifact_root = repo_root / "_out" / worktree_name
    else:
        repo_root = package_root
        worktree_name = None
        artifact_root = package_root / "_out"
    return HarnessLayout(
        package_root=package_root,
        repo_root=repo_root,
        artifact_root=artifact_root,
        worktree_name=worktree_name,
    )


def resolve_cli_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path.resolve()
    return (Path.cwd() / path).resolve()


def resolve_output_root(path_text: str | None, start: Path | None = None) -> Path:
    if path_text is not None:
        return resolve_cli_path(path_text)
    return detect_harness_layout(start).reference_output_root


def canonical_example_site_dir(example: str, start: Path | None = None) -> Path:
    layout = detect_harness_layout(start)
    return layout.reference_output_root / example / "html-multi"


def previous_canonical_example_site_dir(example: str, start: Path | None = None) -> Path:
    layout = detect_harness_layout(start)
    return layout.artifact_root / "example-blueprints" / example / "html-multi"


def legacy_shared_example_site_dir(example: str, start: Path | None = None) -> Path:
    layout = detect_harness_layout(start)
    return layout.artifact_root / example / "html-multi"


def example_site_candidates(example: str, start: Path | None = None) -> list[Path]:
    candidates = [
        canonical_example_site_dir(example, start),
        previous_canonical_example_site_dir(example, start),
        # Retain the older shared repo-root layout during the verso -> verso-blueprint migration.
        legacy_shared_example_site_dir(example, start),
    ]
    unique: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        if candidate not in seen:
            unique.append(candidate)
            seen.add(candidate)
    return unique


def first_existing(paths: Iterable[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def default_example_site_dir(example: str, start: Path | None = None) -> Path:
    candidates = example_site_candidates(example, start)
    return first_existing(candidates) or candidates[0]
