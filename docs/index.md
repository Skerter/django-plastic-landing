# DemoPlast documentation

A Django-based catalog site for a plastic packaging manufacturer.
This is the project's technical documentation: how to run it, how to operate it,
how it is built and why.

The documentation is split into four types following the
[Diátaxis](https://diataxis.fr/) model — each answers a different question.
Pick the one that matches what you need to do right now.

## Tutorials

**"I am here for the first time — walk me through it."**
Step-by-step setup from nothing to a running server.

- [Run the project locally](tutorials/getting-started.md)

## How-to guides

**"I know the context, I need to solve a specific task."**
Recipes for routine operations.

- [Deploy to a server](how-to/deploy.md)
- [Operations: SSH, logs, backups](how-to/operations.md)
- [Manage content through the admin](how-to/add-product-via-admin.md)
- [Enable notification channels](how-to/enable-notification-channels.md)

## Reference

**"I need exact facts: fields, variables, endpoints."**
Exhaustive tables without explanations.

- [Environment variables](reference/environment.md)
- [API and endpoints](reference/api-endpoints.md)
- [Data model](reference/data-model.md)

## Explanation

**"I want to understand why it is built this way."**
The context behind the architectural decisions.

- [Architecture](explanation/architecture.md)
- [152-FZ compliance](explanation/compliance-152fz.md)
- [Decisions (ADR)](adr/index.md)

---

English is the source of truth for this documentation; the Russian version is a
translation ([ADR-0006](adr/0006-language-policy.md)).

Source code and project overview — in the
[repository README](https://github.com/Skerter/django-plastic-landing#readme).
