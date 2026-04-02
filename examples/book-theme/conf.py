"""sphinx-adr example — sphinx-book-theme.

sphinx-book-theme is built on top of pydata-sphinx-theme and shares the same
``html[data-theme="dark"]`` mechanism. sphinx-adr detects this automatically.
"""

project = "sphinx-adr / book"
author = "sphinx-adr contributors"

extensions = ["sphinx_adr"]
exclude_patterns = ["_build"]

html_theme = "sphinx_book_theme"

html_theme_options = {
    "repository_url": "https://github.com/bngoy/sphinx-adr",
    "use_repository_button": True,
}

adr_path = "adr"

html_sidebars = {
    "adr/*": ["adr_nav.html"],
}
