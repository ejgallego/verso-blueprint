from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest

from scripts.blueprint_harness_projects import (
    default_project_manifest,
    load_projects_manifest,
)
from scripts.blueprint_harness import OFFICIAL_BLUEPRINT_REQUIRE, rewrite_local_blueprint_dependency, use_shared_reference_checkout


PACKAGE_ROOT = Path(__file__).resolve().parents[2]


class BlueprintHarnessProjectsTests(unittest.TestCase):
    def test_default_manifest_contains_current_external_projects(self) -> None:
        manifest = default_project_manifest(PACKAGE_ROOT)
        projects = load_projects_manifest(manifest)

        self.assertEqual(
            [project.project_id for project in projects],
            ["project-template", "noperthedron", "spherepackingblueprint"],
        )
        self.assertTrue(projects[0].in_repo_example)
        self.assertTrue(projects[0].in_repo_command_project)
        self.assertEqual(projects[0].project_root, "project_template")
        self.assertEqual(projects[0].generate_command, ("lake", "exe", "blueprint-gen", "--output", "{output_dir}"))
        self.assertTrue(projects[1].git_checkout)
        self.assertEqual(projects[1].repository, "https://github.com/ejgallego/verso-noperthedron.git")
        self.assertEqual(projects[1].browser_tests_path, "tests/browser")
        self.assertEqual(projects[1].panel_regression_script, "tests/harness/noperthedron/check_blueprint_code_panels.py")

    def test_git_checkout_project_is_supported(self) -> None:
        manifest_data = {
            "version": 1,
            "projects": [
                {
                    "id": "external-blueprint",
                    "source": {
                        "kind": "git_checkout",
                        "repository": "https://github.com/example/external-blueprint.git",
                        "ref": "main",
                        "project_root": "."
                    },
                    "build_command": ["lake", "build"],
                    "generate_command": ["lake", "exe", "blueprint-gen", "--output", "{output_dir}"],
                    "site_subdir": "html-multi"
                }
            ]
        }

        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "projects.json"
            manifest.write_text(json.dumps(manifest_data), encoding="utf-8")
            projects = load_projects_manifest(manifest)

        self.assertEqual(len(projects), 1)
        self.assertTrue(projects[0].git_checkout)
        self.assertEqual(projects[0].generate_command, ("lake", "exe", "blueprint-gen", "--output", "{output_dir}"))

    def test_in_repo_command_project_is_supported(self) -> None:
        manifest_data = {
            "version": 1,
            "projects": [
                {
                    "id": "project-template",
                    "source": {
                        "kind": "in_repo_example",
                        "project_root": "project_template",
                    },
                    "build_command": ["lake", "build"],
                    "generate_command": ["lake", "exe", "blueprint-gen", "--output", "{output_dir}"],
                    "site_subdir": "html-multi",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "projects.json"
            manifest.write_text(json.dumps(manifest_data), encoding="utf-8")
            projects = load_projects_manifest(manifest)

        self.assertEqual(len(projects), 1)
        self.assertTrue(projects[0].in_repo_example)
        self.assertTrue(projects[0].in_repo_command_project)
        self.assertEqual(projects[0].project_root, "project_template")
        self.assertEqual(projects[0].build_command, ("lake", "build"))
        self.assertEqual(projects[0].generate_command, ("lake", "exe", "blueprint-gen", "--output", "{output_dir}"))

    def test_duplicate_project_ids_are_rejected(self) -> None:
        manifest_data = {
            "version": 1,
            "projects": [
                {
                    "id": "dup",
                    "source": {"kind": "in_repo_example"},
                    "build_target": "a",
                    "generator": "a"
                },
                {
                    "id": "dup",
                    "source": {"kind": "in_repo_example"},
                    "build_target": "b",
                    "generator": "b"
                }
            ]
        }

        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "projects.json"
            manifest.write_text(json.dumps(manifest_data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate project id"):
                load_projects_manifest(manifest)

    def test_rewrite_local_blueprint_dependency_replaces_official_git_require(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            lakefile = project_dir / "lakefile.lean"
            lakefile.write_text(
                "\n".join(
                    [
                        "import Lake",
                        "open Lake DSL",
                        OFFICIAL_BLUEPRINT_REQUIRE,
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            result = rewrite_local_blueprint_dependency(project_dir, PACKAGE_ROOT)

            self.assertEqual(result, lakefile)
            text = lakefile.read_text(encoding="utf-8")
            self.assertNotIn(OFFICIAL_BLUEPRINT_REQUIRE, text)
            self.assertIn('require VersoBlueprint from "', text)

    def test_rewrite_local_blueprint_dependency_accepts_official_repo_with_non_main_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            lakefile = project_dir / "lakefile.lean"
            lakefile.write_text(
                'require VersoBlueprint from git "https://github.com/leanprover/verso-blueprint.git"@"v1.2.3"\n',
                encoding="utf-8",
            )

            rewrite_local_blueprint_dependency(project_dir, PACKAGE_ROOT)

            text = lakefile.read_text(encoding="utf-8")
            self.assertIn('require VersoBlueprint from "', text)
            self.assertNotIn('from git "https://github.com/leanprover/verso-blueprint.git"', text)

    def test_rewrite_local_blueprint_dependency_rejects_unexpected_require_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            lakefile = project_dir / "lakefile.lean"
            lakefile.write_text(
                'require VersoBlueprint from git "https://github.com/example/fork"@"main"\n',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(SystemExit, "official `leanprover/verso-blueprint` Git source"):
                rewrite_local_blueprint_dependency(project_dir, PACKAGE_ROOT)

    def test_use_shared_reference_checkout_env_switch(self) -> None:
        old = os.environ.get("BP_REFERENCE_CHECKOUT_MODE")
        try:
            os.environ.pop("BP_REFERENCE_CHECKOUT_MODE", None)
            self.assertFalse(use_shared_reference_checkout())
            os.environ["BP_REFERENCE_CHECKOUT_MODE"] = "shared"
            self.assertTrue(use_shared_reference_checkout())
        finally:
            if old is None:
                os.environ.pop("BP_REFERENCE_CHECKOUT_MODE", None)
            else:
                os.environ["BP_REFERENCE_CHECKOUT_MODE"] = old

    def test_reference_prune_plan_finds_stale_cache_and_checkout_paths(self) -> None:
        from scripts.blueprint_harness import reference_prune_plan

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache_root = root / "cache"
            checkout_root = root / "by-worktree"
            (cache_root / "noperthedron").mkdir(parents=True)
            (cache_root / "oldproject").mkdir(parents=True)
            (checkout_root / "main" / "noperthedron").mkdir(parents=True)
            (checkout_root / "main" / "oldproject").mkdir(parents=True)
            (checkout_root / "stale-worktree" / "noperthedron").mkdir(parents=True)

            removals = reference_prune_plan(
                {"main", "cleanup-automation"},
                {"noperthedron"},
                cache_root,
                checkout_root,
            )

            self.assertEqual(
                {path.relative_to(root).as_posix() for path in removals},
                {
                    "cache/oldproject",
                    "by-worktree/main/oldproject",
                    "by-worktree/stale-worktree",
                },
            )


if __name__ == "__main__":
    unittest.main()
