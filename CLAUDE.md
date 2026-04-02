# CLAUDE.md

Project context for Claude Code sessions.

## What is this project?

**sphinx-adr** is a Sphinx extension for Architecture Decision Records (ADRs). It provides two directives (`.. adr::` and `.. adrlist::`) that let users write ADRs as regular Sphinx documents and generate a timeline-based decision log. The visual design is inspired by log4brains (vertical timeline with status-colored dots and cards). The sidebar navigation follows ablog's `html_sidebars` pattern.

## Tech stack

- **Python 3.13+** with **Sphinx >= 8.0**
- **docutils** -- custom nodes and directives
- **Hatchling** -- build backend (pyproject.toml)
- **uv** -- package manager and task runner
- **ruff** -- linting and formatting
- **pytest** -- test framework
- **GitHub Actions** -- CI/CD (lint, test, auto-tag, PyPI release)

## Repository layout

```
sphinx_adr/               # Extension source code
  __init__.py              # setup() function, config values, version
  directives.py            # AdrDirective and AdrListDirective
  nodes.py                 # Custom docutils nodes (adr_meta, adr_list) and HTML/text visitors
  collector.py             # Env event handlers: metadata collection, timeline rendering
  templates/adr_nav.html   # Sidebar Jinja2 template
  static/sphinx_adr.css    # Timeline, status/ID badges, dark mode CSS

docs/                      # Demo documentation site (dogfoods the extension)
  conf.py                  # Sphinx config -- extensions = ["sphinx_adr"]
  adr/                     # Sample ADRs (0001, 0002, 0003)

examples/                  # Theme-specific examples
  alabaster/               # Default theme
  pydata-theme/            # pydata-sphinx-theme (dark mode)
  book-theme/              # sphinx-book-theme (dark mode)

tests/                     # pytest tests
  conftest.py              # make_project fixture for creating temp Sphinx projects
  test_extension.py        # 7 tests: directives, rendering, filtering, sorting, full build

.github/workflows/         # CI/CD
  ci.yml                   # Lint + test on push/PR
  auto-tag.yml             # Tag from VERSION on PR merge to master
  release.yml              # Publish to PyPI on version tags

VERSION                    # Single source of truth for release version
```

## Dev commands

```bash
# Setup
uv sync --extra dev

# Run tests
uv run pytest tests/ -v

# Lint
uv run ruff check .
uv run ruff check --fix .    # auto-fix

# Format
uv run ruff format .

# Build demo docs
uv run sphinx-build -b html docs docs/_build/html

# Build theme examples (needs examples extra)
uv sync --extra examples
uv run sphinx-build -b html examples/pydata-theme examples/pydata-theme/_build/html
```

## How the extension works

1. **`.. adr::` directive** parses metadata options (id, status, date, authors, tags, superseded-by), stores them in `env.adr_all_adrs[docname]`, and emits an `adr_meta` node that renders a metadata banner.
2. **`.. adrlist::` directive** emits a placeholder `adr_list` node.
3. During the `doctree-resolved` event, `process_adr_lists()` in `collector.py` replaces `adr_list` nodes with rendered timeline HTML built from all collected ADR metadata.
4. `html-page-context` event injects `adr_nav_entries` into the template context for the sidebar.
5. `env-purge-doc` and `env-merge-info` handlers ensure incremental and parallel builds work correctly.

## Key conventions

- **`:id:` and `:status:` are required** fields on the `.. adr::` directive. Omitting either produces a build warning and the ADR is not registered.
- **Valid statuses**: Proposed, Accepted, Deprecated, Superseded. Validated at directive parse time.
- ADR metadata is stored on `env.adr_all_adrs` (a dict keyed by docname), following the same pattern as ablog's `env.blog_posts`.
- Timeline HTML is rendered directly in Python (in `collector.py`) rather than using Jinja2 templates, keeping the extension dependency-free beyond Sphinx itself.
- The sidebar template (`adr_nav.html`) uses Jinja2 and is registered via `app.config.templates_path`. Users opt in via `html_sidebars`.
- CSS uses `:has()` selectors for the meta banner border color -- works in all modern browsers.
- CSS custom properties enable dark mode across pydata-sphinx-theme, sphinx-book-theme, and furo.

## Testing workflow

- Tests create temporary Sphinx projects via the `make_project` fixture and run full `sphinx-build` in-process.
- Each test gets its own `tmp_path` so tests are fully isolated.
- The `test_full_demo_build` test builds the actual `docs/` directory as an integration test.
- Timeline HTML assertions scope to the `<!-- /adr-timeline -->` marker to avoid false positives from sidebar content.
- Run `uv run ruff check . && uv run pytest tests/ -v` before committing.

## Versioning

- `VERSION` file at the repo root is the source of truth.
- `sphinx_adr/__init__.py` has `__version__` which must match VERSION.
- On PR merge to master, the `auto-tag.yml` workflow reads VERSION and creates a git tag `v{version}`.
- On tag push, `release.yml` builds and publishes to PyPI.
