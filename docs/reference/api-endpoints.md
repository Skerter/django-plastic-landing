# API and endpoints

A reference of every URL route in the project. This is a server-rendered site (not a
REST API): most addresses return ready-made HTML pages. The exception is the lead form,
which works over HTMX and returns HTML fragments.

The routes are assembled in [`config/urls.py`](https://github.com/Skerter/django-plastic-landing/blob/main/config/urls.py)
and the `urls.py` files of the included apps.

---

## Pages (`apps.pages`)

| Path | Name | Method | Description |
|---|---|---|---|
| `/` | `home` | GET | The home page. |
| `/dostavka/` | `dostavka` | GET | Delivery. |
| `/o-kompanii/` | `o_kompanii` | GET | About the company (+ the certificate gallery). |
| `/kontakty/` | `kontakty` | GET | Contacts and legal details. |
| `/politika-konfidencialnosti/` | `politika` | GET | Privacy policy. |
| `/soglasie-na-obrabotku-pdn/` | `soglasie` | GET | Personal data processing consent. |

!!! note "Two separate legal documents"
    The privacy policy and the personal data processing consent are **different**
    pages, as 152-FZ requires. See
    [152-FZ compliance](../explanation/compliance-152fz.md).

## Catalog (`apps.catalog`)

Included under the `/catalog/` prefix.

| Path | Name | Method | Description |
|---|---|---|---|
| `/catalog/` | `category_list` | GET | The category list (the catalog hub). |
| `/catalog/<category_slug>/` | `category_detail` | GET | A category with its product list. |
| `/catalog/<category_slug>/<slug>/` | `product_detail` | GET | A product page (specs + gallery + form). |

The path parameters are the category and product `slug`. Only records with
`is_active=True` are shown; missing or hidden ones return **404**.

The queries are optimized: `product_detail` uses `select_related('category')`
and `prefetch_related('specs', 'images')` to avoid multiplying SQL queries.

## Lead form (`apps.leads`)

| Path | Name | Method | Description |
|---|---|---|---|
| `/lead/` | `lead_form` | GET / POST | Lead submission. Works over HTMX. |

### Behaviour

- **GET** — renders an empty form (used as an include on the pages).
- **POST, form valid** — saves the lead, queues the notifications and
  returns the `leads/success.html` fragment ("thank you"). Status **200**.
- **POST, validation errors** — returns the fields fragment with the errors highlighted
  (`leads/form_fields.html`). Status **200** (HTMX swaps the fragment into place).
- **Rate limit exceeded** — the `leads/ratelimit.html` fragment. Status **429**.

### Form fields

| Field | Required | Note |
|---|---|---|
| `name` | yes | The name. |
| `phone` | yes | The phone number. |
| `email` | no | If filled in, the format is validated. |
| `comment` | no | A comment. |
| `type` | — | The lead type (`callback` / `order`). |
| `product` | no | A hidden field — the product pk (on a product page). |
| `consent` | **yes** | Personal data processing consent. Without the checkbox the form is not submitted. |
| `website` | — | Honeypot. An invisible trap field; if filled in, the lead is rejected as spam. |

### Protection

- **CSRF** — on every POST request (the Django standard).
- **Honeypot** — the hidden `website` field; bots fill it in, humans do not.
- **Rate limit** — 5 leads per hour from one IP. Exceeding it returns **429**.
  In development the limit is disabled (`RATELIMIT_ENABLE=False` in `dev`).

## Utility (`apps.core`)

| Path | Name | Method | Description |
|---|---|---|---|
| `/cookie-consent/` | `cookie_consent` | POST | Stores the user's cookie choice. |

## SEO

| Path | Method | Description |
|---|---|---|
| `/sitemap.xml` | GET | The sitemap (categories + products), Django sitemaps. |
| `/robots.txt` | GET | The file for search engine crawlers. |

## Admin

| Path | Method | Description |
|---|---|---|
| `/admin/` | GET / POST | The Django admin panel. Requires an administrator login. |

Working in the admin is described in
[Manage content through the admin](../how-to/add-product-via-admin.md).

## Media (uploaded files)

| Path | Description |
|---|---|
| `/media/...` | Files uploaded through the admin (product photos, certificates). |

In development they are served by Django itself (only when `DEBUG=True`). In production —
through a dedicated nginx service (`media`).

---

## Response code summary

| Code | When |
|---|---|
| **200** | Success; also the form fragments (both success and validation errors). |
| **403** | A missing or invalid CSRF token. |
| **404** | A non-existent or hidden (`is_active=False`) category/product. |
| **429** | The lead rate limit is exceeded (5/hour per IP). |
