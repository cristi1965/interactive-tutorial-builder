#!/usr/bin/env python3
"""Validate this repository's dependency-free Skill packaging contract."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

import yaml


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
LINK_RE = re.compile(r"\[[^]]+\]\(([^)]+)\)")


def parse_frontmatter(text: str) -> dict[str, str] | None:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None
    try:
        fields = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None
    return fields if isinstance(fields, dict) else None


def validate(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        return ["SKILL.md not found"]
    text = skill_file.read_text(encoding="utf-8")
    fields = parse_frontmatter(text)
    if fields is None:
        return ["invalid YAML-compatible frontmatter"]
    if set(fields) != {"name", "description"}:
        errors.append("frontmatter must contain only name and description")
    name = fields.get("name", "")
    description = fields.get("description", "")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name) or len(name) > 64 or name != skill_dir.name:
        errors.append("name must be valid hyphen-case and match the directory")
    if not isinstance(description, str) or not description or len(description) > 1024 or "<" in description or ">" in description:
        errors.append("description is missing or invalid")
    if "TODO" in text:
        errors.append("SKILL.md contains unfinished TODO text")
    for link in LINK_RE.findall(text):
        if "://" in link or link.startswith("#"):
            continue
        target = (skill_dir / link).resolve()
        try:
            target.relative_to(skill_dir.resolve())
        except ValueError:
            errors.append(f"linked resource escapes the skill directory: {link}")
            continue
        if not target.is_file():
            errors.append(f"linked resource does not exist: {link}")
    metadata = skill_dir / "agents/openai.yaml"
    if not metadata.is_file():
        errors.append("agents/openai.yaml not found")
    else:
        metadata_text = metadata.read_text(encoding="utf-8")
        if "$interactive-tutorial-builder" not in metadata_text or "TODO" in metadata_text:
            errors.append("agents/openai.yaml is incomplete")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", type=Path)
    args = parser.parse_args()
    errors = validate(args.skill_dir.resolve())
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: skill structure is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
