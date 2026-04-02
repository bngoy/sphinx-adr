ADR-0001: Use Sphinx for Documentation
======================================

.. adr::
   :status: Accepted
   :date: 2024-01-15
   :authors: Alice, Bob
   :tags: tooling, documentation

   We will use Sphinx as our primary documentation tool.

Context and Problem Statement
-----------------------------

We need a documentation system that supports multiple output formats, is
well-integrated with Python projects, and allows us to write documentation
alongside the code.

Considered Options
------------------

1. **Sphinx** — mature Python documentation generator with reStructuredText
   and Markdown support.
2. **MkDocs** — Markdown-based static site generator focused on project
   documentation.
3. **Docusaurus** — React-based documentation platform maintained by Meta.

Decision Outcome
----------------

Chosen option: **Sphinx**, because:

- It is the de-facto standard for Python project documentation.
- It supports reStructuredText and Markdown (via MyST).
- It has a rich ecosystem of extensions.
- It generates multiple output formats (HTML, PDF, EPUB).

Consequences
------------

**Positive:**

- Team members already familiar with reStructuredText.
- Easy integration with Read the Docs for hosting.

**Negative:**

- Steeper learning curve for contributors unfamiliar with RST.
