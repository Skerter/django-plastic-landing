# 152-FZ compliance

152-FZ is the Russian personal data law. The site collects a name, a phone number and
(optionally) an email, so it has to comply. This section explains
**how the requirements of the law are implemented in the code** — so that future changes
do not break them by accident.

!!! warning "This is not legal advice"
    Only the mechanics in the code are described here. The final texts of the consent and
    the privacy policy are prepared and reviewed by the company's lawyer — we build the
    mechanism, we do not compose legal wording.

## Consent is a separate document

The personal data processing consent and the privacy policy
**must not be merged** — the law requires two different documents. On the site they
correspond to two separate pages:

- `/soglasie-na-obrabotku-pdn/` — the personal data processing consent;
- `/politika-konfidencialnosti/` — the privacy policy.

When making changes, do not merge them into a single page.

## The consent checkbox

Three rules, all enforced on the backend:

- **The checkbox is not pre-checked.** The user ticks it themselves.
- **Without the tick the form is not submitted** — `consent` is declared as a required
  form field (`required=True` in
  [`apps/leads/forms.py`](https://github.com/Skerter/django-plastic-landing/blob/main/apps/leads/forms.py)).
  Validation happens on the server, not just on the frontend: even if the JS is bypassed,
  a lead without consent does not go through.
- **The fact of consent is recorded.** The lead (`Lead`) stores `consent=True`
  together with `created_at` — leaving a record that consent was given and when.

## Data minimisation

We collect only what is necessary: the name and the phone number are required, the email
is not. There are no extra fields in the form — that too is a requirement of the law
(minimisation). When extending the form, do not add fields "just in case".

## Localisation: the data stays in Russia

The law requires the personal data of Russian citizens to be stored on Russian territory.
Hence:

- **The VPS is in a Russian data centre**, and the database is there too.
- **No foreign analytics services.** Google Analytics is prohibited — only
  Yandex.Metrica (a Russian service) is used.
- **Personal data does not leave the country even for internal purposes.** For example,
  names, phone numbers and emails are stripped before errors are sent to Sentry
  (`config/sentry.py`, `before_send`) — only a traceback without personal data leaves.

This also explains the caution around external notification channels: a channel that
pushes data through a foreign service must not let personal data cross the border in
the process.

## Cookies and Yandex.Metrica

Metrica is an analytics cookie, so it is loaded **only after the user's explicit
consent**:

- The cookie consent banner splits cookies into **necessary** (session, CSRF —
  always active) and **analytics** (Metrica).
- The user's choice is stored in a dedicated `cookie_consent` cookie
  ([`apps/core/views.py`](https://github.com/Skerter/django-plastic-landing/blob/main/apps/core/views.py)).
- The Metrica script is **injected into the template only with consent**. In `base.html`
  the Metrica block is rendered under the condition
  `request.COOKIES.cookie_consent == 'accepted'` (and a non-empty counter ID).
  Without consent, `tag.js` is not loaded at all.

The decision is made on the server, in the template, from the cookie value — which is
more reliable than trusting client-side code.

## A checklist for the client (outside the code)

These items are the company's responsibility rather than the developers', but they are
worth a reminder:

- file the personal data operator notification with Roskomnadzor;
- have a lawyer review the final consent and policy texts;
- if the data is passed to third parties (amoCRM, for example), that has to be stated
  in the consent (the processing purposes and the list of data).
