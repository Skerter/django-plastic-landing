# 0003 — Server-side rendering, not an SPA

- **Status:** accepted
- **Date:** 2026-05-01

## Context

The site's audience is the Russian B2B market, and search results (SEO) are
critical for it. A page rendering approach has to be chosen: server-side (SSR through
Django templates) or client-side (an SPA on a JS framework).

## Decision

Pages are rendered **on the server** (Django templates). Targeted interactivity
(forms, filters) is built with **HTMX**, without a heavy JS framework.

## Consequences

**Upsides:**

- The crawler receives ready HTML — better indexing than an SPA, where the content
  is loaded by JS.
- Fast first paint, less JS on the client.
- A simpler stack: no separate frontend service is needed ([ADR 0001](0001-monolith-not-microservices.md)).

**Downsides / the cost:**

- Rich client-side interactivity is harder than in an SPA. But the catalog and the forms
  do not need it — HTMX covers what is required (submitting the lead form without a
  page reload, for instance).
