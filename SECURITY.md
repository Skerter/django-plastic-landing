# Security policy

**Language:** English · [Русский](SECURITY.ru.md)

## Supported versions

This is a showcase project developed as a rolling release: the only supported branch is
`main`. Security fixes land there only; individual major/minor releases are not
maintained. Before reporting a vulnerability, make sure you can reproduce it on current
`main`.

| Version           | Supported          |
| ----------------- | ------------------ |
| `main` (latest)   | :white_check_mark: |
| Older commits     | :x:                |

## Reporting a vulnerability

**Please do not report vulnerabilities through public GitHub Issues or Pull Requests** —
that discloses the problem before it can be fixed.

Report privately through one of these channels:

- **GitHub Security Advisories** — the repository's *Security → Report a vulnerability* tab
  ([private report](https://github.com/Skerter/django-plastic-landing/security/advisories/new)).
  The preferred channel.
- **Email** — [geopank55@gmail.com](mailto:geopank55@gmail.com) with the subject `[SECURITY] django-plastic-landing`.

Where possible, include in the report:

- a description of the vulnerability and its potential impact;
- reproduction steps or a PoC;
- the affected commit/file and, if you have one, a suggested fix.

### What to expect

- **Acknowledgement of receipt** — within 5 business days.
- **Initial assessment** — within 14 days: accepted or rejected, with the reasoning.
- **If accepted** — we agree on a fix timeline, ship the fix in `main` and credit you in the
  acknowledgements (if you are happy with that). Coordinated disclosure is welcome.
- **If rejected** — we explain why (for example, expected behaviour or out of the threat model).

## Scope

This is an **anonymized showcase** of a real commercial project. The demo runs in
`DEMO_MODE` without real credentials, and the client's data is replaced by a fictional
company. Accordingly:

- The public demo deployment and its infrastructure are **out of scope** for security
  reports — it deliberately contains fictional data.
- What is of interest are vulnerabilities in the **code** of this repository: lead form
  handling, background tasks, personal-data scrubbers, Django security settings.

Please account for the measures already built in — these are not vulnerabilities: CSRF on
every form, a honeypot and `django-ratelimit` on the lead form,
`SECURE_SSL_REDIRECT`/HSTS/`*_COOKIE_SECURE` in production, and the personal-data scrubber
for Sentry (`config/sentry.py`).

Thank you for helping keep the project secure.
