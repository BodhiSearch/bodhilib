import os
import sys
from pathlib import Path

docs_dir = Path(os.path.dirname(__file__))
libs = docs_dir / ".." / ".." / "libs"
# find all directories in libs
for d in libs.iterdir():
    src = d / "src"
    sys.path.insert(0, str(src.resolve()))

# -- Project information -----------------------------------------------------
project = "bodhilib"
copyright = "2023, Amir Nagri"
author = "Amir Nagri"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.autodoc_pydantic",
    "sphinx_copybutton",
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
    "private-members": False,
    "undoc-members": False,
}
autosummary_generate = True
autodoc_pydantic_model_show_json = False
# rendering fields like `role (bodhilib.models._prompt.Role)`
# switching fields off once figure out how to display objects from private modules with properly
autodoc_pydantic_model_show_field_summary = False
html_theme_options = {
    "repository_url": "https://github.com/BodhiSearch/bodhilib",
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
