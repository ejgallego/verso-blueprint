from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.blueprint_harness_projects import (
    default_project_manifest,
    load_projects_manifest,
)
from scripts.blueprint_harness import OFFICIAL_BLUEPRINT_REQUIRE, rewrite_local_blueprint_dependency


PACKAGE_ROOT = Path(__file__).resolve().parents[2]


class BlueprintHarnessProjectsTests(unittest.TestCase):
    def test_default_manifest_contains_current_external_projects(self) -> None:
        manifest = default_project_manifest(PACKAGE_ROOT)
        projects = load_projects_manifest(manifest)

        self.assertEqual([project.project_id for project in projects], ["noperthedron", "spherepackingblueprint"])
        self.assertTrue(projects[0].git_checkout)
        self.assertEqual(projects[0].repository, "https://github.com/ejgallego/verso-noperthedron.git")
        self.assertEqual(projects[0].browser_tests_path, "tests/browser")
        self.assertEqual(projects[0].panel_regression_script, "tests/harness/noperthedron/check_blueprint_code_panels.py")

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


if __name__ == "__main__":
    unittest.main()
