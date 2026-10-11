from pathlib import Path

import pytest

from sevenflows.lint import banned_words, lint, lint_skill

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


def test_whitespace_only_description_is_missing(tmp_path: Path) -> None:
    skill = write_skill(tmp_path, "name: 7flows-test\ndescription: '   '\n")
    assert lint_skill(skill) == ["7flows-test: description is missing"]


def test_frontmatter_that_is_not_a_mapping_is_no_frontmatter(tmp_path: Path) -> None:
    skill = write_skill(tmp_path, "- name\n- description\n")
    assert lint_skill(skill) == ["7flows-test: SKILL.md has no frontmatter"]


def test_malformed_yaml_is_a_finding_not_a_crash(tmp_path: Path) -> None:
    skill = write_skill(tmp_path, "name: 7flows-test\ndescription: Use when: belief\n")
    assert lint_skill(skill) == ["7flows-test: frontmatter is not valid YAML"]


def test_a_skill_folder_without_skill_md_is_a_finding(tmp_path: Path) -> None:
    (tmp_path / "7flows-test").mkdir()
    assert lint_skill(tmp_path / "7flows-test") == ["7flows-test: SKILL.md is missing"]


def test_windows_line_endings_still_read_the_frontmatter(tmp_path: Path) -> None:
    skill = tmp_path / "7flows-test"
    skill.mkdir()
    crlf = f"---\n{VALID}---\n\nBody.\n".replace("\n", "\r\n")
    (skill / "SKILL.md").write_bytes(crlf.encode())
    assert lint_skill(skill) == []


VOICE = (
    "# K's voice\n\n## Banned words\n\n"
    "| Banned | Say instead |\n|---|---|\n"
    "| Leverage | Use |\n| Align | Agree |\n| Great question | (cut it) |\n"
)


def make_words_repo(root: Path, voice: str | None = VOICE) -> None:
    (root / "method").mkdir()
    if voice is not None:
        (root / "method" / "voice.md").write_text(voice)
    (root / "skills").mkdir()
    write_skill(root / "skills", VALID)


def test_banned_words_come_from_the_voice_table(tmp_path: Path) -> None:
    (tmp_path / "voice.md").write_text(VOICE)
    assert banned_words(tmp_path / "voice.md") == [
        "leverage",
        "align",
        "great question",
    ]


def test_a_banned_word_in_method_text_is_a_finding_with_its_line(
    tmp_path: Path,
) -> None:
    make_words_repo(tmp_path)
    (tmp_path / "method" / "k.md").write_text("# K\n\nK helps you leverage time.\n")
    assert lint(tmp_path) == ["method/k.md:3: banned word 'leverage'"]


def test_inflections_and_case_are_caught_but_not_words_inside_words(
    tmp_path: Path,
) -> None:
    make_words_repo(tmp_path)
    (tmp_path / "method" / "k.md").write_text(
        "Teams ALIGNED.\nA malign realignment.\nGreat Question!\n"
    )
    assert lint(tmp_path) == [
        "method/k.md:1: banned word 'align'",
        "method/k.md:3: banned word 'great question'",
    ]


def test_a_banned_word_in_a_skill_is_a_finding(tmp_path: Path) -> None:
    make_words_repo(tmp_path)
    skill_md = tmp_path / "skills" / "7flows-test" / "SKILL.md"
    skill_md.write_text(skill_md.read_text() + "Leverage it.\n")
    assert lint(tmp_path) == ["skills/7flows-test/SKILL.md:7: banned word 'leverage'"]


def test_the_list_itself_its_copies_and_its_built_region_are_exempt(
    tmp_path: Path,
) -> None:
    make_words_repo(tmp_path)
    skill = tmp_path / "skills" / "7flows-test"
    (skill / "references").mkdir()
    (skill / "references" / "voice.md").write_text(VOICE)
    (skill / "SKILL.md").write_text(
        (skill / "SKILL.md").read_text()
        + "<!-- built from method/voice.md — edit there -->\n"
        + VOICE
        + "<!-- /built -->\nNever align.\n"
    )
    line = (skill / "SKILL.md").read_text().splitlines().index("Never align.") + 1
    assert lint(tmp_path) == [
        f"skills/7flows-test/SKILL.md:{line}: banned word 'align'"
    ]


def test_a_missing_voice_file_is_a_finding(tmp_path: Path) -> None:
    make_words_repo(tmp_path, voice=None)
    assert lint(tmp_path) == ["method/voice.md is missing — no banned words to check"]


def test_a_voice_file_without_the_table_is_a_finding(tmp_path: Path) -> None:
    make_words_repo(tmp_path, voice="# K's voice\n")
    assert lint(tmp_path) == ["method/voice.md lists no banned words"]


def test_skill_md_of_499_lines_passes_and_500_fails(tmp_path: Path) -> None:
    skill = write_skill(tmp_path, VALID)
    head = (skill / "SKILL.md").read_text()
    pad = 499 - head.count("\n")
    (skill / "SKILL.md").write_text(head + "x\n" * pad)
    assert lint_skill(skill) == []
    (skill / "SKILL.md").write_text(head + "x\n" * (pad + 1))
    assert lint_skill(skill) == ["7flows-test: SKILL.md is 500 lines, max 499"]


def test_british_spellings_and_forms_that_drop_the_final_e_are_caught(
    tmp_path: Path,
) -> None:
    voice = VOICE + "| Optimize | Improve |\n| Utilize | Use |\n"
    make_words_repo(tmp_path, voice)
    (tmp_path / "method" / "k.md").write_text(
        "Leveraging it.\nPrice optimisation.\nWe utilised it.\nAn eyelet.\n"
    )
    assert lint(tmp_path) == [
        "method/k.md:1: banned word 'leverage'",
        "method/k.md:2: banned word 'optimize'",
        "method/k.md:3: banned word 'utilize'",
    ]
