import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")


def _manifest(name: str) -> dict[str, object]:
    data = json.loads((ROOT / ".claude-plugin" / name).read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _repo() -> str:
    url = _manifest("plugin.json")["repository"]
    assert isinstance(url, str)
    return url.removeprefix("https://github.com/")


# A renamed plugin or a moved repo must not leave the install page pointing
# at nothing: every install line is copied verbatim by someone.
def test_claude_code_lines_name_this_plugin_and_repo() -> None:
    plugin = _manifest("plugin.json")["name"]
    line = f"plugin install {plugin} --marketplace {_repo()}"
    assert f"/{line}" in README
    assert f"claude {line}" in README


def test_claude_ai_marketplace_step_names_this_repo() -> None:
    assert f"Enter `{_repo()}`." in README


def test_pi_installs_this_repo_into_the_project() -> None:
    assert f"pi install git:github.com/{_repo()} -l" in README


def test_the_zip_names_are_the_skill_folders() -> None:
    skills = sorted(p.name for p in (ROOT / "skills").iterdir() if p.is_dir())
    assert sorted(re.findall(r"`([\w-]+)\.zip`", README)) == skills
