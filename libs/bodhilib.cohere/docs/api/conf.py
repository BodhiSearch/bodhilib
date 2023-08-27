#!/usr/bin/env python
import os
import sys
from pathlib import Path
from importlib import metadata

docs_dir = Path(os.path.dirname(__file__))
src_dir = docs_dir / ".." / ".." / "src"
sys.path.insert(0, str(src_dir.resolve()))

# -- Project information -----------------------------------------------------
project = "bodhilib.cohere"
copyright = "2023, Amir Nagri"
author = "Amir Nagri"
# TODO: changing to namespace might cause issue here
PACKAGE_VERSION = metadata.version("bodhilib.cohere")
version = release = PACKAGE_VERSION

# -- General configuration ---------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.autodoc_pydantic",
    "sphinx_copybutton",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
language = "en"

source_suffix = [".rst", ".md", ".ipynb", ".myst"]
master_doc = "index"
pygments_style = "sphinx"
todo_include_todos = False

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_book_theme"
html_static_path = ["_static"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/", None),
}
autodoc_default_options = {
    "typehints": "description",
    "mock_imports": ["pydantic"],
    "members": True,
    "private-members": True,
    "undoc-members": False,
}
autosummary_generate = True
autodoc_pydantic_model_show_json = False
html_theme_options = {
    "repository_url": "https://github.com/BodhiSearch/bodhilib.cohere",
    "use_repository_button": True,
}
myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_image",
]
myst_url_schemes = ("http", "https", "mailto")
