from pathlib import Path

import pytest

from sevenflows.build import build, check

MANIFEST = {"7flows-test": ["test/toile.md"]}


def make_tree(root: Path) -> None:
    (root / "method" / "test").mkdir(parents=True)
    (root / "method" / "test" / "toile.md").write_text("# The Toile\n")
    (root / "skills" / "7flows-test").mkdir(parents=True)


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
    assert check(tmp_path, MANIFEST) == [
        tmp_path / "skills" / "7flows-test" / "references" / "toile.md"
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
