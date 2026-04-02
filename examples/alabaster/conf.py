"""sphinx-adr example — alabaster theme (Sphinx default)."""

project = "sphinx-adr / alabaster"
author = "sphinx-adr contributors"

extensions = ["sphinx_adr"]
exclude_patterns = ["_build"]

html_theme = "alabaster"

adr_path = "adr"

html_sidebars = {
    "adr/*": ["adr_nav.html"],
}
