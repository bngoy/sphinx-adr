ADR-0003: Use Python for Backend Services
=========================================

.. adr::
   :id: ADR-0003
   :status: Proposed
   :date: 2024-03-10
   :authors: Bob, Diana
   :tags: backend, language

   We propose using Python as the primary language for backend services.

Context and Problem Statement
-----------------------------

The team is starting work on new backend micro-services. We need to decide on a
primary programming language that balances developer productivity, ecosystem
support, and operational concerns.

Decision Drivers
----------------

- Team expertise and hiring pipeline.
- Availability of libraries for data processing and ML.
- Operational tooling and deployment story.

Considered Options
------------------

1. **Python** — general-purpose language with strong data/ML ecosystem.
2. **Go** — compiled language with excellent concurrency support.
3. **TypeScript (Node.js)** — share language with frontend team.

Decision Outcome
----------------

Proposed option: **Python**, because:

- Most of the team has deep Python experience.
- The data processing and ML libraries (pandas, scikit-learn, etc.) are mature.
- FastAPI/Django provide strong web frameworks.

This decision is still under discussion and has not been formally accepted.

Consequences
------------

**Positive:**

- Faster development due to team familiarity.
- Rich ecosystem for data tasks.

**Negative:**

- Python's GIL may limit CPU-bound concurrency.
- Requires careful dependency management.
