from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.blueprint_test_blueprints import (
    StandaloneTestBlueprint,
    default_test_blueprint_manifest,
    find_test_blueprint,
    load_test_blueprints_manifest,
)


PACKAGE_ROOT = Path(__file__).resolve().parents[2]


class StandaloneTestBlueprintTests(unittest.TestCase):
    def test_default_manifest_contains_preview_runtime_showcase(self) -> None:
        fixtures = load_test_blueprints_manifest(default_test_blueprint_manifest(PACKAGE_ROOT))
        fixture = find_test_blueprint(fixtures, "preview_runtime_showcase")

        self.assertEqual(fixture.slug, "preview_runtime_showcase")
        self.assertEqual(fixture.kind, "standalone_project")
        self.assertEqual(fixture.category, "Preview Runtime")
        self.assertEqual(fixture.project_root, "tests/test_blueprints/preview_runtime_showcase")
        self.assertEqual(fixture.browser_tests_path, "tests/browser")
        self.assertEqual(
            fixture.panel_regression_script,
            "tests/harness/preview_runtime_showcase/check_blueprint_code_panels.py",
        )

    def test_duplicate_fixture_slugs_are_rejected(self) -> None:
        manifest_data = {
            "version": 1,
            "fixtures": [
                {
                    "slug": "dup",
                    "title": "One",
                    "category": "Preview Runtime",
                    "summary": "First",
                    "project_root": "tests/test_blueprints/one",
                    "generate_command": ["lake", "exe", "blueprint-gen", "--output", "{output_dir}"],
                },
                {
                    "slug": "dup",
                    "title": "Two",
                    "category": "Preview Runtime",
                    "summary": "Second",
                    "project_root": "tests/test_blueprints/two",
                    "generate_command": ["lake", "exe", "blueprint-gen", "--output", "{output_dir}"],
                },
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "test_blueprints.json"
            manifest.write_text(json.dumps(manifest_data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate fixture slug"):
                load_test_blueprints_manifest(manifest)

    def test_missing_generate_command_is_rejected(self) -> None:
        manifest_data = {
            "version": 1,
            "fixtures": [
                {
                    "slug": "missing",
                    "title": "Missing Generate",
                    "category": "Preview Runtime",
                    "summary": "Bad fixture",
                    "project_root": "tests/test_blueprints/bad",
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "test_blueprints.json"
            manifest.write_text(json.dumps(manifest_data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "generate_command"):
                load_test_blueprints_manifest(manifest)

    def test_meta_uses_unified_shape(self) -> None:
        fixture = StandaloneTestBlueprint(
            slug="preview_runtime_showcase",
            title="Preview Runtime Showcase",
            category="Preview Runtime",
            summary="Summary",
            project_root="tests/test_blueprints/preview_runtime_showcase",
            build_command=("lake", "build"),
            generate_command=("lake", "exe", "blueprint-gen", "--output", "{output_dir}"),
            panel_regression_script=None,
            browser_tests_path=None,
        )
        self.assertEqual(
            fixture.meta,
            {
                "slug": "preview_runtime_showcase",
                "title": "Preview Runtime Showcase",
                "category": "Preview Runtime",
                "summary": "Summary",
                "kind": "standalone_project",
            },
        )


if __name__ == "__main__":
    unittest.main()
