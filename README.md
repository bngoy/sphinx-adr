# sphinx-adr

A [Sphinx](https://www.sphinx-doc.org/) extension for documenting **Architecture Decision Records** (ADRs) directly inside your Sphinx documentation.

Inspired by [ablog](https://ablog.readthedocs.io/) (for the directive-based authoring model) and [log4brains](https://github.com/thomvaill/log4brains) (for the timeline UI with status badges).

## Features

- **`.. adr::` directive** — mark any Sphinx page as an ADR with structured metadata (status, date, authors, tags).
- **`.. adrlist::` directive** — generate a vertical timeline / decision log with filtering and sorting.
- **Status badges** — color-coded pills for Proposed, Accepted, Deprecated, and Superseded.
- **Timeline layout** — vertical timeline with status-colored dots, cards, excerpts, and tag pills.
- **Works with any Sphinx theme** — ships its own CSS, looks best with modern themes like alabaster, furo, or pydata-sphinx-theme.
- **Incremental & parallel safe** — integrates cleanly with Sphinx's build system.

## Quick start

### 1. Install

```bash
pip install sphinx-adr
```

Or for local development with Pipenv (see [Development](#development)):

```bash
pipenv install -e ".[dev]"
```

### 2. Enable the extension

In your Sphinx `conf.py`:

```python
extensions = [
    "sphinx_adr",
]
```

### 3. Write an ADR

Create a file such as `adr/0001-use-sphinx.rst`:

```rst
ADR-0001: Use Sphinx for Documentation
=======================================

.. adr::
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

Considered Options
------------------

1. **Sphinx** — mature Python documentation generator.
2. **MkDocs** — Markdown-based static site generator.
3. **Docusaurus** — React-based documentation platform.

Decision Outcome
----------------

Chosen option: **Sphinx**, because it is the de-facto standard for
Python projects and has a rich extension ecosystem.

Consequences
------------

**Positive:** team familiarity, Read the Docs integration.

**Negative:** steeper learning curve for RST newcomers.
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

## Directives reference

### `.. adr::`

Marks the current page as an ADR. Place it near the top of the document, right after the title.

| Option            | Required | Description                                                        |
|-------------------|----------|--------------------------------------------------------------------|
| `:status:`        | yes      | One of `Proposed`, `Accepted`, `Deprecated`, `Superseded`          |
| `:date:`          | no       | Date string, e.g. `2024-01-15`                                     |
| `:authors:`       | no       | Comma-separated author names                                       |
| `:tags:`          | no       | Comma-separated tags for categorisation                            |
| `:superseded-by:` | no       | Docname of the ADR that supersedes this one (when status is Superseded) |

The directive body is used as a short excerpt displayed in the timeline listing.

### `.. adrlist::`

Generates a timeline-based listing of all ADRs in the project.

| Option     | Default     | Description                                            |
|------------|-------------|--------------------------------------------------------|
| `:status:` | *(all)*     | Comma-separated statuses to include, e.g. `Accepted, Proposed` |
| `:tags:`   | *(all)*     | Comma-separated tags to filter by                      |
| `:sort:`   | `date-desc` | Sort order: `date-desc`, `date-asc`, or `status`       |

## Configuration

In `conf.py` you can optionally customise the allowed statuses:

```python
adr_statuses = ["Proposed", "Accepted", "Deprecated", "Superseded"]
```

## Development

### Prerequisites

- Python 3.9+
- [Pipenv](https://pipenv.pypa.io/)

### Setup

```bash
# Clone the repo
git clone https://github.com/bngoy/sphinx-adr.git
cd sphinx-adr

# Create a virtual environment and install dependencies
pipenv install -e ".[dev]"

# Activate the shell
pipenv shell
```

### Build the demo docs

```bash
pipenv run docs
```

Or manually:

```bash
pipenv run sphinx-build -b html docs docs/_build/html
```

Then open `docs/_build/html/index.html` in your browser to see the timeline and sample ADRs.

### Run the tests

```bash
pipenv run test
```

Or manually:

```bash
pipenv run python -m pytest tests/ -v
```

### Project structure

```
sphinx-adr/
├── pyproject.toml              # Package metadata and build config
├── Pipfile                     # Pipenv dependency specification
├── sphinx_adr/
│   ├── __init__.py             # Extension setup, config values
│   ├── directives.py           # AdrDirective, AdrListDirective
│   ├── nodes.py                # Custom docutils nodes (adr_meta, adr_list)
│   ├── collector.py            # Metadata collection & timeline rendering
│   └── static/
│       └── sphinx_adr.css      # Timeline styling, status badges
├── docs/                       # Demo site (dogfoods the extension)
│   ├── conf.py
│   ├── index.rst
│   └── adr/
│       ├── index.rst           # Decision log with .. adrlist::
│       ├── 0001-*.rst          # Sample ADRs
│       ├── 0002-*.rst
│       └── 0003-*.rst
└── tests/
    └── test_extension.py       # 7 tests covering directives, rendering, filtering
```

## License

Apache 2.0 — see [LICENSE](LICENSE).
