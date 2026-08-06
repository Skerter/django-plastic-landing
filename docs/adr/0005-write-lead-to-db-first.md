# 0005 — The lead is written to the database first

- **Status:** accepted
- **Date:** 2026-05-01

## Context

Every lead from the site has to reach a sales manager and (where possible) amoCRM.
External systems are unreliable: amoCRM can be unavailable, a token can expire, the
network can fail. The lead must not be lost in the process, and the user must not
wait for the CRM's response.

## Decision

The lead is **saved to the local database first** (the source of truth), and only
then sent to the external channels (email/Telegram/amoCRM) — **asynchronously**, through
a background worker. The form's HTTP response does not wait for the external systems.

## Consequences

**Upsides:**

- The lead is not lost when any external channel fails — it is already in the database
  and visible in the admin.
- The form answers "thank you" instantly, independent of the CRM's speed or availability.
- One channel failing neither breaks the form nor affects the other channels; failed
  sends are retried.

**Downsides / the cost:**

- A background worker (`qcluster`) and a task queue are required — an extra moving
  part in production.
- Delivery to the external systems becomes "eventual" rather than instant, which is
  acceptable for lead notifications.

The implementation details of the flow — [Architecture](../explanation/architecture.md);
the channel setup — [Notification channels](../how-to/enable-notification-channels.md).
