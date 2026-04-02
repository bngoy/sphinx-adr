# sphinx-adr example project

A minimal, self-contained example showing how to use the `sphinx-adr` extension in your own Sphinx project.

## Setup & build

```bash
# From the repository root, install sphinx-adr (if not already done)
pip install -e ..        # or: pip install sphinx-adr

# Build the HTML
sphinx-build -b html . _build/html

# Open the result
open _build/html/index.html       # macOS
xdg-open _build/html/index.html   # Linux
```

Or if you're using Pipenv from the repo root:

```bash
cd example
pipenv run sphinx-build -b html . _build/html
```

## What's in here

```
example/
├── conf.py                             # Sphinx config — only needs sphinx_adr in extensions
├── index.rst                           # Landing page with a link to the decision log
└── adr/
    ├── index.rst                       # Decision log page with .. adrlist::
    ├── 0001-record-architecture-decisions.rst   # Accepted ADR
    ├── 0002-use-rest-api.rst                    # Accepted ADR
    ├── 0003-use-postgresql.rst                  # Superseded ADR
    └── 0004-switch-to-mongodb.rst               # Proposed ADR
```

## What you'll see

- **`adr/index.html`** — A vertical timeline showing all ADRs ordered by date (newest first), with color-coded status dots and cards.
- **Each ADR page** — A metadata banner at the top showing the status badge, date, authors, and tags.
