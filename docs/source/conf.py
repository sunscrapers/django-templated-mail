# django-templated-mail documentation build configuration file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import datetime
import pathlib
import sys

import toml

ROOT_DIR = pathlib.Path(__file__).parents[2].resolve()
sys.path.append(ROOT_DIR.as_posix())

pyproject = toml.load((ROOT_DIR / "pyproject.toml").as_posix())
project_info = pyproject["project"]

# -- General configuration ------------------------------------------------

extensions = []
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"

project = project_info["name"]
copyright = f"{datetime.datetime.now().year}, Sunscrapers"
author = project_info["authors"][0]["name"]
release = version = project_info["version"]

language = "en"
exclude_patterns = []
pygments_style = "sphinx"
todo_include_todos = False

# -- Options for HTML output ----------------------------------------------

try:
    import sphinx_rtd_theme  # noqa: F401
except Exception:
    html_theme = "default"
else:
    html_theme = "sphinx_rtd_theme"

html_static_path = []

# -- Options for HTMLHelp output ------------------------------------------

htmlhelp_basename = "django-templated-maildoc"

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {}
latex_documents = [
    (
        master_doc,
        "django-templated-mail.tex",
        "django-templated-mail Documentation",
        author,
        "manual",
    )
]

# -- Options for manual page output ---------------------------------------

man_pages = [
    (
        master_doc,
        "django-templated-mail",
        "django-templated-mail Documentation",
        [author],
        1,
    )
]

# -- Options for Texinfo output -------------------------------------------

texinfo_documents = [
    (
        master_doc,
        "django-templated-mail",
        "django-templated-mail Documentation",
        author,
        "django-templated-mail",
        "Send emails using Django template system.",
        "Miscellaneous",
    )
]
