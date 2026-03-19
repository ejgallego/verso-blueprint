from __future__ import annotations

import argparse
from pathlib import Path
from types import SimpleNamespace
import unittest

import scripts.blueprint_harness as harness_mod
import scripts.blueprint_reference_harness as reference_harness_mod
from scripts.blueprint_harness import build_parser, create_worktree_sync_policy, generate_projects
from scripts.blueprint_harness_projects import HarnessProject
from scripts.blueprint_harness_worktrees import GitWorktree


class BlueprintHarnessCliTests(unittest.TestCase):
    def test_create_worktree_sync_policy_respects_lightweight_mode(self) -> None:
        args = argparse.Namespace(skip_sync=False, skip_reference_sync=False, lightweight=True)
        self.assertEqual(create_worktree_sync_policy(args), (True, True))

    def test_create_worktree_sync_policy_preserves_explicit_flags(self) -> None:
        args = argparse.Namespace(skip_sync=True, skip_reference_sync=False, lightweight=False)
        self.assertEqual(create_worktree_sync_policy(args), (True, False))

    def test_reference_sync_does_not_accept_example_alias(self) -> None:
        parser = reference_harness_mod.build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["sync", "--example", "noperthedron"])

    def test_main_status_parses_require_sync(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["main-status", "--require-sync"])
        self.assertTrue(args.require_sync)

    def test_land_main_parses_cleanup_flags(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["land-main", "feat/demo", "--cleanup", "--keep-remote", "--no-push"])
        self.assertEqual(args.source, "feat/demo")
        self.assertTrue(args.cleanup)
        self.assertTrue(args.keep_remote)
        self.assertTrue(args.no_push)

    def test_reference_edit_parses_project_branch_and_base(self) -> None:
        parser = reference_harness_mod.build_parser()
        args = parser.parse_args(["edit", "noperthedron", "--branch", "wip/noperthedron", "--base", "origin/main"])
        self.assertEqual(args.project, "noperthedron")
        self.assertEqual(args.branch, "wip/noperthedron")
        self.assertEqual(args.base, "origin/main")

    def test_create_worktree_uses_preferred_main_ref_by_default(self) -> None:
        layout = SimpleNamespace(repo_root=Path("/tmp/repo"))
        original = harness_mod.preferred_main_ref
        try:
            harness_mod.preferred_main_ref = lambda _repo_root: "origin/main"
            self.assertEqual(harness_mod.resolve_create_worktree_base(layout, None), "origin/main")
        finally:
            harness_mod.preferred_main_ref = original

    def test_create_worktree_rejects_unsynced_local_main_base(self) -> None:
        layout = SimpleNamespace(repo_root=Path("/tmp/repo"))
        originals = {
            "preferred_main_ref": harness_mod.preferred_main_ref,
            "main_sync_status": harness_mod.main_sync_status,
        }
        try:
            harness_mod.preferred_main_ref = lambda _repo_root: "origin/main"
            harness_mod.main_sync_status = lambda _repo_root: harness_mod.RefSyncStatus(
                local_ref="main",
                upstream_ref="origin/main",
                local_oid="abc",
                upstream_oid="def",
                relationship="diverged",
            )
            with self.assertRaisesRegex(SystemExit, "refusing to use local `main` as the worktree base"):
                harness_mod.resolve_create_worktree_base(layout, "main")
        finally:
            for name, value in originals.items():
                setattr(harness_mod, name, value)

    def test_main_status_require_sync_returns_nonzero_when_unsynced(self) -> None:
        args = argparse.Namespace(require_sync=True)
        layout = SimpleNamespace(repo_root=Path("/tmp/repo"))
        originals = {
            "detect_harness_layout": harness_mod.detect_harness_layout,
            "main_sync_status": harness_mod.main_sync_status,
            "current_branch_name": harness_mod.current_branch_name,
        }
        try:
            harness_mod.detect_harness_layout = lambda _start=None: layout
            harness_mod.main_sync_status = lambda _repo_root: harness_mod.RefSyncStatus(
                local_ref="main",
                upstream_ref="origin/main",
                local_oid="abc",
                upstream_oid="def",
                relationship="behind",
            )
            harness_mod.current_branch_name = lambda _repo_root: "main"
            self.assertEqual(harness_mod.command_main_status(args), 1)
        finally:
            for name, value in originals.items():
                setattr(harness_mod, name, value)

    def test_land_main_rejects_unsynced_main(self) -> None:
        args = argparse.Namespace(source="feat/demo", no_push=False, cleanup=False, keep_remote=False)
        layout = SimpleNamespace(repo_root=Path("/tmp/repo"), package_root=Path("/tmp/repo"), in_linked_worktree=False)
        originals = {
            "detect_harness_layout": harness_mod.detect_harness_layout,
            "current_branch_name": harness_mod.current_branch_name,
            "worktree_is_clean": harness_mod.worktree_is_clean,
            "main_sync_status": harness_mod.main_sync_status,
        }
        try:
            harness_mod.detect_harness_layout = lambda _start=None: layout
            harness_mod.current_branch_name = lambda _repo_root: "main"
            harness_mod.worktree_is_clean = lambda _path: True
            harness_mod.main_sync_status = lambda _repo_root: harness_mod.RefSyncStatus(
                local_ref="main",
                upstream_ref="origin/main",
                local_oid="abc",
                upstream_oid="def",
                relationship="behind",
            )
            with self.assertRaisesRegex(SystemExit, "sync `main` before landing"):
                harness_mod.command_land_main(args)
        finally:
            for name, value in originals.items():
                setattr(harness_mod, name, value)

    def test_land_main_fast_forwards_and_pushes(self) -> None:
        args = argparse.Namespace(source="feat/demo", no_push=False, cleanup=False, keep_remote=False)
        layout = SimpleNamespace(repo_root=Path("/tmp/repo"), package_root=Path("/tmp/repo"), in_linked_worktree=False)
        originals = {
            "detect_harness_layout": harness_mod.detect_harness_layout,
            "current_branch_name": harness_mod.current_branch_name,
            "worktree_is_clean": harness_mod.worktree_is_clean,
            "main_sync_status": harness_mod.main_sync_status,
            "ref_oid": harness_mod.ref_oid,
            "is_ancestor": harness_mod.is_ancestor,
            "preferred_main_ref": harness_mod.preferred_main_ref,
            "run": harness_mod.run,
        }
        commands: list[list[str]] = []
        try:
            harness_mod.detect_harness_layout = lambda _start=None: layout
            harness_mod.current_branch_name = lambda _repo_root: "main"
            harness_mod.worktree_is_clean = lambda _path: True
            harness_mod.main_sync_status = lambda _repo_root: harness_mod.RefSyncStatus(
                local_ref="main",
                upstream_ref="origin/main",
                local_oid="abc",
                upstream_oid="abc",
                relationship="in_sync",
            )
            harness_mod.ref_oid = lambda _repo_root, ref: "deadbeef" if ref == "feat/demo" else None
            harness_mod.is_ancestor = lambda _repo_root, ancestor, descendant: (ancestor, descendant) == ("main", "feat/demo")
            harness_mod.preferred_main_ref = lambda _repo_root: "origin/main"
            harness_mod.run = lambda command, *, cwd: commands.append(command)

            self.assertEqual(harness_mod.command_land_main(args), 0)
        finally:
            for name, value in originals.items():
                setattr(harness_mod, name, value)

        self.assertEqual(commands, [["git", "merge", "--ff-only", "feat/demo"], ["git", "push", "origin", "main"]])

    def test_land_main_cleanup_removes_branch_worktree_and_remote(self) -> None:
        args = argparse.Namespace(source="feat/demo", no_push=False, cleanup=True, keep_remote=False)
        layout = SimpleNamespace(repo_root=Path("/tmp/repo"), package_root=Path("/tmp/repo"), in_linked_worktree=False)
        demo_worktree = GitWorktree(
            name="demo",
            path=Path("/tmp/repo/.worktrees/demo"),
            head="abc123",
            branch="feat/demo",
            root_checkout=False,
        )
        originals = {
            "detect_harness_layout": harness_mod.detect_harness_layout,
            "current_branch_name": harness_mod.current_branch_name,
            "worktree_is_clean": harness_mod.worktree_is_clean,
            "main_sync_status": harness_mod.main_sync_status,
            "ref_oid": harness_mod.ref_oid,
            "is_ancestor": harness_mod.is_ancestor,
            "preferred_main_ref": harness_mod.preferred_main_ref,
            "run": harness_mod.run,
            "branch_worktrees": harness_mod.branch_worktrees,
            "local_branch_ref": harness_mod.local_branch_ref,
            "origin_branch_exists": harness_mod.origin_branch_exists,
        }
        commands: list[list[str]] = []
        try:
            harness_mod.detect_harness_layout = lambda _start=None: layout
            harness_mod.current_branch_name = lambda _repo_root: "main"
            harness_mod.worktree_is_clean = lambda _path: True
            harness_mod.main_sync_status = lambda _repo_root: harness_mod.RefSyncStatus(
                local_ref="main",
                upstream_ref="origin/main",
                local_oid="abc",
                upstream_oid="abc",
                relationship="in_sync",
            )
            harness_mod.ref_oid = lambda _repo_root, ref: "deadbeef" if ref in {"feat/demo", "refs/heads/feat/demo", "refs/remotes/origin/feat/demo"} else None
            harness_mod.is_ancestor = lambda _repo_root, ancestor, descendant: (ancestor, descendant) == ("main", "feat/demo")
            harness_mod.preferred_main_ref = lambda _repo_root: "origin/main"
            harness_mod.run = lambda command, *, cwd: commands.append(command)
            harness_mod.branch_worktrees = lambda _repo_root, branch: [demo_worktree] if branch == "feat/demo" else []
            harness_mod.local_branch_ref = lambda _repo_root, branch: branch if branch == "feat/demo" else None
            harness_mod.origin_branch_exists = lambda _repo_root, branch: branch == "feat/demo"

            self.assertEqual(harness_mod.command_land_main(args), 0)
        finally:
            for name, value in originals.items():
                setattr(harness_mod, name, value)

        self.assertEqual(
            commands,
            [
                ["git", "merge", "--ff-only", "feat/demo"],
                ["git", "push", "origin", "main"],
                ["git", "worktree", "remove", str(demo_worktree.path)],
                ["git", "branch", "-d", "feat/demo"],
                ["git", "push", "origin", "--delete", "feat/demo"],
            ],
        )

    def test_generate_keeps_example_alias(self) -> None:
        parser = reference_harness_mod.build_parser()
        args = parser.parse_args(["generate", "--example", "noperthedron"])
        self.assertEqual(args.project, ["noperthedron"])

    def test_reference_edit_uses_prepare_reference_checkout(self) -> None:
        project = HarnessProject(
            project_id="noperthedron",
            source_kind="git_checkout",
            project_root=".",
            build_target=None,
            generator=None,
            repository="https://github.com/example/noperthedron.git",
            ref="main",
            build_command=("lake", "build"),
            generate_command=("lake", "exe", "blueprint-gen"),
            site_subdir="html-multi",
            panel_regression_script=None,
            browser_tests_path=None,
            description=None,
        )
        args = argparse.Namespace(manifest=None, project="noperthedron", branch="wip/noperthedron", base="origin/main")
        layout = SimpleNamespace(package_root=Path("/tmp/package"), reference_project_edit_root=Path("/tmp/edit"))
        originals = {
            "detect_harness_layout": harness_mod.detect_harness_layout,
            "resolve_manifest_path": harness_mod.resolve_manifest_path,
            "load_project_catalog": harness_mod.load_project_catalog,
            "prepare_reference_edit_checkout": harness_mod.prepare_reference_edit_checkout,
        }
        seen: dict[str, object] = {}
        try:
            harness_mod.detect_harness_layout = lambda _start=None: layout
            harness_mod.resolve_manifest_path = lambda _path_text, _package_root: Path("/tmp/projects.json")
            harness_mod.load_project_catalog = lambda _manifest_path: [project]

            def fake_prepare(_layout, _project, *, branch, base_ref):
                seen["layout"] = _layout
                seen["project"] = _project
                seen["branch"] = branch
                seen["base_ref"] = base_ref
                return Path("/tmp/edit/noperthedron"), branch or "wip/noperthedron", base_ref or "origin/main"

            harness_mod.prepare_reference_edit_checkout = fake_prepare

            self.assertEqual(harness_mod.command_reference_edit(args), 0)
        finally:
            for name, value in originals.items():
                setattr(harness_mod, name, value)

        self.assertEqual(seen["layout"], layout)
        self.assertEqual(seen["project"], project)
        self.assertEqual(seen["branch"], "wip/noperthedron")
        self.assertEqual(seen["base_ref"], "origin/main")

    def test_worktree_retire_supports_detached_merged_worktree(self) -> None:
        args = argparse.Namespace(name="reference-edit", dry_run=False)
        layout = SimpleNamespace(
            repo_root=Path("/tmp/repo"),
            package_root=Path("/tmp/package"),
            worktree_name=None,
            reference_project_cache_root=Path("/tmp/cache"),
            reference_project_root=Path("/tmp/reference-root"),
        )
        detached = GitWorktree(
            name="reference-edit",
            path=Path("/tmp/repo/.worktrees/reference-edit"),
            head="abc123",
            branch=None,
            root_checkout=False,
        )
        originals = {
            "detect_harness_layout": harness_mod.detect_harness_layout,
            "git_worktree_map": harness_mod.git_worktree_map,
            "ref_merged_into_main": harness_mod.ref_merged_into_main,
            "worktree_is_clean": harness_mod.worktree_is_clean,
            "run": harness_mod.run,
            "resolve_manifest_path": harness_mod.resolve_manifest_path,
            "load_project_catalog": harness_mod.load_project_catalog,
            "git_worktrees": harness_mod.git_worktrees,
            "reference_prune_plan": harness_mod.reference_prune_plan,
        }
        commands: list[list[str]] = []
        try:
            harness_mod.detect_harness_layout = lambda _start=None: layout
            harness_mod.git_worktree_map = lambda _repo_root: {"reference-edit": detached}
            harness_mod.ref_merged_into_main = lambda _repo_root, ref: ref == "abc123"
            harness_mod.worktree_is_clean = lambda _path: True
            harness_mod.run = lambda command, *, cwd: commands.append(command)
            harness_mod.resolve_manifest_path = lambda _path_text, _package_root: Path("/tmp/projects.json")
            harness_mod.load_project_catalog = lambda _manifest_path: []
            harness_mod.git_worktrees = lambda _repo_root: []
            harness_mod.reference_prune_plan = lambda *_args, **_kwargs: []

            self.assertEqual(harness_mod.command_worktree_retire(args), 0)
        finally:
            for name, value in originals.items():
                setattr(harness_mod, name, value)

        self.assertEqual(commands, [["git", "worktree", "remove", str(detached.path)]])

    def test_generate_projects_does_not_auto_sync_root_lake(self) -> None:
        project = HarnessProject(
            project_id="demo",
            source_kind="in_repo_example",
            project_root=".",
            build_target="Demo",
            generator="demo",
            repository=None,
            ref=None,
            build_command=None,
            generate_command=None,
            site_subdir="html-multi",
            panel_regression_script=None,
            browser_tests_path=None,
            description=None,
        )
        layout = SimpleNamespace(package_root=Path("/tmp/package"), in_linked_worktree=True)

        original_sync = harness_mod.sync_root_worktree_lake
        original_ensure = harness_mod.ensure_prebuilt_executable
        original_render = harness_mod.render_in_repo_projects
        try:
            harness_mod.sync_root_worktree_lake = lambda _layout: (_ for _ in ()).throw(AssertionError("unexpected sync"))
            harness_mod.ensure_prebuilt_executable = lambda _package_root, _exe_name: Path("/tmp/demo")
            harness_mod.render_in_repo_projects = lambda _package_root, _output_root, _projects, _serial: None

            generate_projects(
                layout,
                Path("/tmp/out"),
                [project],
                skip_build=False,
                serial=False,
                allow_local_build=False,
            )
        finally:
            harness_mod.sync_root_worktree_lake = original_sync
            harness_mod.ensure_prebuilt_executable = original_ensure
            harness_mod.render_in_repo_projects = original_render

    def test_validate_run_lean_tests_does_not_auto_sync_root_lake(self) -> None:
        args = argparse.Namespace(
            output_root=None,
            manifest=None,
            project=None,
            run_lean_tests=True,
            skip_panel_regression=False,
            skip_browser_tests=False,
            serial=False,
            pytest_arg=[],
            allow_local_build=False,
            stop_on_first_failure=False,
        )
        layout = SimpleNamespace(package_root=Path("/tmp/package"), in_linked_worktree=True)
        originals = {
            "detect_harness_layout": harness_mod.detect_harness_layout,
            "resolve_output_root": harness_mod.resolve_output_root,
            "resolve_manifest_path": harness_mod.resolve_manifest_path,
            "load_project_catalog": harness_mod.load_project_catalog,
            "selected_projects": harness_mod.selected_projects,
            "should_use_local_build": harness_mod.should_use_local_build,
            "sync_root_worktree_lake": harness_mod.sync_root_worktree_lake,
            "find_test_driver_binary": harness_mod.find_test_driver_binary,
            "run_capturing_failure": harness_mod.run_capturing_failure,
            "generate_projects": harness_mod.generate_projects,
        }
        try:
            harness_mod.detect_harness_layout = lambda _start=None: layout
            harness_mod.resolve_output_root = lambda _path_text, _start=None: Path("/tmp/out")
            harness_mod.resolve_manifest_path = lambda _path_text, _package_root: Path("/tmp/projects.json")
            harness_mod.load_project_catalog = lambda _manifest_path: []
            harness_mod.selected_projects = lambda _catalog, _values: []
            harness_mod.should_use_local_build = lambda _layout, _allow_local_build: False
            harness_mod.sync_root_worktree_lake = lambda _layout: (_ for _ in ()).throw(AssertionError("unexpected sync"))
            harness_mod.find_test_driver_binary = lambda _package_root: Path("/tmp/verso-blueprint-tests")
            harness_mod.run_capturing_failure = lambda _step, _command, cwd: None
            harness_mod.generate_projects = lambda *_args, **_kwargs: None

            self.assertEqual(harness_mod.command_validate(args), 0)
        finally:
            for name, value in originals.items():
                setattr(harness_mod, name, value)


if __name__ == "__main__":
    unittest.main()
