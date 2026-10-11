import argparse
import sys
from pathlib import Path

from sevenflows.build import build, check
from sevenflows.lint import lint


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sevenflows")
    commands = parser.add_subparsers(dest="command", required=True)
    build_cmd = commands.add_parser("build", help="copy method/ into the skills")
    build_cmd.add_argument(
        "--check", action="store_true", help="report drift, change nothing"
    )
    commands.add_parser("lint", help="check every skill's frontmatter")
    args = parser.parse_args(argv)
    root = Path.cwd()

    if args.command == "build":
        if not args.check:
            build(root)
            return 0
        drifted = check(root)
        for path in drifted:
            print(f"out of date: {path.relative_to(root)} — run `sevenflows build`")
        return 1 if drifted else 0

    findings = lint(root)
    for finding in findings:
        print(finding)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
