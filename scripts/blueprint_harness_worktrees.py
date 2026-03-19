from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess


WORKTREE_METADATA_FILENAME = ".codex-worktree.json"
ROOT_METADATA_FILENAME = "_root.json"
REGISTRY_FILENAME = "registry.json"
METADATA_DIRNAME = "_meta"


@dataclass(frozen=True)
class GitWorktree:
    name: str
    path: Path
    head: str
    branch: str | None
    root_checkout: bool


@dataclass
class WorktreeRecord:
    version: int
    name: str
    path: str
    branch: str | None
    root_checkout: bool
    status: str
    owner: str | None = None
    issue: str | None = None
    task_id: str | None = None
    summary: str | None = None
    write_scope: list[str] = field(default_factory=list)
    updated_at: str | None = None
    last_seen_at: str | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def worktree_name(repo_root: Path, path: Path) -> str:
    return "main" if path.resolve() == repo_root.resolve() else path.name


def metadata_path(repo_root: Path, name: str) -> Path:
    if name == "main":
        return repo_root / ".worktrees" / METADATA_DIRNAME / ROOT_METADATA_FILENAME
    return repo_root / ".worktrees" / METADATA_DIRNAME / f"{name}.json"


def legacy_metadata_path(repo_root: Path, name: str) -> Path:
    if name == "main":
        return repo_root / ".worktrees" / ROOT_METADATA_FILENAME
    return repo_root / ".worktrees" / name / WORKTREE_METADATA_FILENAME


def registry_path(repo_root: Path) -> Path:
    return repo_root / ".worktrees" / REGISTRY_FILENAME


def default_status(branch: str | None, root_checkout: bool) -> str:
    if root_checkout:
        return "base"
    if branch is None:
        return "active"
    if branch.startswith("wip/"):
        return "wip"
    return "active"


def default_summary(name: str) -> str:
    return name.replace("-", " ")


def parse_git_worktree_porcelain(text: str, repo_root: Path) -> list[GitWorktree]:
    blocks = [block for block in text.strip().split("\n\n") if block.strip()]
    worktrees: list[GitWorktree] = []
    for block in blocks:
        path: Path | None = None
        head: str | None = None
        branch: str | None = None
        for line in block.splitlines():
            if line.startswith("worktree "):
                path = Path(line.removeprefix("worktree ").strip())
            elif line.startswith("HEAD "):
                head = line.removeprefix("HEAD ").strip()
            elif line.startswith("branch "):
                branch_ref = line.removeprefix("branch ").strip()
                branch = branch_ref.removeprefix("refs/heads/")
        if path is None or head is None:
            continue
        worktrees.append(
            GitWorktree(
                name=worktree_name(repo_root, path),
                path=path,
                head=head,
                branch=branch,
                root_checkout=path.resolve() == repo_root.resolve(),
            )
        )
    return worktrees


def git_worktrees(repo_root: Path) -> list[GitWorktree]:
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    )
    return parse_git_worktree_porcelain(result.stdout, repo_root)


def load_record(path: Path) -> WorktreeRecord | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return WorktreeRecord(**data)


def save_record(path: Path, record: WorktreeRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(record), indent=2) + "\n", encoding="utf-8")


def load_registry(repo_root: Path) -> dict[str, WorktreeRecord]:
    path = registry_path(repo_root)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("worktrees", [])
    return {entry["name"]: WorktreeRecord(**entry) for entry in entries}


def save_registry(repo_root: Path, records: list[WorktreeRecord]) -> Path:
    path = registry_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "generated_at": utc_now(),
        "worktrees": [asdict(record) for record in records],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def sync_worktree_registry(repo_root: Path) -> tuple[list[WorktreeRecord], Path]:
    previous = load_registry(repo_root)
    now = utc_now()
    records: list[WorktreeRecord] = []
    for git_wt in git_worktrees(repo_root):
        path = metadata_path(repo_root, git_wt.name)
        legacy_path = legacy_metadata_path(repo_root, git_wt.name)
        existing = load_record(path) or load_record(legacy_path) or previous.get(git_wt.name)
        record = WorktreeRecord(
            version=1,
            name=git_wt.name,
            path=str(git_wt.path),
            branch=git_wt.branch,
            root_checkout=git_wt.root_checkout,
            status=existing.status if existing else default_status(git_wt.branch, git_wt.root_checkout),
            owner=existing.owner if existing else None,
            issue=existing.issue if existing else None,
            task_id=existing.task_id if existing else None,
            summary=existing.summary if existing else default_summary(git_wt.name),
            write_scope=existing.write_scope[:] if existing else [],
            updated_at=now,
            last_seen_at=now,
        )
        save_record(path, record)
        if legacy_path.exists():
            legacy_path.unlink()
        records.append(record)
    records.sort(key=lambda record: (not record.root_checkout, record.name))
    return records, save_registry(repo_root, records)


def resolve_worktree_name(current_name: str | None, requested_name: str | None) -> str:
    if requested_name:
        return requested_name
    return current_name or "main"


def worktree_record_map(repo_root: Path) -> tuple[dict[str, WorktreeRecord], Path]:
    records, registry = sync_worktree_registry(repo_root)
    return {record.name: record for record in records}, registry


def update_worktree_record(
    repo_root: Path,
    name: str,
    *,
    owner: str | None = None,
    issue: str | None = None,
    task_id: str | None = None,
    summary: str | None = None,
    status: str | None = None,
    write_scope: list[str] | None = None,
) -> tuple[WorktreeRecord, Path, Path]:
    record_map, registry = worktree_record_map(repo_root)
    if name not in record_map:
        raise KeyError(name)
    record = record_map[name]
    if owner is not None:
        record.owner = owner
    if issue is not None:
        record.issue = issue
    if task_id is not None:
        record.task_id = task_id
    if summary is not None:
        record.summary = summary
    if status is not None:
        record.status = status
    if write_scope is not None:
        record.write_scope = write_scope
    now = utc_now()
    record.updated_at = now
    record.last_seen_at = now
    record_path = metadata_path(repo_root, name)
    save_record(record_path, record)
    save_registry(repo_root, sorted(record_map.values(), key=lambda rec: (not rec.root_checkout, rec.name)))
    return record, record_path, registry
