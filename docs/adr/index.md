# Architecture decisions (ADR)

An **ADR** (Architecture Decision Record) is a short note about one significant
architectural decision: the context it was made in, what exactly was decided and what
the consequences are.

## Why this exists

The code shows *how* everything works, but not *why*. A year later (or for a new
person) the reason behind a decision is lost — and it is either "improved" back into
what it moved away from, or left untouched out of fear of the unknown logic. An ADR
records the reason at the moment it is made.

The rules:

- **One decision, one record.** Files are numbered sequentially
  (`0001-...`, `0002-...`).
- **Records are not rewritten after the fact.** If a decision becomes obsolete, a
  **new** record is created with the new decision, and the old one is marked
  `superseded` with a link to the new one. That preserves the history instead of
  replacing it.
- Statuses: `accepted` (in force), `superseded` (replaced), `deprecated`
  (revoked without a replacement).

## The list of decisions

| № | Decision | Status |
|---|---|---|
| [0001](0001-monolith-not-microservices.md) | Monolith, not microservices | accepted |
| [0002](0002-compose-not-k8s.md) | docker-compose, not Kubernetes | accepted |
| [0003](0003-ssr-not-spa.md) | Server-side rendering, not an SPA | accepted |
| [0004](0004-tailwind-compiled-not-cdn.md) | Tailwind is compiled, not from a CDN | accepted |
| [0005](0005-write-lead-to-db-first.md) | The lead is written to the database first | accepted |
| [0006](0006-language-policy.md) | Language policy: English first, Russian as a translation | accepted |

## The template for a new record

```markdown
# NNNN — Short decision title

- **Status:** accepted
- **Date:** YYYY-MM-DD

## Context

Which task or constraint forced the decision.

## Decision

What exactly was decided (in one or two sentences).

## Consequences

What it gives (the upsides) and what it costs (the downsides).
```
