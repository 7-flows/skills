import stat
import zipfile
from pathlib import Path

import pytest

from sevenflows.build import LICENCES, build
from sevenflows.package import package

MANIFEST = {"7flows-test": ["test/toile.md"], "7flows": ["k.md"]}


def make_repo(root: Path) -> None:
    for name in LICENCES:
        (root / name).write_text(f"{name} text\n")
    for skill, sources in MANIFEST.items():
        (root / "skills" / skill).mkdir(parents=True)
        (root / "skills" / skill / "SKILL.md").write_text(f"---\nname: {skill}\n---\n")
        for source in sources:
            (root / "method" / source).parent.mkdir(parents=True, exist_ok=True)
            (root / "method" / source).write_text("# Source\n")
    build(root, MANIFEST)


def names(archive: Path) -> list[str]:
    with zipfile.ZipFile(archive) as z:
        return z.namelist()


def test_one_zip_per_skill_with_the_skill_folder_at_the_top(tmp_path: Path) -> None:
    make_repo(tmp_path)
    archives = package(tmp_path, MANIFEST)
    assert archives == [
        tmp_path / "dist" / "7flows-test.zip",
        tmp_path / "dist" / "7flows.zip",
    ]
    for archive in archives:
        skill = archive.stem
        assert {n.split("/")[0] for n in names(archive)} == {skill}
        assert f"{skill}/SKILL.md" in names(archive)


def test_every_zip_carries_both_licence_texts(tmp_path: Path) -> None:
    make_repo(tmp_path)
    for archive in package(tmp_path, MANIFEST):
        with zipfile.ZipFile(archive) as z:
            assert z.read(f"{archive.stem}/LICENSE") == b"LICENSE text\n"
            assert z.read(f"{archive.stem}/LICENSE-METHOD") == b"LICENSE-METHOD text\n"


def test_the_skill_files_are_all_there_and_caches_are_left_out(tmp_path: Path) -> None:
    make_repo(tmp_path)
    skill = tmp_path / "skills" / "7flows-test"
    (skill / "scripts" / "__pycache__").mkdir(parents=True)
    (skill / "scripts" / "close_call.py").write_text("print()\n")
    (skill / "scripts" / "__pycache__" / "close_call.pyc").write_bytes(b"\0")
    (skill / ".DS_Store").write_bytes(b"\0")
    package(tmp_path, MANIFEST)
    assert sorted(names(tmp_path / "dist" / "7flows-test.zip")) == [
        "7flows-test/LICENSE",
        "7flows-test/LICENSE-METHOD",
        "7flows-test/SKILL.md",
        "7flows-test/references/toile.md",
        "7flows-test/scripts/close_call.py",
    ]


def test_packing_twice_gives_the_same_bytes(tmp_path: Path) -> None:
    make_repo(tmp_path)
    first = [a.read_bytes() for a in package(tmp_path, MANIFEST)]
    second = [a.read_bytes() for a in package(tmp_path, MANIFEST)]
    assert first == second


def test_stale_copies_are_never_packed(tmp_path: Path) -> None:
    make_repo(tmp_path)
    (tmp_path / "method" / "k.md").write_text("# Recut\n")
    with pytest.raises(ValueError, match="run `sevenflows build`"):
        package(tmp_path, MANIFEST)
    assert not (tmp_path / "dist").exists()


def test_entries_are_plain_files_with_their_modes(tmp_path: Path) -> None:
    make_repo(tmp_path)
    script = tmp_path / "skills" / "7flows-test" / "run.py"
    script.write_text("print()\n")
    script.chmod(0o755)
    package(tmp_path, MANIFEST)
    with zipfile.ZipFile(tmp_path / "dist" / "7flows-test.zip") as z:
        modes = {i.filename: i.external_attr >> 16 for i in z.infolist()}
    assert all(stat.S_ISREG(mode) for mode in modes.values())
    assert stat.S_IMODE(modes["7flows-test/run.py"]) == 0o755
    assert stat.S_IMODE(modes["7flows-test/SKILL.md"]) == 0o644
