#!/usr/bin/env python3

import glob
import os
import subprocess
from pathlib import Path


def main() -> None:
    # Get the current script directory
    docs_dir = Path(__file__).parent.absolute()
    os.chdir(docs_dir)
    output_path = "reference"
    src_path = docs_dir / ".." / "src" / "bodhilib"
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
    libs_root = glob.glob(os.path.join(docs_dir / ".." / "libs", "*"))
    exts_src = [Path(lib_root) / "src" / "bodhiext" for lib_root in libs_root]
    exts_src.insert(0, docs_dir / ".." / "src" / "bodhiext")
    for ext_src in exts_src:
        if os.path.isdir(ext_src):
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
                    ext_src.absolute(),
                ]
            )
    # Remove unnecessary files
    os.remove("reference/modules.rst")
    os.remove("reference/bodhiext.rst")

    # generate doctrees
    subprocess.run(["make", "html"])

    # Build the documentation
    subprocess.run(
        [
            "poetry",
            "run",
            "sphinx-build",
            "-a",
            "-T",
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
