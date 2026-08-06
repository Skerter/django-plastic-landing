# 0001 — Monolith, not microservices

- **Status:** accepted
- **Date:** 2026-05-01

## Context

The project is a catalog site with lead generation: a handful of pages, a catalog and
lead forms. The amount of business logic is small. The overall application structure
has to be chosen.

## Decision

We build **a single Django monolith**. No splitting into microservices, no separate
frontend service.

## Consequences

**Upsides:**

- Easier to develop and to understand — all the code in one place, one deployment.
- Cheaper to operate: no network calls between services, no orchestration,
  fewer points of failure.
- Transactions and relations between data work out of the box (a single database).

**Downsides / the cost:**

- It can only be scaled as a whole (not a problem for the current load).
- Under heavy feature growth the monolith would have to be split — but for six
  pages and some forms that is not on the horizon.

There is nothing to justify splitting into microservices: the complexity of the
orchestration would exceed the complexity of the application itself.
