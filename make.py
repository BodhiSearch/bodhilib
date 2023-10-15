#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from typing import List, cast

import tomli

from update_configs import fetch_versions, plugin_dirs, plugin_names, python_versions

dir_opts = tuple(["core", "all"] + list(plugin_names))


def get_plugin_dirs(arg: str) -> List[str]:
    if arg == "all":
        return list(plugin_dirs)
    else:
        plugin_path = f"plugins/bodhiext.{arg}"
        if not os.path.exists(plugin_path):
            raise ValueError(f"Plugin {plugin_path} does not exist")
        return [plugin_path]


def get_project_dirs(arg: str) -> List[str]:
    if arg == "core":
        return ["core"]
    elif arg == "all":
        return ["core"] + get_plugin_dirs(arg)
    else:
        return get_plugin_dirs(arg)


def execute_command(dirs: List[str], command: List[str]) -> int:
    for dir_path in dirs:
        print(f"Executing: {' '.join(command)} in directory {dir_path}...")
        result = subprocess.run(command, cwd=dir_path)
        if result.returncode != 0:
            return result.returncode
    return 0


def run_poetry_cmd(plugin_dir: str, args: List[str]) -> List[str]:
    errors = []
    result = subprocess.run(["poetry"] + args, stderr=subprocess.PIPE, cwd=plugin_dir)
    if result.returncode != 0:
        error = result.stderr.decode("utf-8")
        errors.append(f"Error running poetry command `poetry {' '.join(args)}` in {plugin_dir=}")
        errors.append(error)
    return errors


def run_tox(bodhilib_versions: List[str], plugin_dir: str) -> List[str]:
    errors = []
    pyproj_file = os.path.join(plugin_dir, "pyproject.toml")
    with open(pyproj_file, "r") as file:
        content = file.read()
    for python_version in python_versions:
        for bodhilib_version in bodhilib_versions:
            if error := run_poetry_cmd(plugin_dir, ["check", "--lock"]):
                errors.extend(error)
                continue
            # update bodhilib version
            if error := run_poetry_cmd(plugin_dir, ["add", f"bodhilib=={bodhilib_version}"]):
                errors.extend(error)
                continue
            bodhilib_version_str = bodhilib_version.replace(".", "_")
            plugin_name = plugin_dir.replace("plugins/bodhiext.", "")
            env = f"{python_version}-plugins_{plugin_name}-bodhilib_{bodhilib_version_str}"
            command = [
                "tox",
                "-e",
                env,
            ]
            print(f"Running command='{' '.join(command)}' for {env}...")
            result = subprocess.run(command, stderr=subprocess.PIPE, cwd=plugin_dir)
            if result.returncode != 0:
                error_msg = result.stderr.decode("utf-8")
                errors.append(f"Error running tox for {python_version=}, {bodhilib_version=}\n")
                errors.append(error_msg)
    with open(pyproj_file, "w") as file:
        file.write(content)
    if error := run_poetry_cmd(plugin_dir, ["lock", "--no-update"]):
        errors.extend(error)
    return errors


def load_pyproject(dir_path: str) -> dict:
    with open(f"{dir_path}/pyproject.toml", "r") as file:
        content = file.readlines()
    bodhilib_section = []
    bodhilib_section_start = False
    for line in content:
        if line.startswith("[tool.bodhilib]"):
            bodhilib_section.append(line)
            bodhilib_section_start = True
            continue
        if bodhilib_section_start:
            if line.startswith("["):
                break
            bodhilib_section.append(line)
    bodhilib_config = tomli.loads("\n".join(bodhilib_section))
    print(bodhilib_config)
    return cast(dict, bodhilib_config)


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
        for error in errors:
            print(error, end="")
            print("")
        return 1
    return 0


def main() -> None:
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
        choices=["all"] + list(plugin_names),
        nargs="?",
        default="all",
        help="Project to run compatibility check against",
    )
    args = parser.parse_args()
    # Check if target directory exists in plugins
    if not os.path.exists(f"plugins/bodhiext.{args.target}") and args.target not in ["all", "core"]:
        print(f"Error: Directory for target '{args.target}' does not exist: plugins/bodhiext.{args.target}")
        sys.exit(1)

    dirs = get_project_dirs(args.target)
    if args.top_command == "run":
        sys.exit(execute_command(dirs, ["poetry", "run", args.command] + args.other_args))
    elif args.top_command == "exec":
        sys.exit(execute_command(dirs, ["poetry", args.command] + args.other_args))
    elif args.top_command == "compat":
        dirs = get_plugin_dirs(args.target)
        sys.exit(exec_compat(dirs))


if __name__ == "__main__":
    main()
