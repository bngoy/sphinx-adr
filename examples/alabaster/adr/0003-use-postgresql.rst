ADR-0003: Use PostgreSQL as Primary Database
============================================

.. adr::
   :id: ADR-0003
   :status: Superseded
   :date: 2024-03-05
   :authors: Charlie
   :tags: database, backend
   :superseded-by: adr/0004-switch-to-mongodb

   PostgreSQL will be the primary data store for all services.

Context and Problem Statement
-----------------------------

We need a primary database for our application data. The main candidates are
PostgreSQL and MongoDB.

Decision Outcome
----------------

We initially chose **PostgreSQL** for its ACID compliance and relational model.

This decision was later **superseded** by ADR-0004 as requirements evolved
towards a document-oriented data model.
