"""Sphinx configuration for sphinx-adr demo documentation."""

project = "sphinx-adr demo"
copyright = "2024, sphinx-adr contributors"
author = "sphinx-adr contributors"

extensions = [
    "sphinx_adr",
]

exclude_patterns = ["_build"]
html_theme = "alabaster"

adr_path = "adr"

html_sidebars = {
    "adr/*": ["adr_nav.html"],
}
