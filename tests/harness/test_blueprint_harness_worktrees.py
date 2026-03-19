from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from scripts.blueprint_harness_worktrees import (
    METADATA_DIRNAME,
    metadata_path,
    parse_git_worktree_porcelain,
    resolve_worktree_name,
    sync_worktree_registry,
)


class BlueprintHarnessWorktreesTests(unittest.TestCase):
    def test_parse_git_worktree_porcelain(self) -> None:
        repo_root = Path("/tmp/repo")
        text = """
worktree /tmp/repo
HEAD abc
branch refs/heads/main

worktree /tmp/repo/.worktrees/harness-rework
HEAD def
branch refs/heads/feat/harness-rework

worktree /tmp/repo/.worktrees/detached-edit
HEAD 1234567
"""
        worktrees = parse_git_worktree_porcelain(text, repo_root)

        self.assertEqual([(worktree.name, worktree.branch, worktree.head) for worktree in worktrees], [
            ("main", "main", "abc"),
            ("harness-rework", "feat/harness-rework", "def"),
            ("detached-edit", None, "1234567"),
        ])
        self.assertTrue(worktrees[0].root_checkout)
        self.assertFalse(worktrees[1].root_checkout)

    def test_resolve_worktree_name_prefers_explicit_name(self) -> None:
        self.assertEqual(resolve_worktree_name("harness-rework", "doc-polish"), "doc-polish")
        self.assertEqual(resolve_worktree_name("harness-rework", None), "harness-rework")
        self.assertEqual(resolve_worktree_name(None, None), "main")

    def test_sync_worktree_registry_creates_local_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            worktree_dir = repo_root / ".worktrees" / "demo"
            worktree_dir.mkdir(parents=True)
            subprocess_text = f"""
worktree {repo_root}
HEAD abc
branch refs/heads/main

worktree {worktree_dir}
HEAD def
branch refs/heads/feat/demo
"""

            import scripts.blueprint_harness_worktrees as worktrees_mod

            original = worktrees_mod.git_worktrees
            try:
                worktrees_mod.git_worktrees = lambda _repo_root: parse_git_worktree_porcelain(subprocess_text, repo_root)
                records, registry = sync_worktree_registry(repo_root)
            finally:
                worktrees_mod.git_worktrees = original

            self.assertEqual([record.name for record in records], ["main", "demo"])
            self.assertTrue(metadata_path(repo_root, "main").exists())
            self.assertTrue(metadata_path(repo_root, "demo").exists())
            self.assertEqual(metadata_path(repo_root, "demo"), repo_root / ".worktrees" / METADATA_DIRNAME / "demo.json")
            self.assertFalse((worktree_dir / ".codex-worktree.json").exists())
            self.assertTrue(registry.exists())


if __name__ == "__main__":
    unittest.main()
