"""Pack each skill into dist/<skill>.zip for a claude.ai upload or a release.

claude.ai wants the skill folder itself at the top of the archive, never its
files loose at the root.
"""

import stat
import zipfile
from pathlib import Path

from sevenflows.build import MANIFEST, Manifest, check

# Left behind by Python and macOS, never part of a skill.
SKIP = {"__pycache__", ".DS_Store"}
# A fixed timestamp: the same skill always packs to the same bytes, so a
# release ZIP can be checked against a fresh build.
EPOCH = (1980, 1, 1, 0, 0, 0)


def _files(skill: Path) -> list[Path]:
    return sorted(
        path
        for path in skill.rglob("*")
        if path.is_file()
        and not SKIP & set(path.relative_to(skill).parts)
        and path.suffix != ".pyc"
    )


def _pack(skill: Path, archive: Path) -> None:
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for path in _files(skill):
            info = zipfile.ZipInfo(
                f"{skill.name}/{path.relative_to(skill).as_posix()}", EPOCH
            )
            info.external_attr = (
                stat.S_IFREG | stat.S_IMODE(path.stat().st_mode)
            ) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, path.read_bytes())


def package(root: Path, manifest: Manifest = MANIFEST) -> list[Path]:
    """Write one ZIP per skill into dist/ and return their paths."""
    if drifted := check(root, manifest):
        stale = ", ".join(str(p.relative_to(root)) for p in drifted)
        raise ValueError(f"out of date: {stale} — run `sevenflows build`")
    dist = root / "dist"
    dist.mkdir(exist_ok=True)
    # A skill dropped from the manifest must not ride along in a release.
    for old in dist.glob("*.zip"):
        old.unlink()
    archives = []
    for skill in manifest:
        archive = dist / f"{skill}.zip"
        _pack(root / "skills" / skill, archive)
        archives.append(archive)
    return archives
