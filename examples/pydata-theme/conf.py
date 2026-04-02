"""sphinx-adr example — pydata-sphinx-theme.

pydata-sphinx-theme provides a modern, responsive layout with built-in
light/dark mode toggle. sphinx-adr automatically adapts to the active theme
via CSS custom properties keyed to ``html[data-theme="dark"]``.
"""

project = "sphinx-adr / pydata"
author = "sphinx-adr contributors"

extensions = ["sphinx_adr"]
exclude_patterns = ["_build"]

html_theme = "pydata_sphinx_theme"

html_theme_options = {
    # Show the dark mode toggle in the navbar
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
}
