import sys
from pathlib import Path

import tomli

DOCS_DIR = Path(__file__).parent.absolute()
ROOT_DIR = DOCS_DIR / ".."
PLUGINS_DIR = ROOT_DIR / "plugins"
for plugin_dir in PLUGINS_DIR.glob("*"):
  sys.path.insert(0, str(plugin_dir / "src"))
CORE_DIR = ROOT_DIR / "core"
sys.path.insert(0, str(CORE_DIR / "src"))

with open(CORE_DIR / "pyproject.toml") as f:
  pyproj_file = tomli.load(f)

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
  ("py:class", "bodhilib._components.PS"),
  ("py:class", "bodhilib._components.DL"),
  ("py:class", "bodhilib._components.E"),
  ("py:class", "bodhilib._components.L"),
  ("py:class", "bodhilib._components.V"),
  ("py:class", "bodhilib._components.S"),
  ("py:class", "bodhilib._plugin.C"),
  ("py:class", "bodhilib._models.T"),
  ("py:class", "PathLike"),
  ("py:class", "TextLike"),
  ("py:class", "Embedding"),
  ("py:class", "TextLikeOrTextLikeList"),
  ("py:class", "SerializedInput"),
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
  "mock_imports": ["pydantic"],
  "members": True,
}
autodoc_type_aliases = {
  "PathLike": "PathLike",
  "TextLike": "TextLike",
  "Embedding": "Embedding",
  "TextLikeOrTextLikeList": "TextLikeOrTextLikeList",
  "SerializedInput": "SerializedInput",
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
