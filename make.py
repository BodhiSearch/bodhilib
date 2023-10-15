#!/usr/bin/env python3
import argparse
import contextlib
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterator, List, cast

import requests
from poetry.factory import Factory
from poetry.poetry import Poetry

python_versions = ["py38", "py39", "py310", "py311"]


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


def fetch_versions(package_name: str, min_version: str) -> List[str]:
    response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
    releases = response.json()["releases"].keys()
    min_version_ints = tuple(map(int, min_version.split(".")))
    valid_versions = [v for v in releases if tuple(map(int, v.split("."))) >= min_version_ints]
    return valid_versions


def run_tox(bodhilib_versions: List[str], plugin_dir: str) -> List[str]:
    errors = []
    for python_version in python_versions:
        for bodhilib_version in bodhilib_versions:
            bodhilib_version_str = bodhilib_version.replace(".", "_")
            env = f"{python_version}-bodhilib{bodhilib_version_str}"
            env_vars = os.environ.copy()
            env_vars["BODHILIB_VERSION"] = bodhilib_version
            env_vars["PLUGIN_DIR"] = plugin_dir
            command = [
                "tox",
                "-e",
                env,
            ]
            print(f"Running command='{' '.join(command)}' for {env}...")
            result = subprocess.run(
                command,
                stderr=subprocess.PIPE,
                env=env_vars,
            )
            if result.returncode != 0:
                error = result.stderr.decode("utf-8")
                errors.append(f"Error running tox for {python_version=}, {bodhilib_version=}\n {error=}")
    return errors


def load_pyproject(dir_path: str) -> dict:
    poetry: Poetry = Factory().create_poetry(Path(dir_path))
    pyproject_data = poetry.pyproject.data
    return cast(dict, pyproject_data)


def exec_compat(dirs: List[str]) -> int:
    errors = []
    for dir_path in dirs:
        pyproj = load_pyproject(dir_path)
        min_version = pyproj["tool"]["bodhilib"]["version"]
        bodhilib_versions = fetch_versions("bodhilib", min_version)
        result = run_tox(bodhilib_versions, dir_path)
        errors.extend(result)
    if errors:
        print("test failed")
        print("\n".join(errors))
        return 1
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

    # 'compat' command
    compat_parser = subparsers.add_parser("compat", help="Execute compatibility checks for given plugin")
    compat_parser.add_argument(
        "target",
        type=str,
        choices=["all"] + plugin_names,
        nargs="?",
        default="all",
        help="Project to run compatibility check against",
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
    elif args.top_command == "compat":
        sys.exit(exec_compat(dirs))


if __name__ == "__main__":
    main()
