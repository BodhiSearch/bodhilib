from importlib import metadata
from pathlib import Path

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "bodhilib.cohere"
copyright = "2023, Amir Nagri"
author = "Amir Nagri"
# TODO: changing to namespace might cause issue here
PACKAGE_VERSION = metadata.version("bodhilib.cohere")
version = release = PACKAGE_VERSION

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autodoc.typehints",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]

# hookin sphinx_apidoc
PROJECT_ROOT = Path(__file__).parent.parent
PACKAGE_ROOT = PROJECT_ROOT / "bodhilib"


def run_apidoc(_):
    from sphinx.ext import apidoc

    try:
        apidoc.main(
            [
                "--force",
                "--implicit-namespaces",
                "--module-first",
                "-o",
                str(PROJECT_ROOT / "docs" / "reference"),
                str(PACKAGE_ROOT),
            ]
        )
    except Exception as e:
        print(f"error with apidoc: {e}")


def setup(app):
    app.connect("builder-inited", run_apidoc)
