import os
import sys
from datetime import datetime


# -- Project information -----------------------------------------------------

project = "VeloDetect"
author = "VeloDetect Contributors"
current_year = datetime.now().year
copyright = f"{current_year}, {author}"

# Prefer RTD-provided version when available
release = os.environ.get("READTHEDOCS_VERSION") or os.environ.get(
    "READTHEDOCS_VERSION_NAME", "latest"
)
version = release


# -- General configuration ---------------------------------------------------

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.viewcode",
    "sphinx.ext.doctest",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Recognize both .rst and .md sources
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# MyST configuration (Markdown)
myst_enable_extensions = [
    "deflist",
    "linkify",
    "smartquotes",
    "substitution",
    "tasklist",
]
myst_heading_anchors = 3

# Use the new name for Sphinx 5+; default is "index"
root_doc = "index"

# If your package lives in the repo root, add it to sys.path for autodoc
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)


# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_theme_options = {
    "collapse_navigation": False,
    "navigation_depth": 4,
    "sticky_navigation": True,
}

# Make section labels unique across files
autosectionlabel_prefix_document = True

# Napoleon (Google/Numpy-style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False


