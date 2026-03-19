from __future__ import annotations

import argparse
from pathlib import Path
from types import SimpleNamespace
import unittest

import scripts.blueprint_harness as harness_mod
from scripts.blueprint_harness import build_parser, create_worktree_sync_policy, generate_projects
from scripts.blueprint_harness_projects import HarnessProject


class BlueprintHarnessCliTests(unittest.TestCase):
    def test_create_worktree_sync_policy_respects_lightweight_mode(self) -> None:
        args = argparse.Namespace(skip_sync=False, skip_reference_sync=False, lightweight=True)
        self.assertEqual(create_worktree_sync_policy(args), (True, True))

    def test_create_worktree_sync_policy_preserves_explicit_flags(self) -> None:
        args = argparse.Namespace(skip_sync=True, skip_reference_sync=False, lightweight=False)
        self.assertEqual(create_worktree_sync_policy(args), (True, False))

    def test_reference_sync_does_not_accept_example_alias(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["reference-sync", "--example", "noperthedron"])

    def test_generate_keeps_example_alias(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["generate", "--example", "noperthedron"])
        self.assertEqual(args.project, ["noperthedron"])

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
