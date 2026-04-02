ADR-0002: Adopt ADR Process
===========================

.. adr::
   :status: Accepted
   :date: 2024-02-01
   :authors: Alice, Charlie
   :tags: process, governance

   We will use Architecture Decision Records to document significant decisions.

Context and Problem Statement
-----------------------------

Important architectural decisions are often made in meetings or chat threads and
quickly forgotten. New team members have no way to understand *why* things are
the way they are.

Considered Options
------------------

1. **ADRs in the repo** — lightweight Markdown/RST files committed alongside
   the code.
2. **Wiki pages** — decisions documented in a project wiki.
3. **No formal process** — continue relying on institutional memory.

Decision Outcome
----------------

Chosen option: **ADRs in the repo**, because:

- They live next to the code and are version-controlled.
- They follow the MADR (Markdown Any Decision Record) template.
- They can be rendered as part of the project documentation via ``sphinx-adr``.

Consequences
------------

**Positive:**

- Decisions are discoverable and searchable.
- Context is preserved for future team members.

**Negative:**

- Requires discipline to write ADRs for every significant decision.
