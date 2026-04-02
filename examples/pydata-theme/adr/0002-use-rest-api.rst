ADR-0002: Use REST API for Service Communication
=================================================

.. adr::
   :id: ADR-0002
   :status: Accepted
   :date: 2024-02-20
   :authors: Alice, Bob
   :tags: api, backend

   Services will communicate via RESTful HTTP APIs.

Context and Problem Statement
-----------------------------

Our micro-services need a communication protocol. We need to choose between
REST, gRPC, and GraphQL.

Considered Options
------------------

1. **REST** — simple, well-understood, broad tooling support.
2. **gRPC** — efficient binary protocol, strong typing via protobuf.
3. **GraphQL** — flexible queries, but adds complexity on the server side.

Decision Outcome
----------------

Chosen option: **REST**, because:

- The team has extensive REST experience.
- Tooling (OpenAPI, Swagger) is mature.
- Debugging is straightforward with standard HTTP tools.

Consequences
------------

**Positive:** Easy onboarding, rich ecosystem.

**Negative:** Potentially more round-trips than GraphQL for complex queries.
