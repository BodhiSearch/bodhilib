#!/usr/bin/env python3
import argparse
import contextlib
import os
import subprocess
import sys
from typing import Iterator, List


@contextlib.contextmanager
def change_dir(target_dir: str) -> Iterator[None]:
    """Context manager to change the working directory."""
    original_dir = os.getcwd()  # Store the original directory
    os.chdir(target_dir)
    try:
        yield
    finally:
        os.chdir(original_dir)  # Always revert back to the original directory


def get_directories(arg: str) -> List[str]:
    if arg == "all":
        dirs: List[str] = ["core"]
        ext_dirs = [d for d in os.listdir("plugins") if d.startswith("bodhiext.")]
        dirs.extend(os.path.join("plugins", d) for d in ext_dirs)
    elif arg == "core":
        dirs = ["core"]
    else:
        plugin_path = f"plugins/bodhiext.{arg}"
        if not os.path.exists(plugin_path):
            raise ValueError(f"Plugin {plugin_path} does not exist")
        dirs = [plugin_path]
    return dirs


def execute_command(dirs: List[str], command: List[str]) -> int:
    for dir_path in dirs:
        with change_dir(dir_path):
            print(f"Executing: {' '.join(command)} in directory {dir_path}...")
            result = subprocess.run(command)
            if result.returncode != 0:
                return result.returncode
    return 0


def main() -> None:
    dir_opts = ["core", "all"]
    plugin_names = [d.replace("bodhiext.", "") for d in os.listdir("plugins") if d.startswith("bodhiext.")]
    dir_opts.extend(plugin_names)

    parser = argparse.ArgumentParser(description="Python library to automate and orchestrate bodhilib build process.")
    subparsers = parser.add_subparsers(dest="top_command", required=True)
    # 'run' command
    run_parser = subparsers.add_parser("run", help="Run command")
    run_parser.add_argument(
        "target",
        type=str,
        choices=dir_opts,
        nargs="?",
        default="all",
        help="Project to run the `poetry run` command. E.g. core, all, common, openai etc.",
    )
    run_parser.add_argument("command", type=str, help="Poetry command to run. E.g. install etc.")
    run_parser.add_argument(
        "other_args",
        type=str,
        nargs=argparse.REMAINDER,
        default=[],
        help="Pass through arguments for the `poetry run` command.",
    )
    # 'exec' command
    exec_parser = subparsers.add_parser("exec", help="Execute command")
    exec_parser.add_argument(
        "target",
        type=str,
        choices=dir_opts,
        nargs="?",
        default="all",
        help="Project to execute `poetry` command. E.g. core, all, common, openai etc.",
    )
    exec_parser.add_argument("command", type=str, help="Command to execute")
    exec_parser.add_argument(
        "other_args", type=str, nargs=argparse.REMAINDER, default=[], help="Passthrough arguments for `poetry` command."
    )
    args = parser.parse_args()
    # Check if target directory exists in plugins
    if not os.path.exists(f"plugins/bodhiext.{args.target}") and args.target not in ["all", "core"]:
        print(f"Error: Directory for target '{args.target}' does not exist: plugins/bodhiext.{args.target}")
        sys.exit(1)

    dirs = get_directories(args.target)
    if args.top_command == "run":
        sys.exit(execute_command(dirs, ["poetry", "run", args.command] + args.other_args))
    elif args.top_command == "exec":
        sys.exit(execute_command(dirs, ["poetry", args.command] + args.other_args))


if __name__ == "__main__":
    main()
