# 0002 — docker-compose, not Kubernetes

- **Status:** accepted
- **Date:** 2026-05-01

## Context

The application ([ADR 0001](0001-monolith-not-microservices.md)) is deployed on a
single VPS. A way to orchestrate the containers (web, database, background
worker, reverse proxy) has to be chosen.

## Decision

We use **docker-compose**. Kubernetes / k3s is not used.

## Consequences

**Upsides:**

- For a single node compose is sufficient and simple: the stack is described in one
  file, the commands are obvious.
- Container auto-restart is provided by `restart: unless-stopped` — on a single
  node that *is* "self-healing".
- Minimal overhead: the orchestrator does not eat the resources the application needs.

**Downsides / the cost:**

- No automatic scaling across several nodes and no cluster-level fault tolerance.
  For one VPS that is irrelevant.

On a single node Kubernetes is over-engineering: the orchestrator would consume more
resources than the application itself, and "self-healing" on the only node is exactly
what `restart: unless-stopped` gives.
