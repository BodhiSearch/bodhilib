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


def execute_command(run: str, dirs: List[str], command_args: List[str]) -> None:
    for dir_path in dirs:
        cmd: List[str] = ["poetry"]
        if run == "run":
            cmd.append("run")
        cmd.extend(command_args)
        with change_dir(dir_path):
            print(f"Executing: {' '.join(cmd)} in directory {dir_path}...")
            subprocess.run(cmd)


if __name__ == "__main__":
    all_args = sys.argv
    all_args = [arg for arg in all_args if arg != ""]
    print("Running: python", all_args)
    if len(all_args) < 3:
        print("Usage: python make.py <run|exec> [<directory>] <command> [<other args>]")
        sys.exit(1)
    run_or_exec = all_args[1]
    if run_or_exec not in ["run", "exec"]:
        print("Usage: python make.py <run|exec> [<directory>] <command> [<other args>]")
        print(f"argument='{run_or_exec}' is not one of 'run' or 'exec'")
        sys.exit(1)
    may_be_dir = all_args[2]
    if may_be_dir in ["all", "core"] or os.path.exists(
        f"plugins/bodhiext.{may_be_dir}"
    ):
        if len(all_args) < 4:
            print(
                "Usage: python make.py <run|exec> [<directory>] <command> [<other args>]"
            )
            print("<command> not provided")
            sys.exit(1)
        dirs = get_directories(may_be_dir)
        execute_command(run_or_exec, dirs, all_args[3:])
    else:
        dirs = get_directories("all")
        execute_command(run_or_exec, dirs, all_args[2:])
