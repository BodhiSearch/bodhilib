#!/usr/bin/env python3

import glob
import os
import subprocess


def main() -> None:
    # Get the current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Build the api documentation
    lib_dir = os.path.join("..", "libs")
    for plugin in glob.glob(os.path.join(lib_dir, "*")):
        if os.path.isdir(plugin):
            src_path = os.path.join(plugin, "src", "bodhilib")
            output_path = "api/reference"

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
                    "api/_templates",
                    "-o",
                    output_path,
                    src_path,
                ]
            )
    # Remove unnecessary files
    os.remove("api/reference/modules.rst")
    os.remove("api/reference/bodhilib.rst")

    # Build the documentation
    subprocess.run(
        [
            "poetry",
            "run",
            "sphinx-build",
            "-a",
            "-E",
            "-j",
            "auto",
            "-n",
            "--color",
            "-W",
            "--keep-going",
            "-b",
            "html",
            "api",
            "api/_build/",
        ]
    )

    # Check links in the documentation
    subprocess.run(["poetry", "run", "sphinx-build", "-b", "linkcheck", "api", "api/_build/linkcheck/"])


if __name__ == "__main__":
    main()
