#!/usr/bin/env python3
import argparse
import itertools
import json
import os
import subprocess
import sys
from typing import List, Optional, Union, cast, no_type_check

import tomli

from update_configs import (
    fetch_gh_releases,
    fetch_versions,
    plugin_dirs,
    plugin_folders,
    python_versions,
    update_github_workflows,
    update_mypy_ini,
    update_pytest_ini,
    update_tox_inis,
)

dir_opts = tuple(["all", "core"] + list(plugin_folders))


def get_plugin_dirs(arg: str) -> List[str]:
    if arg == "all":
        return list(plugin_dirs)
    else:
        plugin_path = f"plugins/{arg}"
        if not os.path.exists(plugin_path):
            raise ValueError(f"Plugin {plugin_path} does not exist")
        return [plugin_path]


def get_plugin_dirs_from_name(arg: str) -> List[str]:
    if arg == "all":
        return list(plugin_dirs)
    else:
        plugin_path = f"plugins/{arg}"
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


def run_tox_for(py_versions: List[str], bodhilib_versions: List[str], plugin_dir: str) -> List[str]:
    errors = []
    for py_version in py_versions:
        for bodhilib_version in bodhilib_versions:
            if error := run_poetry_cmd(plugin_dir, ["check", "--lock"]):
                errors.extend(error)
                continue
            # update bodhilib version
            if bodhilib_version.startswith("pre/"):
                whl_url = bodhilib_version.replace("pre/", "")
                if error := run_poetry_cmd(plugin_dir, ["add", whl_url]):
                    errors.extend(error)
                    continue
                bodhilib_version_str = "pre"
            elif bodhilib_version == "dev":
                if error := run_poetry_cmd(plugin_dir, ["add", "bodhilib", "-e", "../../core"]):
                    errors.extend(error)
                    continue
                bodhilib_version_str = "dev"
            else:
                if error := run_poetry_cmd(plugin_dir, ["add", f"bodhilib=={bodhilib_version}"]):
                    errors.extend(error)
                    continue
                bodhilib_version_str = bodhilib_version.replace(".", "_")
            plugin_slug = plugin_dir.replace("plugins/", "").replace(".", "_")
            env = f"{py_version}-plugins_{plugin_slug}-bodhilib_{bodhilib_version_str}"
            errors.extend(run_tox(env, plugin_dir))
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
    return cast(dict, bodhilib_config)


def exec_tox(
    targets: Union[str, List[str]],
    only_dev: bool = False,
    only_min: bool = False,
    include_prerelease: bool = False,
    arg_py_versions: Optional[str] = None,
) -> int:
    if isinstance(targets, str):
        targets = ["all"]
    folders = list(set(itertools.chain(*[parse_args_target(target) for target in targets])))
    errors = []
    if arg_py_versions is None:
        arg_py_versions = ",".join(python_versions)
    py_versions = arg_py_versions.split(",")
    missing_versions = [py for py in py_versions if py not in python_versions]
    if missing_versions:
        print(f"Error: Python versions {missing_versions} are not supported.")
        return 1
    for folder in folders:
        if folder == "core":
            result = run_tox_for_core(py_versions, folder)
        else:
            if only_dev:
                bodhilib_versions = ["dev"]
            else:
                bodhilib_versions = find_supported_versions(folder, only_min, include_prerelease)
            result = run_tox_for_plugin(py_versions, bodhilib_versions, folder)
        errors.extend(result)
    if errors:
        print("test failed")
        for error in errors:
            print(error, end="")
            print("")
        return 1
    return 0


def run_tox_for_core(py_versions: List[str], plugin_dir: str) -> List[str]:
    errors = []
    for py_version in py_versions:
        env = f"{py_version}-core"
        errors.extend(run_tox(env, plugin_dir))
    return errors


def run_tox_for_plugin(py_versions: List[str], bodhilib_versions: List[str], plugin_dir: str) -> List[str]:
    errors = []
    pyproj_file = os.path.join(plugin_dir, "pyproject.toml")
    with open(pyproj_file, "r") as file:
        content = file.read()
    try:
        tox_errors = run_tox_for(py_versions, bodhilib_versions, plugin_dir)
        errors.extend(tox_errors)
    finally:
        with open(pyproj_file, "w") as file:
            file.write(content)
    if error := run_poetry_cmd(plugin_dir, ["lock", "--no-update"]):
        errors.extend(error)
    return errors


def run_tox(env: str, plugin_dir: str) -> List[str]:
    command = [
        "tox",
        "-e",
        env,
    ]
    print(f"Running command='{' '.join(command)}' for {env}, inside {plugin_dir}")
    result = subprocess.run(command, stderr=subprocess.PIPE, cwd=plugin_dir)
    errors = []
    if result.returncode != 0:
        error_msg = result.stderr.decode("utf-8")
        errors.append(f"Error running tox, {env=}, {plugin_dir=}\n")
        errors.append(error_msg)
    return errors


@no_type_check
def find_supported_versions(plugin_dir: str, only_min: bool = False, include_prerelease: bool = False) -> List[str]:
    result = []
    pyproj = load_pyproject(plugin_dir)
    if "tool" not in pyproj or "bodhilib" not in pyproj["tool"]:
        raise ValueError(f"[tool.bodhilib] section missing in {plugin_dir}/pyproject.toml")
    min_version = pyproj["tool"]["bodhilib"]["version"]
    pypi_releases = fetch_versions("bodhilib", min_version)
    if only_min and not include_prerelease:
        # return only the min supported release
        return [pypi_releases[-1]]
    if only_min:
        # add only the min supported release
        result.append(pypi_releases[-1])
    else:
        # add all supported releases
        result.extend(pypi_releases)
    if include_prerelease:
        # add the latest prerelease
        gh_releases = fetch_gh_releases("BodhiSearch", "bodhilib", None)
        prereleases = [
            release for release in gh_releases if release["name"].startswith("bodhilib/") and release["prerelease"]
        ]
        prereleases = sorted(prereleases, key=lambda k: k["created_at"], reverse=True)
        prerelease = prereleases[0]
        asset_whl = [asset for asset in prerelease["assets"] if asset["name"].endswith(".whl")]
        whl_url = asset_whl[0]["browser_download_url"]
        result.insert(0, f"pre/{whl_url}")
    return result


def parse_args_target(target: str) -> List[str]:
    # Check if target directory exists in plugins
    if target not in ["all", "core"] and not os.path.exists(f"plugins/{target}"):
        print(f"Error: Directory for target '{target}' does not exist: plugins/{target}")
        sys.exit(1)
    dirs = get_project_dirs(target)
    return dirs


def exec_supports(plugin_folders: List[str], only_min: bool, plaintext: bool) -> int:
    missing_folders = [folder for folder in plugin_folders if not os.path.exists(f"plugins/{folder}")]
    if missing_folders:
        print(f"Error: Plugin directory does not exist: '{missing_folders}'")
        return 1
    result = {}
    for plugin_folder in plugin_folders:
        plugin_dir = f"plugins/{plugin_folder}"
        versions = find_supported_versions(plugin_dir, only_min)
        if only_min:
            result[plugin_folder] = versions[0]
        else:
            result[plugin_folder] = versions
    if plaintext and len(result.items()) == 1:
        version = next(iter(result.items()))[1]
        print(f"{version}")
        return 0
    print(json.dumps(result, separators=(",", ":")))
    return 0


def exec_update_configs() -> int:
    update_mypy_ini()
    update_pytest_ini()
    update_github_workflows()
    update_tox_inis()
    return 0


def exec_check_pyproj(targets: List[str]) -> int:
    folders = list(set(itertools.chain(*[parse_args_target(target) for target in targets])))
    # sort folders, keep core on top if exists
    folders = sorted(folders, key=lambda x: (x != "core", x))
    errors = []
    for folder in folders:
        pyproj = load_pyproject(folder)
        if folder != "core" and ("tool" not in pyproj or "bodhilib" not in pyproj["tool"]):
            errors.append(f"[tool.bodhilib] section missing in {folder}/pyproject.toml")
        result = subprocess.run(["poetry", "version", "--short"], cwd=folder, stdout=subprocess.PIPE)
        if result.returncode != 0:
            errors.append(f"Error running poetry version in {folder}")
            continue
        version = result.stdout.decode("utf-8").strip()
        if not version.endswith("-dev"):
            errors.append(f"{folder} has a non-dev version `{version}`")
    if errors:
        print("\n".join(errors))
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

    # 'supports' command
    supports_parser = subparsers.add_parser("supports", help="List supported versions")
    supports_parser.add_argument(
        "targets",
        type=str,
        nargs="+",
        choices=list(plugin_folders),
        help="List supported versions for given plugin.",
    )
    supports_parser.add_argument("--only-min", action="store_true", help="List only minimum supported version")
    supports_parser.add_argument("--plaintext", action="store_true", help="Print output in plaintext")

    # 'compat' command
    tox_parser = subparsers.add_parser("tox", help="Execute compatibility checks for given plugin using tox")
    tox_parser.add_argument(
        "targets",
        type=str,
        choices=dir_opts,
        nargs="*",
        default="all",
        help="Run tox for given projects",
    )
    tox_parser.add_argument("--only-dev", action="store_true", help="Run only for dev versions")
    tox_parser.add_argument("--only-min", action="store_true", help="Run only for minimum supported version")
    tox_parser.add_argument(
        "--include-prerelease", action="store_true", help="Include the latest pre-release for compatibility test"
    )
    tox_parser.add_argument(
        "--python-versions", type=str, default=",".join(python_versions), help="Python version to run tox against"
    )

    # 'update-configs' command
    _ = subparsers.add_parser("update-configs", help="Update configs")

    # 'check-pyproj' command
    check_pyproj = subparsers.add_parser(
        "check-pyproj", help="Check pyproject.toml for tool.bodhilib section, and version as `-dev`"
    )
    check_pyproj.add_argument(
        "targets",
        type=str,
        nargs="+",
        choices=dir_opts,
        help="List supported versions for given plugin.",
        default="all",
    )

    args = parser.parse_args()
    if args.top_command == "run":
        dirs = parse_args_target(args.target)
        sys.exit(execute_command(dirs, ["poetry", "run", args.command] + args.other_args))
    elif args.top_command == "exec":
        dirs = parse_args_target(args.target)
        sys.exit(execute_command(dirs, ["poetry", args.command] + args.other_args))
    elif args.top_command == "supports":
        sys.exit(exec_supports(args.targets, args.only_min, args.plaintext))
    elif args.top_command == "tox":
        sys.exit(exec_tox(args.targets, args.only_dev, args.only_min, args.include_prerelease, args.python_versions))
    elif args.top_command == "update-configs":
        sys.exit(exec_update_configs())
    elif args.top_command == "check-pyproj":
        sys.exit(exec_check_pyproj(args.targets))
    else:
        print(f"Unknown command {args.top_command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
