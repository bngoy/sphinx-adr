"""Minimal Sphinx configuration for the sphinx-adr example project."""

project = "My Project"
author = "My Team"

extensions = [
    "sphinx_adr",
]

exclude_patterns = ["_build", "README.md"]
html_theme = "alabaster"
