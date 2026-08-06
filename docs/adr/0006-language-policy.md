# 0006 — Language policy: English first, Russian as a translation

- **Status:** accepted
- **Date:** 2026-08-06

## Context

The repository is a public showcase. Its README is in English and its badges point at
a live demo, but everything an interested reader opens next — the whole of `docs/`,
`SECURITY.md`, the inline comments — used to be in Russian. A foreign developer coming
from the README hit a wall on the second click.

The earlier version of this record fixed the opposite policy ("split by audience:
`docs/` in Russian") and referred to `CLAUDE.md §18`, a file that does not exist in this
repository — the reference was inherited from the private source project. So the rule
was both wrong for a public repository and partly unverifiable.

The question is which language the project is *authored* in, not which languages it is
readable in.

## Decision

**English is the project's first language.** Russian stays as a full translation where
the reader is Russian-speaking by definition.

- **English — the source of truth:** `docs/` (all pages), `README.md`, `SECURITY.md`,
  code identifiers, inline comments, docstrings, commit messages, CI workflow comments.
- **Russian — a translation and the client-facing UI:** the `*.ru.md` pages of `docs/`
  published at `/ru/`, `README.ru.md`, `SECURITY.ru.md`, and everything user-facing in
  the Django admin (`verbose_name`, `help_text`, fieldsets) — the admin is the
  Russian-speaking client's workplace, a product interface rather than documentation.

The documentation site is built by `mkdocs-static-i18n` in suffix mode: `deploy.md` is
the English source, `deploy.ru.md` its translation. English is served at `/`, Russian at
`/ru/`, with a language switcher in the header.

**When the versions disagree, the English one is correct.** A translation may lag; the
source may not.

## Consequences

**Upsides:**

- The repository is legible end to end for an outside reader — README, docs, security
  policy and code comments are all in one language.
- The Russian reader loses nothing: the translation is complete, 1:1, on the same site.
- The rule is explicit, so new pages and new code do not reintroduce a mixture.

**Downsides / the cost:**

- Every documentation change has to be made twice, in `page.md` and `page.ru.md`.
  Forgetting the second one leaves a stale translation (mitigated by the rule above:
  English wins).
- The existing Russian inline comments and docstrings now contradict the policy. They
  are migrated separately, as a follow-up — this record states the target, not a
  completed state.

## History

- **2026-06-29 — 2026-08-06:** the policy was "split by audience": English for the
  outward-facing shell (README, commits, identifiers), Russian for everything the
  working team used (`docs/`, comments, docstrings, the admin).
- **2026-08-06:** replaced by the current policy. The record was rewritten in place
  rather than superseded by a new one, so this section keeps the trace of the change.
