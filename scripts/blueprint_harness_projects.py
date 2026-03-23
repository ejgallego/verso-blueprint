from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class HarnessProject:
    project_id: str
    source_kind: str
    project_root: str
    build_target: str | None
    generator: str | None
    repository: str | None
    ref: str | None
    prepare_command: tuple[str, ...] | None
    build_command: tuple[str, ...] | None
    generate_command: tuple[str, ...] | None
    site_subdir: str
    panel_regression_script: str | None
    browser_tests_path: str | None
    description: str | None

    @property
    def in_repo_example(self) -> bool:
        return self.source_kind == "in_repo_example"

    @property
    def git_checkout(self) -> bool:
        return self.source_kind == "git_checkout"

    @property
    def in_repo_target_project(self) -> bool:
        return self.in_repo_example and self.build_target is not None and self.generator is not None

    @property
    def in_repo_command_project(self) -> bool:
        return self.in_repo_example and self.generate_command is not None


def default_project_manifest(package_root: Path) -> Path:
    return package_root / "tests" / "harness" / "projects.json"


def resolve_manifest_path(path_text: str | None, package_root: Path) -> Path:
    if path_text is None:
        return default_project_manifest(package_root)

    path = Path(path_text)
    if path.is_absolute():
        return path.resolve()
    return (Path.cwd() / path).resolve()


def _require_string(data: dict, key: str, *, context: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{context}: expected non-empty string field `{key}`")
    return value


def _optional_string(data: dict, key: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ValueError(f"expected non-empty string field `{key}`")
    return value


def _optional_command(data: dict, key: str, *, context: str) -> tuple[str, ...] | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"{context}: expected non-empty string list field `{key}`")
    return tuple(value)


def load_projects_manifest(manifest_path: Path) -> list[HarnessProject]:
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    if raw.get("version") != 1:
        raise ValueError(f"{manifest_path}: unsupported manifest version {raw.get('version')!r}")

    entries = raw.get("projects")
    if not isinstance(entries, list):
        raise ValueError(f"{manifest_path}: expected top-level `projects` list")

    projects: list[HarnessProject] = []
    seen_ids: set[str] = set()
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"{manifest_path}: project #{index} must be an object")

        context = f"{manifest_path}: project #{index}"
        project_id = _require_string(entry, "id", context=context)
        if project_id in seen_ids:
            raise ValueError(f"{context}: duplicate project id `{project_id}`")
        seen_ids.add(project_id)

        source = entry.get("source")
        if not isinstance(source, dict):
            raise ValueError(f"{context}: missing object field `source`")
        source_kind = _require_string(source, "kind", context=context)
        project_root = _optional_string(source, "project_root") or "."

        build_target = _optional_string(entry, "build_target")
        generator = _optional_string(entry, "generator")
        repository = _optional_string(source, "repository")
        ref = _optional_string(source, "ref") or "main"
        prepare_command = _optional_command(entry, "prepare_command", context=context)
        build_command = _optional_command(entry, "build_command", context=context)
        generate_command = _optional_command(entry, "generate_command", context=context)

        validation = entry.get("validation") or {}
        if not isinstance(validation, dict):
            raise ValueError(f"{context}: expected object field `validation`")
        panel_regression_script = _optional_string(validation, "panel_regression_script")
        browser_tests_path = _optional_string(validation, "browser_tests_path")
        description = _optional_string(entry, "description")
        site_subdir = _optional_string(entry, "site_subdir") or "html-multi"

        if source_kind == "in_repo_example":
            target_mode = build_target is not None or generator is not None
            command_mode = build_command is not None or generate_command is not None
            if target_mode and command_mode:
                raise ValueError(
                    f"{context}: in-repo examples must use either `build_target`/`generator` or "
                    "`build_command`/`generate_command`, not both"
                )
            if target_mode:
                if build_target is None or generator is None:
                    raise ValueError(
                        f"{context}: in-repo examples using root-package targets must declare both "
                        "`build_target` and `generator`"
                    )
                if repository is not None or build_command is not None or generate_command is not None:
                    raise ValueError(
                        f"{context}: in-repo examples using root-package targets must not declare "
                        "`repository`, `build_command`, or `generate_command`"
                    )
                if prepare_command is not None:
                    raise ValueError(
                        f"{context}: in-repo examples using root-package targets must not declare "
                        "`prepare_command`"
                    )
            elif command_mode:
                if generate_command is None:
                    raise ValueError(
                        f"{context}: in-repo examples using nested project commands must declare "
                        "`generate_command`"
                    )
                if repository is not None or build_target is not None or generator is not None:
                    raise ValueError(
                        f"{context}: in-repo examples using nested project commands must not declare "
                        "`repository`, `build_target`, or `generator`"
                    )
            else:
                raise ValueError(
                    f"{context}: in-repo examples must declare either `build_target`/`generator` "
                    "or `generate_command`"
                )
        elif source_kind == "git_checkout":
            if repository is None:
                raise ValueError(f"{context}: git checkout projects must declare `source.repository`")
            if generate_command is None:
                raise ValueError(f"{context}: git checkout projects must declare `generate_command`")
            if build_target is not None or generator is not None:
                raise ValueError(
                    f"{context}: git checkout projects must not declare `build_target` or `generator`"
                )
        else:
            raise ValueError(f"{context}: unsupported source kind `{source_kind}`")

        projects.append(
            HarnessProject(
                project_id=project_id,
                source_kind=source_kind,
                project_root=project_root,
                build_target=build_target,
                generator=generator,
                repository=repository,
                ref=ref,
                prepare_command=prepare_command,
                build_command=build_command,
                generate_command=generate_command,
                site_subdir=site_subdir,
                panel_regression_script=panel_regression_script,
                browser_tests_path=browser_tests_path,
                description=description,
            )
        )

    return projects
