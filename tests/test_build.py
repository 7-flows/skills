from pathlib import Path

import pytest

from sevenflows.build import LICENCES, build, check

MANIFEST = {"7flows-test": ["test/toile.md"]}


def make_tree(root: Path) -> None:
    (root / "method" / "test").mkdir(parents=True)
    (root / "method" / "test" / "toile.md").write_text("# The Toile\n")
    (root / "skills" / "7flows-test").mkdir(parents=True)
    for name in LICENCES:
        (root / name).write_text(f"{name} text\n")


def test_build_copies_method_files_into_the_skill(tmp_path: Path) -> None:
    make_tree(tmp_path)
    build(tmp_path, MANIFEST)
    copied = tmp_path / "skills" / "7flows-test" / "references" / "toile.md"
    assert copied.read_text().endswith("# The Toile\n")
    assert "method/test/toile.md" in copied.read_text()


def test_check_is_clean_right_after_build(tmp_path: Path) -> None:
    make_tree(tmp_path)
    build(tmp_path, MANIFEST)
    assert check(tmp_path, MANIFEST) == []


def test_check_reports_a_copy_edited_by_hand(tmp_path: Path) -> None:
    make_tree(tmp_path)
    build(tmp_path, MANIFEST)
    copied = tmp_path / "skills" / "7flows-test" / "references" / "toile.md"
    copied.write_text("edited in the wrong place\n")
    assert check(tmp_path, MANIFEST) == [copied]


def test_check_reports_a_source_change_not_yet_built(tmp_path: Path) -> None:
    make_tree(tmp_path)
    build(tmp_path, MANIFEST)
    (tmp_path / "method" / "test" / "toile.md").write_text("# The Toile, recut\n")
    assert check(tmp_path, MANIFEST) == [
        tmp_path / "skills" / "7flows-test" / "references" / "toile.md"
    ]


def test_check_reports_a_missing_copy(tmp_path: Path) -> None:
    make_tree(tmp_path)
    skill = tmp_path / "skills" / "7flows-test"
    assert check(tmp_path, MANIFEST) == [
        skill / "LICENSE",
        skill / "LICENSE-METHOD",
        skill / "references" / "toile.md",
    ]


def test_build_removes_references_no_longer_in_the_manifest(tmp_path: Path) -> None:
    make_tree(tmp_path)
    stale = tmp_path / "skills" / "7flows-test" / "references" / "old.md"
    stale.parent.mkdir()
    stale.write_text("left over\n")
    assert stale in check(tmp_path, MANIFEST)
    build(tmp_path, MANIFEST)
    assert not stale.exists()


def test_two_sources_with_one_basename_in_one_skill_are_refused(tmp_path: Path) -> None:
    make_tree(tmp_path)
    (tmp_path / "method" / "toile.md").write_text("# Another toile\n")
    clash = {"7flows-test": ["test/toile.md", "toile.md"]}
    with pytest.raises(ValueError, match=r"toile\.md"):
        check(tmp_path, clash)


def test_check_reports_references_of_a_skill_left_out_of_the_manifest(
    tmp_path: Path,
) -> None:
    make_tree(tmp_path)
    orphan = tmp_path / "skills" / "7flows-old" / "references" / "toile.md"
    orphan.parent.mkdir(parents=True)
    orphan.write_text("left over\n")
    build(tmp_path, MANIFEST)
    assert not orphan.exists()
    orphan.parent.mkdir(parents=True, exist_ok=True)
    orphan.write_text("left over\n")
    assert check(tmp_path, MANIFEST) == [orphan]


CORED = (
    "# The Toile\n\nWhy.\n\n<!-- core -->\n## Fields\n1. Assumption\n<!-- /core -->\n"
)
HEAD = "---\nname: 7flows-test\ndescription: Test a belief.\n---\n\n# Test\n\nRun it.\n"


def make_cored_tree(root: Path, source: str = CORED) -> Path:
    make_tree(root)
    (root / "method" / "test" / "toile.md").write_text(source)
    skill_md = root / "skills" / "7flows-test" / "SKILL.md"
    skill_md.write_text(HEAD)
    return skill_md


def test_build_writes_the_core_into_skill_md_under_the_head(tmp_path: Path) -> None:
    skill_md = make_cored_tree(tmp_path)
    build(tmp_path, MANIFEST)
    assert skill_md.read_text() == (
        HEAD + "\n<!-- built from method/test/toile.md — edit there -->\n"
        "## Fields\n1. Assumption\n<!-- /built -->\n"
    )


def test_build_is_stable_on_a_second_run(tmp_path: Path) -> None:
    skill_md = make_cored_tree(tmp_path)
    build(tmp_path, MANIFEST)
    first = skill_md.read_text()
    build(tmp_path, MANIFEST)
    assert skill_md.read_text() == first
    assert check(tmp_path, MANIFEST) == []


def test_check_reports_a_hand_edited_inline_region(tmp_path: Path) -> None:
    skill_md = make_cored_tree(tmp_path)
    build(tmp_path, MANIFEST)
    skill_md.write_text(skill_md.read_text().replace("Assumption", "Hunch"))
    assert check(tmp_path, MANIFEST) == [skill_md]


def test_check_reports_a_core_change_not_yet_built(tmp_path: Path) -> None:
    skill_md = make_cored_tree(tmp_path)
    build(tmp_path, MANIFEST)
    (tmp_path / "method" / "test" / "toile.md").write_text(CORED.replace("1.", "One."))
    assert skill_md in check(tmp_path, MANIFEST)


def test_hand_written_text_around_the_region_survives_a_rebuild(tmp_path: Path) -> None:
    skill_md = make_cored_tree(tmp_path)
    build(tmp_path, MANIFEST)
    skill_md.write_text(skill_md.read_text() + "\n## After\n\nKept.\n")
    (tmp_path / "method" / "test" / "toile.md").write_text(CORED.replace("1.", "One."))
    build(tmp_path, MANIFEST)
    text = skill_md.read_text()
    assert text.startswith(HEAD)
    assert "One. Assumption\n<!-- /built -->\n\n## After\n\nKept.\n" in text


def test_several_core_regions_join_in_source_order(tmp_path: Path) -> None:
    source = (
        CORED + "\nAside.\n\n<!-- core -->\n## Done\nTwo sentences.\n<!-- /core -->\n"
    )
    skill_md = make_cored_tree(tmp_path, source)
    build(tmp_path, MANIFEST)
    assert "1. Assumption\n\n## Done\nTwo sentences.\n<!-- /built -->" in (
        skill_md.read_text()
    )
    assert "Aside." not in skill_md.read_text()


def test_a_source_without_core_leaves_skill_md_alone(tmp_path: Path) -> None:
    skill_md = make_cored_tree(tmp_path, "# The Toile\n")
    build(tmp_path, MANIFEST)
    assert skill_md.read_text() == HEAD


def test_a_region_whose_source_left_the_manifest_is_removed(tmp_path: Path) -> None:
    skill_md = make_cored_tree(tmp_path)
    build(tmp_path, MANIFEST)
    (tmp_path / "method" / "test" / "toile.md").write_text("# The Toile\n")
    copy = tmp_path / "skills" / "7flows-test" / "references" / "toile.md"
    assert check(tmp_path, MANIFEST) == [copy, skill_md]
    build(tmp_path, MANIFEST)
    assert skill_md.read_text() == HEAD


def test_an_unclosed_core_marker_is_refused(tmp_path: Path) -> None:
    make_cored_tree(tmp_path, "<!-- core -->\n## Fields\n")
    with pytest.raises(ValueError, match=r"unclosed"):
        check(tmp_path, MANIFEST)


def test_a_core_without_skill_md_is_refused(tmp_path: Path) -> None:
    make_cored_tree(tmp_path).unlink()
    with pytest.raises(ValueError, match=r"SKILL\.md"):
        check(tmp_path, MANIFEST)


def test_a_skill_md_whose_final_newline_was_trimmed_builds_in_one_pass(
    tmp_path: Path,
) -> None:
    skill_md = make_cored_tree(tmp_path)
    build(tmp_path, MANIFEST)
    skill_md.write_text(skill_md.read_text().rstrip("\n"))
    build(tmp_path, MANIFEST)
    assert skill_md.read_text().count("<!-- built from") == 1
    assert check(tmp_path, MANIFEST) == []


def test_a_duplicated_region_is_built_once(tmp_path: Path) -> None:
    skill_md = make_cored_tree(tmp_path)
    build(tmp_path, MANIFEST)
    built = skill_md.read_text()
    region = built[len(HEAD) :]
    skill_md.write_text(built + region)
    build(tmp_path, MANIFEST)
    assert skill_md.read_text() == built


def test_build_puts_both_licence_texts_in_every_skill(tmp_path: Path) -> None:
    make_tree(tmp_path)
    build(tmp_path, MANIFEST)
    skill = tmp_path / "skills" / "7flows-test"
    assert (skill / "LICENSE").read_text() == "LICENSE text\n"
    assert (skill / "LICENSE-METHOD").read_text() == "LICENSE-METHOD text\n"


def test_check_reports_a_licence_text_changed_at_the_root(tmp_path: Path) -> None:
    make_tree(tmp_path)
    build(tmp_path, MANIFEST)
    (tmp_path / "LICENSE-METHOD").write_text("a newer text\n")
    assert check(tmp_path, MANIFEST) == [
        tmp_path / "skills" / "7flows-test" / "LICENSE-METHOD"
    ]


def test_a_missing_root_licence_is_refused(tmp_path: Path) -> None:
    make_tree(tmp_path)
    (tmp_path / "LICENSE").unlink()
    with pytest.raises(ValueError, match="LICENSE is missing"):
        build(tmp_path, MANIFEST)


def test_every_copied_reference_names_the_method_licence(tmp_path: Path) -> None:
    make_tree(tmp_path)
    build(tmp_path, MANIFEST)
    copied = tmp_path / "skills" / "7flows-test" / "references" / "toile.md"
    assert "CC BY-SA 4.0" in copied.read_text().splitlines()[0]
