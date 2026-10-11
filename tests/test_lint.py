from pathlib import Path

import pytest

from sevenflows.lint import lint_skill

VALID = "name: 7flows-test\ndescription: Test a belief before you build on it.\n"


def write_skill(root: Path, frontmatter: str, folder: str = "7flows-test") -> Path:
    skill = root / folder
    skill.mkdir()
    (skill / "SKILL.md").write_text(f"---\n{frontmatter}---\n\nBody.\n")
    return skill


def test_valid_skill_has_no_findings(tmp_path: Path) -> None:
    assert lint_skill(write_skill(tmp_path, VALID)) == []


def test_all_six_spec_fields_are_allowed(tmp_path: Path) -> None:
    frontmatter = VALID + (
        "license: Apache-2.0\ncompatibility: Any agent.\n"
        "metadata:\n  version: '1'\nallowed-tools: Read\n"
    )
    assert lint_skill(write_skill(tmp_path, frontmatter)) == []


def test_a_seventh_frontmatter_key_fails(tmp_path: Path) -> None:
    findings = lint_skill(write_skill(tmp_path, VALID + "when_to_use: always\n"))
    assert findings == ["7flows-test: unknown frontmatter key 'when_to_use'"]


def test_description_of_200_chars_passes(tmp_path: Path) -> None:
    frontmatter = f"name: 7flows-test\ndescription: {'x' * 200}\n"
    assert lint_skill(write_skill(tmp_path, frontmatter)) == []


def test_description_of_201_chars_fails(tmp_path: Path) -> None:
    frontmatter = f"name: 7flows-test\ndescription: {'x' * 201}\n"
    assert lint_skill(write_skill(tmp_path, frontmatter)) == [
        "7flows-test: description is 201 chars, max 200"
    ]


def test_missing_description_fails(tmp_path: Path) -> None:
    findings = lint_skill(write_skill(tmp_path, "name: 7flows-test\n"))
    assert findings == ["7flows-test: description is missing"]


def test_name_must_match_the_folder(tmp_path: Path) -> None:
    findings = lint_skill(write_skill(tmp_path, VALID, folder="7flows-make"))
    assert findings == ["7flows-make: name '7flows-test' does not match folder"]


@pytest.mark.parametrize("name", ["Test", "-test", "test-", "te--st", "a" * 65])
def test_malformed_names_fail(tmp_path: Path, name: str) -> None:
    frontmatter = f"name: {name}\ndescription: A belief to test.\n"
    findings = lint_skill(write_skill(tmp_path, frontmatter, folder=name.lower()))
    assert any("is not a valid skill name" in f for f in findings)


def test_missing_frontmatter_fails(tmp_path: Path) -> None:
    skill = tmp_path / "7flows-test"
    skill.mkdir()
    (skill / "SKILL.md").write_text("# No frontmatter\n")
    assert lint_skill(skill) == ["7flows-test: SKILL.md has no frontmatter"]
