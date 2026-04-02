ADR-0004: Switch to MongoDB for Document Storage
=================================================

.. adr::
   :status: Proposed
   :date: 2024-04-18
   :authors: Diana, Charlie
   :tags: database, backend

   We propose switching from PostgreSQL to MongoDB for our primary data store.

Context and Problem Statement
-----------------------------

After six months of development, we have found that most of our data is
document-oriented and the relational model adds unnecessary complexity.
Frequent schema migrations are slowing down the team.

Decision Drivers
----------------

- 80% of queries fetch/store entire documents.
- Schema changes happen weekly during the current phase.
- The team wants to reduce migration overhead.

Considered Options
------------------

1. **Stay with PostgreSQL** — use JSONB columns for flexible data.
2. **Switch to MongoDB** — native document model, flexible schema.

Decision Outcome
----------------

Proposed option: **MongoDB**, because the document model better fits our access
patterns and reduces operational friction from migrations.

This decision is currently under review and has not yet been formally accepted.

Consequences
------------

**Positive:** Faster iteration, natural fit for document data.

**Negative:** Loss of strong relational constraints, team needs MongoDB training.
