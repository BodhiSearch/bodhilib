#!/usr/bin/env python3

import glob
import os
import subprocess
from pathlib import Path


def main() -> None:
    # Get the current script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    output_path = "reference"
    src_path = script_dir / ".." / "src" / "bodhilib"
    subprocess.run(
        [
            "poetry",
            "run",
            "sphinx-apidoc",
            "--implicit-namespaces",
            "--separate",
            "--module-first",
            "--templatedir",
            "_templates",
            "-o",
            output_path,
            src_path,
        ]
    )

    # Build the api documentation
    lib_dir = script_dir / ".." / "libs"
    for plugin in glob.glob(os.path.join(lib_dir, "*")):
        if os.path.isdir(plugin):
            src_path = Path(plugin) / "src" / "bodhilib"
            # Run sphinx-apidoc
            subprocess.run(
                [
                    "poetry",
                    "run",
                    "sphinx-apidoc",
                    "--implicit-namespaces",
                    "--separate",
                    "--module-first",
                    "--templatedir",
                    "_templates",
                    "-o",
                    output_path,
                    src_path,
                ]
            )
    # Remove unnecessary files
    os.remove("reference/modules.rst")
    os.remove("reference/bodhilib.rst")

    # generate doctrees
    subprocess.run(["make", "html"])

    # Build the documentation
    subprocess.run(
        [
            "poetry",
            "run",
            "sphinx-build",
            "-a",
            "-E",
            "-j",
            "1",
            "-n",
            "--color",
            "-W",
            "--keep-going",
            "-b",
            "html",
            ".",
            "_build/html",
        ]
    )

    # Check links in the documentation
    subprocess.run(["poetry", "run", "sphinx-build", "-b", "linkcheck", ".", "_build/linkcheck"])


if __name__ == "__main__":
    main()
