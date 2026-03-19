from __future__ import annotations

import subprocess
from pathlib import Path


def format_command(command: list[str]) -> str:
    return " ".join(command)


def run(command: list[str], *, cwd: Path) -> None:
    print(f"[blueprint-harness] $ {format_command(command)}")
    subprocess.run(command, cwd=cwd, check=True)


def lean_low_priority_command(package_root: Path, *args: str) -> list[str]:
    return [str(package_root / "scripts" / "lean-low-priority"), *args]
