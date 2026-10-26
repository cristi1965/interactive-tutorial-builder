from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


CHECKER = load("check_repository", ROOT / "scripts/check_repository.py")
VALIDATOR = load("validate_skill", ROOT / "scripts/validate_skill.py")


class RepositoryChecksTest(unittest.TestCase):
    def test_detects_local_paths_in_binary_data(self):
        errors = CHECKER.scan_data("artifact.bin", b"\x00/App" + b"lications/workspace/private\x00")
        self.assertTrue(any("local absolute path" in error for error in errors))

    def test_detects_common_token_families(self):
        samples = (
            b"github" + b"_pat_ABCDEFGHIJKLMNOPQRSTUVWXYZ123456",
            b"sk" + b"-proj-ABCDEFGHIJKLMNOPQRSTUVWXYZ123456",
            b"xox" + b"b-1234567890-ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        )
        for sample in samples:
            with self.subTest(sample=sample):
                self.assertTrue(CHECKER.scan_data("secret.txt", sample))

    def test_current_skill_structure_is_valid(self):
        errors = VALIDATOR.validate(ROOT / "skills/interactive-tutorial-builder")
        self.assertEqual([], errors)

    def test_validator_rejects_missing_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            skill = Path(directory) / "demo-skill"
            (skill / "agents").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: demo-skill\ndescription: Demo skill.\n---\n[missing](references/no.md)\n",
                encoding="utf-8",
            )
            (skill / "agents/openai.yaml").write_text(
                "interface:\n  default_prompt: 'Use $interactive-tutorial-builder.'\n",
                encoding="utf-8",
            )
            errors = VALIDATOR.validate(skill)
            self.assertTrue(any("does not exist" in error for error in errors))

    def test_validator_rejects_invalid_yaml(self):
        with tempfile.TemporaryDirectory() as directory:
            skill = Path(directory) / "demo-skill"
            (skill / "agents").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: demo-skill\ndescription: [\n---\nBody\n",
                encoding="utf-8",
            )
            (skill / "agents/openai.yaml").write_text(
                "interface:\n  default_prompt: 'Use $interactive-tutorial-builder.'\n",
                encoding="utf-8",
            )
            self.assertTrue(VALIDATOR.validate(skill))


if __name__ == "__main__":
    unittest.main()
