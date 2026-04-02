# DESIGN.md

Architecture and design decisions for the sphinx-adr extension.

## Problem statement

Teams using Sphinx for documentation lack a native way to capture Architecture Decision Records (ADRs) as first-class document types. Existing solutions either live outside the documentation (standalone Markdown tools like adr-tools, log4brains) or require manual HTML/template work. There is no Sphinx extension that provides:

1. A structured directive for ADR metadata (id, status, date, authors, tags).
2. An auto-generated timeline view of all decisions.
3. A sidebar navigation scoped to ADR pages.
4. Dark mode support across popular Sphinx themes.

**Goal**: Build a zero-dependency (beyond Sphinx) extension that integrates ADRs into Sphinx as naturally as ablog integrates blog posts.

## Architecture overview

```
                  ┌─────────────────────────────────────────────┐
                  │              Sphinx build pipeline           │
                  └─────────────────────────────────────────────┘
                         │                    │
        ┌────────────────┤                    ├────────────────┐
        ▼                ▼                    ▼                ▼
  ┌──────────┐    ┌──────────┐     ┌──────────────┐    ┌──────────────┐
  │ Directive │    │ Directive │     │   Collector   │    │  HTML output │
  │  .. adr:: │    │..adrlist::│     │  (events)     │    │  + CSS + JS  │
  └────┬─────┘    └────┬─────┘     └──────┬───────┘    └──────────────┘
       │               │                  │
       │  Stores       │  Emits           │ Replaces adr_list nodes
       │  metadata     │  adr_list        │ with timeline HTML;
       │  in env       │  placeholder     │ injects sidebar context
       ▼               ▼                  ▼
  ┌──────────────────────────────────────────┐
  │        env.adr_all_adrs (dict)           │
  │   docname → {id, status, date, ...}      │
  └──────────────────────────────────────────┘
```

### Component responsibilities

| Component          | File                | Role                                              |
|--------------------|---------------------|----------------------------------------------------|
| `AdrDirective`     | `directives.py`     | Parse `:id:`, `:status:`, etc.; store in env       |
| `AdrListDirective` | `directives.py`     | Emit placeholder node with filter/sort options     |
| `adr_meta` node    | `nodes.py`          | Render metadata banner at top of ADR pages         |
| `adr_list` node    | `nodes.py`          | Placeholder replaced by timeline at resolve time   |
| Collector          | `collector.py`      | Event handlers: init, purge, merge, resolve, inject|
| CSS                | `static/sphinx_adr.css` | All visual styling, dark mode, responsive      |
| Sidebar template   | `templates/adr_nav.html` | Jinja2 template for sidebar navigation        |
| Setup              | `__init__.py`       | Wire everything together, register config values   |

## Design decisions

### 1. Directive-based authoring over standalone tooling

**Decision**: ADRs are written as regular Sphinx RST documents with a `.. adr::` directive, not as standalone Markdown files processed by external tools.

**Rationale**: Keeps ADRs inside the documentation build. Authors use familiar RST syntax. ADRs participate in Sphinx's cross-referencing, search indexing, and toctree navigation.

**Trade-off**: Requires Sphinx knowledge; cannot be used outside a Sphinx project.

### 2. Store metadata on the build environment

**Decision**: ADR metadata is stored in `env.adr_all_adrs`, a dict keyed by docname, following ablog's `env.blog_posts` pattern.

**Rationale**: The Sphinx environment is the standard mechanism for sharing data across documents during a build. Using it gives us incremental build support (via `env-purge-doc`) and parallel build support (via `env-merge-info`) for free.

**Trade-off**: Metadata is only available during the build, not at import time.

### 3. ID as a required field

**Decision**: The `:id:` option is required on every `.. adr::` directive.

**Rationale**: ADRs are inherently numbered documents (ADR-0001, ADR-0002, ...). The ID appears in timelines and the sidebar as a distinct teal badge, giving readers an immediate visual reference. Making it required ensures every record is identifiable.

**Trade-off**: Slightly more boilerplate per ADR document.

### 4. Server-side timeline rendering over Jinja2 templates

**Decision**: Timeline HTML is built in Python (`_render_timeline()` in `collector.py`) rather than via Jinja2 templates.

**Rationale**: Keeps the extension dependency-free beyond Sphinx itself. The timeline is static content that doesn't need template inheritance or theme-specific overrides. Python string building is simpler to test and debug.

**Trade-off**: Harder to customize the timeline HTML without modifying the extension source. The sidebar template (`adr_nav.html`) does use Jinja2, since it needs to integrate with theme-specific sidebar mechanisms.

### 5. ablog-style sidebar pattern

**Decision**: The sidebar is provided as a Jinja2 template (`adr_nav.html`) that users opt into via `html_sidebars` glob patterns, exactly like ablog.

**Rationale**: This is the established Sphinx pattern for page-scoped sidebars. Regular pages keep their normal theme sidebar. ADR pages get the timeline navigation. Users have full control over which pages show what.

**Trade-off**: Requires users to add `html_sidebars` configuration. More explicit than auto-injection, but also more predictable.

### 6. CSS custom properties for theme compatibility

**Decision**: All colors are defined as CSS custom properties (`:root` variables) with overrides for `html[data-theme="dark"]` and `@media (prefers-color-scheme: dark)`.

**Rationale**: This is the only approach that works across alabaster, pydata-sphinx-theme, sphinx-book-theme, and furo without theme-specific CSS files. Each theme uses a different dark mode mechanism, but CSS custom properties handle all of them.

**Trade-off**: Requires modern browsers (CSS custom properties are supported in all browsers since 2017). The `:has()` selector used for meta banner borders requires 2023+ browsers.

### 7. Three visual badge types with distinct styling

**Decision**: ID badges (teal, monospace, square corners), status badges (colored pills, rounded), and tag pills (gray, small, rounded) each have distinct visual styles.

**Rationale**: Users scanning a timeline need to instantly distinguish between an ADR's identifier, its lifecycle status, and its categorization tags. Different colors, shapes, and fonts make this effortless.

**Trade-off**: More CSS to maintain, but each badge type serves a clear purpose.

### 8. Status validation at parse time

**Decision**: Invalid status values cause a build warning and the ADR is not registered. Valid values are Proposed, Accepted, Deprecated, Superseded.

**Rationale**: Catching errors early (during RST parsing) rather than at render time gives better error messages with source locations. The fixed status set ensures consistent badge colors.

**Trade-off**: Adding new statuses requires changing `VALID_STATUSES` in `directives.py`.

### 9. VERSION file as version source of truth

**Decision**: A plain `VERSION` file at the repo root holds the release version. `__init__.py` has a matching `__version__`. The CI auto-tag workflow reads VERSION to create git tags.

**Rationale**: Separating the version from Python code makes it easy for CI scripts to read and bump. Hatchling reads `__version__` from `__init__.py` for building. The VERSION file drives the release pipeline.

**Trade-off**: Two places to update (VERSION and `__init__.py`), but the release workflow validates they match.

### 10. Separate CI workflows for lint, tag, and release

**Decision**: Three GitHub Actions workflows: `ci.yml` (lint + test on every push/PR), `auto-tag.yml` (tag from VERSION on PR merge to master), `release.yml` (build + publish to PyPI on tag).

**Rationale**: Separation of concerns. Lint/test runs on every change. Tagging only happens on merge. Publishing only happens on tag. Each workflow has a single responsibility and clear trigger.

**Trade-off**: More workflow files, but each is simple and independently debuggable.

## Data flow

### Build-time data flow

```
RST source files
    │
    ├── .. adr:: directive
    │       │
    │       ├── Validates :id: (required)
    │       ├── Validates :status: (required, must be in VALID_STATUSES)
    │       ├── Parses :date:, :authors:, :tags:, :superseded-by:
    │       ├── Stores metadata → env.adr_all_adrs[docname]
    │       └── Emits adr_meta node → rendered as metadata banner
    │
    └── .. adrlist:: directive
            │
            └── Emits adr_list node (placeholder)

            ┌─── doctree-resolved event ───┐
            │                               │
            │  process_adr_lists():         │
            │  1. Collect all ADRs from env │
            │  2. Apply status/tag filters  │
            │  3. Sort by date/status       │
            │  4. Resolve titles from env   │
            │  5. Build timeline HTML       │
            │  6. Replace adr_list node     │
            └───────────────────────────────┘

            ┌─── html-page-context event ───┐
            │                                │
            │  inject_adr_nav_context():     │
            │  1. Sort all ADRs by date      │
            │  2. Resolve URIs and titles     │
            │  3. Set adr_nav_entries in ctx  │
            └────────────────────────────────┘
```

### Incremental build support

```
env-purge-doc(docname)  →  Remove docname from env.adr_all_adrs
env-merge-info(other)   →  Merge other.adr_all_adrs into env.adr_all_adrs
```

## HTML output structure

### Meta banner (top of each ADR page)

```html
<div class="adr-meta">
  <span class="adr-id">ADR-0001</span>
  <span class="adr-status adr-status-accepted">Accepted</span>
  <span class="adr-date">2024-01-15</span>
  <span class="adr-authors">Authors: Alice, Bob</span>
  <span class="adr-tags">
    <span class="adr-tag">tooling</span>
    <span class="adr-tag">documentation</span>
  </span>
</div>
```

### Timeline card (generated by `.. adrlist::`)

```html
<div class="adr-timeline">
  <div class="adr-timeline-item adr-timeline-accepted">
    <div class="adr-timeline-dot adr-dot-accepted"></div>
    <div class="adr-timeline-content">
      <div class="adr-timeline-header">
        <span class="adr-id">ADR-0001</span>
        <a href="0001-use-sphinx.html" class="adr-timeline-title">
          ADR-0001: Use Sphinx for Documentation
        </a>
        <span class="adr-status adr-status-accepted">Accepted</span>
      </div>
      <div class="adr-timeline-meta">
        <span class="adr-timeline-date">2024-01-15</span> &middot;
        <span class="adr-timeline-authors">Alice, Bob</span>
      </div>
      <p class="adr-timeline-excerpt">We will use Sphinx as our primary documentation tool.</p>
      <div class="adr-timeline-tags">
        <span class="adr-tag">tooling</span>
        <span class="adr-tag">documentation</span>
      </div>
    </div>
  </div>
  <!-- more items... -->
</div><!-- /adr-timeline -->
```

### Sidebar navigation

```html
<div class="adr-sidebar-nav">
  <p class="adr-sidebar-heading">Decision log</p>
  <div class="adr-sidebar-timeline">
    <a href="0001-use-sphinx.html" class="adr-sidebar-entry adr-sidebar-current">
      <span class="adr-sidebar-dot adr-dot-accepted"></span>
      <span class="adr-sidebar-info">
        <span class="adr-sidebar-title">
          <span class="adr-id">ADR-0001</span> ADR-0001: Use Sphinx
        </span>
        <span class="adr-status adr-status-accepted">Accepted</span>
      </span>
    </a>
    <!-- more entries... -->
  </div>
</div>
```

## CI/CD pipeline

```
                    Push / PR to any branch
                            │
                            ▼
                    ┌───────────────┐
                    │   ci.yml      │
                    │               │
                    │  1. Checkout  │
                    │  2. uv sync   │
                    │  3. ruff check│
                    │  4. ruff fmt  │
                    │  5. pytest    │
                    └───────────────┘

                    PR merged to master
                            │
                            ▼
                    ┌───────────────┐
                    │ auto-tag.yml  │
                    │               │
                    │  1. Checkout  │
                    │  2. Read      │
                    │     VERSION   │
                    │  3. Check if  │
                    │     tag exists│
                    │  4. Create    │
                    │     v{ver}    │
                    │     tag       │
                    └───────┬───────┘
                            │ (tag pushed)
                            ▼
                    ┌───────────────┐
                    │ release.yml   │
                    │               │
                    │  1. Checkout  │
                    │  2. uv build  │
                    │  3. twine     │
                    │     upload    │
                    │     (PyPI)    │
                    │  4. GH release│
                    └───────────────┘

Secrets required:
  - PYPI_API_TOKEN: PyPI API token for publishing
```
