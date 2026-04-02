# CLAUDE.md

Project context for Claude Code sessions.

## What is this project?

**sphinx-adr** is a Sphinx extension for Architecture Decision Records (ADRs). It provides two directives (`.. adr::` and `.. adrlist::`) that let users write ADRs as regular Sphinx documents and generate a timeline-based decision log. The visual design is inspired by log4brains (vertical timeline with status-colored dots and cards).

## Tech stack

- **Python 3.9+** with **Sphinx >= 7.0**
- **docutils** — custom nodes and directives
- **Hatchling** — build backend (pyproject.toml)
- **Pipenv** — local development environment
- **pytest** — test framework

## Repository layout

```
sphinx_adr/             # Extension source code
  __init__.py           # setup() function, config values, wiring
  directives.py         # AdrDirective and AdrListDirective
  nodes.py              # Custom docutils nodes (adr_meta, adr_list) and HTML/text visitors
  collector.py          # Env event handlers: metadata collection, timeline rendering
  static/sphinx_adr.css # Timeline and status badge CSS

docs/                   # Demo documentation site (dogfoods the extension)
  conf.py               # Sphinx config — extensions = ["sphinx_adr"]
  adr/                  # Sample ADRs (0001, 0002, 0003)

tests/                  # pytest tests
  conftest.py           # make_project fixture for creating temp Sphinx projects
  test_extension.py     # 7 tests: directives, rendering, filtering, sorting, full build
```

## Common commands

```bash
# Set up development environment
pipenv install -e ".[dev]"
pipenv shell

# Build demo docs
pipenv run docs
# or: pipenv run sphinx-build -b html docs docs/_build/html

# Run tests
pipenv run test
# or: pipenv run python -m pytest tests/ -v

# Install in editable mode (without pipenv)
pip install -e ".[dev]"
```

## How the extension works

1. **`.. adr::` directive** parses metadata options (status, date, authors, tags, superseded-by), stores them in `env.adr_all_adrs[docname]`, and emits an `adr_meta` node that renders a metadata banner.
2. **`.. adrlist::` directive** emits a placeholder `adr_list` node.
3. During the `doctree-resolved` event, `process_adr_lists()` in `collector.py` replaces `adr_list` nodes with rendered timeline HTML built from all collected ADR metadata.
4. `env-purge-doc` and `env-merge-info` handlers ensure incremental and parallel builds work correctly.

## Key design decisions

- ADR metadata is stored on `env.adr_all_adrs` (a dict keyed by docname), following the same pattern as ablog's `env.blog_posts`.
- Timeline HTML is rendered directly in Python (in `collector.py`) rather than using Jinja2 templates, keeping the extension dependency-free beyond Sphinx itself.
- CSS uses `:has()` selectors for the meta banner border color — works in all modern browsers.
- Valid statuses: Proposed, Accepted, Deprecated, Superseded. Validated at directive parse time.

## Testing notes

- Tests create temporary Sphinx projects via the `make_project` fixture and run full `sphinx-build` in-process.
- Each test gets its own `tmp_path` so tests are fully isolated.
- The `test_full_demo_build` test builds the actual `docs/` directory as an integration test.
