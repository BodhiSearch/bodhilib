from pathlib import Path

import toml

API_DIR = Path(__file__).parent.absolute()
PROJ_DIR = API_DIR / ".." / ".."
with open(PROJ_DIR / "pyproject.toml") as f:
    pyproj_file = toml.load(f)

# -- Project information -----------------------------------------------------
project = "bodhilib"
copyright = "2023, Amir Nagri"
author = "Amir Nagri"
release = pyproj_file["tool"]["poetry"]["version"]

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_rtd_theme",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
language = "en"

source_suffix = [".rst", ".md", ".ipynb", ".myst"]
master_doc = "index"
pygments_style = "sphinx"
todo_include_todos = False
nitpick_ignore = [
    ("py:class", "bodhilib.data_loader._data_loader.T"),
    ("py:class", "bodhilib.embedder._embedder.T"),
    ("py:class", "bodhilib.llm._llm.T"),
    ("py:class", "bodhilib.plugin._plugin.T"),
    ("py:class", "bodhilib.models._prompt.T"),
    ("py:class", "PathLike"),
    ("py:class", "PromptInput"),
    ("py:class", "TextLike"),
    ("py:class", "pydantic.main.BaseModel"),
    ("py:class", "T"),
    ("py:data", "T"),
]

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/", None),
}
autodoc_default_options = {
    "typehints": "description",
    "mock_imports": ["torch", "pydantic"],
    "members": True,
}
autodoc_type_aliases = {
    "PromptInput": "PromptInput",
    "TextLike": "TextLike",
    "PathLike": "PathLike",
}
autoclass_content = "both"
html_theme_options = {
    "collapse_navigation": False,
}
myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_image",
]
myst_url_schemes = ("http", "https", "mailto")
