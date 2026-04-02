# sphinx-adr examples

Three self-contained example projects demonstrating `sphinx-adr` with different
Sphinx themes. Each can be built independently.

| Directory          | Theme                    | Dark mode |
|--------------------|--------------------------|-----------|
| `alabaster/`       | alabaster (Sphinx default)| No        |
| `pydata-theme/`    | pydata-sphinx-theme      | Yes       |
| `book-theme/`      | sphinx-book-theme        | Yes       |

## Quick start

From the repository root:

```bash
# Install the extension + theme dependencies
pip install -e ".[examples]"

# Build any example
sphinx-build -b html examples/alabaster     examples/alabaster/_build/html
sphinx-build -b html examples/pydata-theme  examples/pydata-theme/_build/html
sphinx-build -b html examples/book-theme    examples/book-theme/_build/html
```

Or with Pipenv:

```bash
pipenv install -e ".[examples]"
pipenv run sphinx-build -b html examples/pydata-theme examples/pydata-theme/_build/html
```

Then open `_build/html/index.html` inside any example directory.
