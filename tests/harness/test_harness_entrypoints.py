from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest


PACKAGE_ROOT = Path(__file__).resolve().parents[2]


class HarnessEntrypointSmokeTests(unittest.TestCase):
    def run_command(self, command: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            command,
            cwd=PACKAGE_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

    def test_blueprint_harness_help(self) -> None:
        result = self.run_command([sys.executable, "-m", "scripts.blueprint_harness", "--help"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("create-worktree", result.stdout)
        self.assertIn("land-main", result.stdout)

    def test_blueprint_reference_harness_help(self) -> None:
        result = self.run_command([sys.executable, "-m", "scripts.blueprint_reference_harness", "--help"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("generate", result.stdout)
        self.assertIn("sync", result.stdout)
        self.assertIn("edit", result.stdout)

    def test_generate_reference_wrapper_help(self) -> None:
        result = self.run_command(["bash", "scripts/generate-reference-blueprints.sh", "--help"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("python3 -m scripts.blueprint_reference_harness", result.stdout)

    def test_validate_reference_wrapper_help(self) -> None:
        result = self.run_command(["bash", "scripts/validate-reference-blueprints.sh", "--help"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("python3 -m scripts.blueprint_reference_harness", result.stdout)

    def test_project_template_fresh_repo_smoke_help(self) -> None:
        result = self.run_command([sys.executable, "scripts/check_project_template_fresh_repo.py", "--help"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("--site-output", result.stdout)


if __name__ == "__main__":
    unittest.main()
