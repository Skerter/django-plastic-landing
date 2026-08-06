# 0004 — Tailwind is compiled, not from a CDN

- **Status:** accepted
- **Date:** 2026-05-01

## Context

The markup uses Tailwind CSS. It can be included in two ways: as a script from a CDN
(generating the classes in the browser) or by compiling a ready CSS file at build
time.

## Decision

Tailwind is **compiled** through `django-tailwind` (the CLI). The CDN include is not
used in production.

## Consequences

**Upsides:**

- A small CSS file ships to production — only the classes actually used (purge),
  not the whole library.
- No dependency on an external CDN: the site does not break if the CDN is unavailable,
  and it does not pull data from a third-party domain.
- Stable performance — the styles are not generated in the browser on every visit.

**Downsides / the cost:**

- A CSS build step (`tailwind build`) is needed whenever the classes in the templates
  change. It is a one-off command, and dev has a watch mode.

Including Tailwind from a CDN in production is a well-known anti-pattern (slower,
heavier, an external dependency), so we compile it.
