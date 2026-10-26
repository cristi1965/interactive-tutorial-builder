#!/usr/bin/env python3
"""Run lightweight public-repository hygiene checks without dependencies."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_BYTES = 1024 * 1024
SKILL = ROOT / "skills/interactive-tutorial-builder/SKILL.md"
SELF = Path(__file__).resolve()
SKIP_PARTS = {".git"}
FORBIDDEN_PATHS = ("/Users/", "/Applications/", "C:\\Users\\")
SECRET_PATTERNS = (
    re.compile(rb"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(rb"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(rb"sk-(?:proj-)?[A-Za-z0-9_-]{20,}"),
    re.compile(rb"xox[baprs]-[A-Za-z0-9-]{20,}"),
    re.compile(rb"AKIA[0-9A-Z]{16}"),
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)


def files() -> list[Path]:
    if (ROOT / ".git").exists():
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
        return [ROOT / item.decode("utf-8") for item in result.stdout.split(b"\0") if item]
    return [
        path for path in ROOT.rglob("*")
        if path.is_file() and not any(part in SKIP_PARTS for part in path.relative_to(ROOT).parts)
    ]


def scan_data(relative: str, data: bytes) -> list[str]:
    errors: list[str] = []
    for marker in FORBIDDEN_PATHS:
        if marker.encode("utf-8") in data:
            errors.append(f"local absolute path in {relative}: {marker}")
    for pattern in SECRET_PATTERNS:
        if pattern.search(data):
            errors.append(f"possible secret in {relative}: {pattern.pattern.decode('ascii')}")
    return errors


def main() -> int:
    errors: list[str] = []
    repository_files = files()
    for path in repository_files:
        relative = path.relative_to(ROOT).as_posix()
        if path.stat().st_size > MAX_FILE_BYTES:
            errors.append(f"large file over 1 MiB: {relative}")
        if path.resolve() == SELF:
            continue
        data = path.read_bytes()
        errors.extend(scan_data(relative, data))

    skill_text = SKILL.read_text(encoding="utf-8") if SKILL.is_file() else ""
    if not skill_text.startswith("---\nname: interactive-tutorial-builder\ndescription:"):
        errors.append("SKILL.md frontmatter is missing or malformed")
    if "TODO" in skill_text:
        errors.append("SKILL.md contains unfinished TODO text")

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: checked {len(repository_files)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
