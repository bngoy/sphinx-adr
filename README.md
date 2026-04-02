# sphinx-adr

A [Sphinx](https://www.sphinx-doc.org/) extension for documenting **Architecture Decision Records** (ADRs) directly inside your Sphinx documentation.

Inspired by [ablog](https://ablog.readthedocs.io/) (for the directive-based authoring model) and [log4brains](https://github.com/thomvaill/log4brains) (for the timeline UI with status badges).

## Features

- **`.. adr::` directive** -- mark any Sphinx page as an ADR with structured metadata (id, status, date, authors, tags).
- **`.. adrlist::` directive** -- generate a vertical timeline / decision log with filtering and sorting.
- **Sidebar navigation** -- compact timeline sidebar on ADR pages (ablog-style `html_sidebars` pattern).
- **Status badges** -- color-coded pills for Proposed, Accepted, Deprecated, and Superseded.
- **ID badges** -- teal monospace badge for each record's identifier, visually distinct from status and tags.
- **Timeline layout** -- vertical timeline with status-colored glowing dots, cards, excerpts, and tag pills.
- **Works with any Sphinx theme** -- tested with alabaster, pydata-sphinx-theme, and sphinx-book-theme.
- **Dark mode support** -- automatically adapts to light/dark mode on pydata-sphinx-theme, sphinx-book-theme, and furo.
- **Incremental & parallel safe** -- integrates cleanly with Sphinx's build system.

## Quick start

### 1. Install

```bash
pip install sphinx-adr
```

### 2. Enable the extension

In your Sphinx `conf.py`:

```python
extensions = ["sphinx_adr"]

# Path to ADR documents (default: "adr")
adr_path = "adr"

# Show the ADR sidebar only on ADR pages (ablog-style pattern)
html_sidebars = {
    "adr/*": ["adr_nav.html"],
}
```

### 3. Write an ADR

Create a file such as `adr/0001-use-sphinx.rst`:

```rst
ADR-0001: Use Sphinx for Documentation
=======================================

.. adr::
   :id: ADR-0001
   :status: Accepted
   :date: 2024-01-15
   :authors: Alice, Bob
   :tags: tooling, documentation

   We will use Sphinx as our primary documentation tool.

Context and Problem Statement
-----------------------------

We need a documentation system that supports multiple output formats,
is well-integrated with Python projects, and allows us to write
documentation alongside the code.

Decision Outcome
----------------

Chosen option: **Sphinx**, because it is the de-facto standard for
Python projects and has a rich extension ecosystem.
```

### 4. Create a decision log page

```rst
Architecture Decision Log
=========================

.. adrlist::

.. toctree::
   :hidden:

   0001-use-sphinx
   0002-adopt-adr-process
```

### 5. Build

```bash
sphinx-build -b html docs docs/_build/html
```

## Directive reference

### `.. adr::`

Marks the current page as an ADR. Place it near the top of the document, right after the title.

| Option            | Required | Description                                                            |
|-------------------|----------|------------------------------------------------------------------------|
| `:id:`            | **yes**  | Unique identifier for the ADR, e.g. `ADR-0001`                        |
| `:status:`        | **yes**  | One of `Proposed`, `Accepted`, `Deprecated`, `Superseded`              |
| `:date:`          | no       | Date string, e.g. `2024-01-15`                                        |
| `:authors:`       | no       | Comma-separated author names                                          |
| `:tags:`          | no       | Comma-separated tags for categorisation                                |
| `:superseded-by:` | no       | Docname of the ADR that supersedes this one (when status is Superseded)|

The directive body is used as a short excerpt displayed in the timeline listing.

### `.. adrlist::`

Generates a timeline-based listing of all ADRs in the project.

| Option     | Default     | Description                                                    |
|------------|-------------|----------------------------------------------------------------|
| `:status:` | *(all)*     | Comma-separated statuses to include, e.g. `Accepted, Proposed` |
| `:tags:`   | *(all)*     | Comma-separated tags to filter by                              |
| `:sort:`   | `date-desc` | Sort order: `date-desc`, `date-asc`, or `status`               |

## Configuration

| Config value    | Default                                              | Description                        |
|-----------------|------------------------------------------------------|------------------------------------|
| `adr_path`      | `"adr"`                                              | Directory containing ADR documents |
| `adr_statuses`  | `["Proposed", "Accepted", "Deprecated", "Superseded"]` | Allowed status values            |

### Sidebar setup (ablog-style)

The extension provides an `adr_nav.html` sidebar template. Use Sphinx's `html_sidebars` to control which pages display it:

```python
# Show ADR sidebar only on pages under adr/
html_sidebars = {
    "adr/*": ["adr_nav.html"],
}
```

Regular pages keep their normal theme sidebar. This follows the same pattern as [ablog](https://ablog.readthedocs.io/).

## Interactive controls

### Timeline

- **Hover** on a timeline card to see an elevated shadow and glowing status dot.
- **Click** the title link to navigate to the full ADR document.
- **Filter** ADRs by status or tags using `.. adrlist::` options.

### Sidebar navigation

- **Current page** is highlighted with bold text and link color.
- **Hover** on any entry to see the title highlighted and dot glow.
- Each entry shows the **ID badge**, **title**, and **status pill** at a glance.

## Theme compatibility

| Theme                  | Light mode | Dark mode | Notes                          |
|------------------------|:----------:|:---------:|--------------------------------|
| alabaster              | yes        | --        | Sphinx default, no dark mode   |
| pydata-sphinx-theme    | yes        | yes       | Toggle via navbar switcher     |
| sphinx-book-theme      | yes        | yes       | Built on pydata, same mechanism|
| furo                   | yes        | yes       | Via `prefers-color-scheme`     |

## Development

### Prerequisites

- Python 3.9+
- [uv](https://docs.astral.sh/uv/)

### Setup

```bash
git clone https://github.com/bngoy/sphinx-adr.git
cd sphinx-adr

# Install in development mode
uv sync --extra dev
```

### Common commands

```bash
# Run tests
uv run pytest tests/ -v

# Lint and format
uv run ruff check .
uv run ruff format .

# Build demo docs
uv run sphinx-build -b html docs docs/_build/html

# Build theme examples (requires examples extra)
uv sync --extra examples
uv run sphinx-build -b html examples/pydata-theme examples/pydata-theme/_build/html
uv run sphinx-build -b html examples/book-theme examples/book-theme/_build/html
uv run sphinx-build -b html examples/alabaster examples/alabaster/_build/html
```

### Project structure

```
sphinx-adr/
├── VERSION                     # Single source of truth for package version
├── pyproject.toml              # Package metadata, build config, ruff config, uv scripts
├── sphinx_adr/
│   ├── __init__.py             # Extension setup, config values, version
│   ├── directives.py           # AdrDirective, AdrListDirective
│   ├── nodes.py                # Custom docutils nodes (adr_meta, adr_list)
│   ├── collector.py            # Metadata collection & timeline rendering
│   ├── templates/
│   │   └── adr_nav.html        # Sidebar navigation Jinja2 template
│   └── static/
│       └── sphinx_adr.css      # Timeline styling, status/ID badges, dark mode
├── docs/                       # Demo site (dogfoods the extension)
│   ├── conf.py
│   ├── index.rst
│   └── adr/                    # Sample ADRs
├── examples/                   # Theme-specific examples
│   ├── alabaster/
│   ├── pydata-theme/
│   └── book-theme/
├── tests/
│   ├── conftest.py             # make_project fixture
│   └── test_extension.py       # 7 tests
└── .github/workflows/
    ├── ci.yml                  # Lint + test on every push/PR
    ├── auto-tag.yml            # Tag repo from VERSION on PR merge
    └── release.yml             # Build and publish to PyPI on tag
```

## License

Apache 2.0 -- see [LICENSE](LICENSE).
