import argparse
import subprocess
import sys
from pathlib import Path

from sevenflows.build import build, check
from sevenflows.lint import lint
from sevenflows.package import package
from sevenflows.release import release


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sevenflows")
    commands = parser.add_subparsers(dest="command", required=True)
    build_cmd = commands.add_parser("build", help="copy method/ into the skills")
    build_cmd.add_argument(
        "--check", action="store_true", help="report drift, change nothing"
    )
    commands.add_parser("lint", help="check every skill's frontmatter")
    commands.add_parser("package", help="write one ZIP per skill into dist/")
    release_cmd = commands.add_parser(
        "release", help="tag and publish a version, only on a full green eval run"
    )
    release_cmd.add_argument("version", help="X.Y.Z, as in plugin.json")
    release_cmd.add_argument(
        "--results",
        type=Path,
        required=True,
        help="aggregate-result.json of a full `claude plugin eval` run",
    )
    release_cmd.add_argument(
        "--rerun",
        type=Path,
        action="append",
        default=[],
        help="aggregate-result.json of a fresh re-run of the cases that fell short",
    )
    release_cmd.add_argument(
        "--dry-run", action="store_true", help="check everything, tag nothing"
    )
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

    if args.command == "package":
        try:
            archives = package(root)
        except ValueError as error:
            print(error)
            return 1
        for archive in archives:
            print(archive.relative_to(root))
        return 0

    if args.command == "release":
        try:
            refused = release(
                root,
                args.version,
                args.results,
                dry_run=args.dry_run,
                reruns=args.rerun,
            )
        except subprocess.CalledProcessError as error:
            print(f"{' '.join(error.cmd)} failed: {error.stderr.strip()}")
            return 1
        for reason in refused:
            print(f"refused: {reason}")
        if refused:
            return 1
        verb = "would release" if args.dry_run else "released"
        print(f"{verb} v{args.version}")
        return 0

    findings = lint(root)
    for finding in findings:
        print(finding)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
