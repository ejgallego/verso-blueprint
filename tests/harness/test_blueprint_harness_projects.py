from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.blueprint_harness_projects import (
    HarnessProject,
    default_project_manifest,
    load_projects_manifest,
)
from scripts.blueprint_harness_references import (
    OFFICIAL_BLUEPRINT_REQUIRE,
    clone_git_project,
    discard_untracked_project_manifest,
    default_reference_edit_base,
    reference_update_command,
    rewrite_local_blueprint_dependency,
    tracked_project_manifest_path,
    update_git_checkout,
    use_shared_reference_checkout,
)


PACKAGE_ROOT = Path(__file__).resolve().parents[2]


class BlueprintHarnessProjectsTests(unittest.TestCase):
    def init_git_repo(self, root: Path) -> None:
        subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def run_git(self, root: Path, *args: str) -> None:
        subprocess.run(["git", *args], cwd=root, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def commit(self, root: Path, message: str) -> str:
        self.run_git(root, "config", "user.name", "Test User")
        self.run_git(root, "config", "user.email", "test@example.com")
        self.run_git(root, "commit", "-m", message)
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()

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

    def test_tracked_project_manifest_path_accepts_git_tracked_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            self.init_git_repo(project_dir)
            manifest = project_dir / "lake-manifest.json"
            manifest.write_text("{}\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "lake-manifest.json"],
                cwd=project_dir,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            self.assertEqual(tracked_project_manifest_path(project_dir), manifest)

    def test_tracked_project_manifest_path_ignores_untracked_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            self.init_git_repo(project_dir)
            manifest = project_dir / "lake-manifest.json"
            manifest.write_text("{}\n", encoding="utf-8")

            self.assertIsNone(tracked_project_manifest_path(project_dir))

    def test_discard_untracked_project_manifest_removes_generated_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            self.init_git_repo(project_dir)
            manifest = project_dir / "lake-manifest.json"
            manifest.write_text("{}\n", encoding="utf-8")

            discard_untracked_project_manifest(project_dir)

            self.assertFalse(manifest.exists())

    def test_discard_untracked_project_manifest_preserves_tracked_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            self.init_git_repo(project_dir)
            manifest = project_dir / "lake-manifest.json"
            manifest.write_text("{}\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "lake-manifest.json"],
                cwd=project_dir,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            discard_untracked_project_manifest(project_dir)

            self.assertTrue(manifest.exists())

    def test_reference_update_command_targets_blueprint_when_manifest_is_committed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            self.init_git_repo(project_dir)
            manifest = project_dir / "lake-manifest.json"
            manifest.write_text("{}\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "lake-manifest.json"],
                cwd=project_dir,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            command = reference_update_command(PACKAGE_ROOT, project_dir)

            self.assertEqual(command[-3:], ["lake", "update", "VersoBlueprint"])

    def test_reference_update_command_falls_back_to_full_update_without_tracked_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            self.init_git_repo(project_dir)

            command = reference_update_command(PACKAGE_ROOT, project_dir)

            self.assertEqual(command[-2:], ["lake", "update"])

    def test_project_template_manifest_keeps_verso_and_subverso_in_sync_with_root(self) -> None:
        root_manifest = json.loads((PACKAGE_ROOT / "lake-manifest.json").read_text(encoding="utf-8"))
        template_manifest = json.loads((PACKAGE_ROOT / "project_template" / "lake-manifest.json").read_text(encoding="utf-8"))

        def package_rev(manifest_data: dict, package_name: str) -> str:
            package = next(entry for entry in manifest_data["packages"] if entry["name"] == package_name)
            rev = package.get("rev")
            self.assertIsInstance(rev, str)
            return rev

        self.assertEqual(package_rev(template_manifest, "verso"), package_rev(root_manifest, "verso"))
        self.assertEqual(package_rev(template_manifest, "subverso"), package_rev(root_manifest, "subverso"))

    def test_clone_git_project_checks_out_commit_ref_without_branch_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            remote = root / "remote.git"
            seed = root / "seed"
            checkout = root / "checkout"

            subprocess.run(["git", "init", "--bare", str(remote)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            seed.mkdir()
            self.init_git_repo(seed)
            (seed / "file.txt").write_text("first\n", encoding="utf-8")
            self.run_git(seed, "add", "file.txt")
            first = self.commit(seed, "first")
            (seed / "file.txt").write_text("second\n", encoding="utf-8")
            self.run_git(seed, "commit", "-am", "second")
            self.run_git(seed, "branch", "-M", "main")
            self.run_git(seed, "remote", "add", "origin", str(remote))
            self.run_git(seed, "push", "-u", "origin", "main")

            project = HarnessProject(
                project_id="external-blueprint",
                source_kind="git_checkout",
                project_root=".",
                build_target=None,
                generator=None,
                repository=str(remote),
                ref=first,
                build_command=None,
                generate_command=("lake", "exe", "blueprint-gen"),
                site_subdir="html-multi",
                panel_regression_script=None,
                browser_tests_path=None,
                description=None,
            )

            clone_git_project(project, checkout, cwd=root)

            head = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=checkout,
                check=True,
                text=True,
                capture_output=True,
            ).stdout.strip()
            self.assertEqual(head, first)

    def test_default_reference_edit_base_uses_detached_commit_for_sha_ref(self) -> None:
        project = HarnessProject(
            project_id="external-blueprint",
            source_kind="git_checkout",
            project_root=".",
            build_target=None,
            generator=None,
            repository="https://github.com/example/external-blueprint.git",
            ref="9b50e39c17434ee1a574fd27ed97006adfdc5dc1",
            build_command=None,
            generate_command=("lake", "exe", "blueprint-gen"),
            site_subdir="html-multi",
            panel_regression_script=None,
            browser_tests_path=None,
            description=None,
        )

        self.assertEqual(default_reference_edit_base(project), project.ref)

    def test_update_git_checkout_discards_stale_untracked_manifest_before_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            remote = root / "remote.git"
            seed = root / "seed"
            checkout = root / "checkout"

            subprocess.run(["git", "init", "--bare", str(remote)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            seed.mkdir()
            self.init_git_repo(seed)
            (seed / "lakefile.lean").write_text("import Lake\n", encoding="utf-8")
            self.run_git(seed, "add", "lakefile.lean")
            self.commit(seed, "seed")
            self.run_git(seed, "branch", "-M", "main")
            self.run_git(seed, "remote", "add", "origin", str(remote))
            self.run_git(seed, "push", "-u", "origin", "main")

            subprocess.run(["git", "clone", str(remote), str(checkout)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            (checkout / "lake-manifest.json").write_text("{}\n", encoding="utf-8")

            (seed / "lake-manifest.json").write_text('{"version":"1.1.0"}\n', encoding="utf-8")
            self.run_git(seed, "add", "lake-manifest.json")
            target = self.commit(seed, "add manifest")
            self.run_git(seed, "push", "origin", "main")

            project = HarnessProject(
                project_id="external-blueprint",
                source_kind="git_checkout",
                project_root=".",
                build_target=None,
                generator=None,
                repository=str(remote),
                ref=target,
                build_command=None,
                generate_command=("lake", "exe", "blueprint-gen"),
                site_subdir="html-multi",
                panel_regression_script=None,
                browser_tests_path=None,
                description=None,
            )

            update_git_checkout(project, checkout)

            manifest = checkout / "lake-manifest.json"
            self.assertEqual(tracked_project_manifest_path(checkout), manifest)
            self.assertEqual(manifest.read_text(encoding="utf-8"), '{"version":"1.1.0"}\n')

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
