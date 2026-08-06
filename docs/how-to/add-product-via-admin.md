# Manage content through the admin

How to fill and edit the site through the Django admin panel:
the catalog, contacts, legal details, certificates. No programming needed.

The admin lives at `/admin/` (locally —
[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)). Sign in with an
administrator login and password. If you do not have an account yet, create one with
the `createsuperuser` command (see [Run the project locally](../tutorials/getting-started.md),
step 5).

!!! note "The admin interface is in Russian"
    The admin is the client's workplace, so its labels are Russian
    ([ADR-0006](../adr/0006-language-policy.md)). Section names below are given as
    they appear on screen, with an English gloss in brackets. Model field names
    (`Name`, `Slug`, `Image`, …) are shown as-is.

## How the catalog is structured

The catalog has three levels:

- **Категория** (category, for example "Канистры", "Крышки") — a catalog section.
- **Товар** (product) belongs to exactly one category.
- A product has **specs** and **photos** — they are edited right
  inside the product form, there is no need to create them separately.

## Add a category

1. On the admin home page → **Категории** (Categories) → **Добавить категорию** (Add category).
2. Fill in:
   - **Name** — the title ("Канистры").
   - **Slug** — part of the URL. Filled automatically from the title; for
     Cyrillic titles type the Latin form by hand (`kanistry`). It ends up in the URL:
     `/catalog/kanistry/`.
   - **Image** — the section picture (optional).
   - **Order** — the sort order (a lower number is higher in the list).
   - **Is active** — clear the checkbox to hide the category from the site
     without deleting it.
3. **Сохранить** (Save).

## Add a product

1. **Товары** (Products) → **Добавить товар** (Add product).
2. Fill in the main fields:
   - **Category** — pick a category.
   - **Name** — the product title.
   - **Slug** — in Latin characters (`kanistra-20l`). It ends up in the URL:
     `/catalog/kanistry/kanistra-20l/`.
   - **Метка (badge)** — a short label over the photo in the card
     ("Евроканистра", "Круглая"). Optional.
   - **Description** — the product description.
   - **Image** — the main photo of the card.
   - **Order**, **Is active** — same as for a category.
   - **Meta title / Meta description** — tags for search engines (SEO).
     If empty, the regular title and description are used.
3. **Характеристики** (specs) and **Фото товара** (product photos) are added lower in
   the same form — see the next two sections.
4. **Сохранить** (Save).

### Product specs

Specs are "parameter → value" pairs (volume, weight, material).
The set differs from product to product, so the fields are free-form.

In the product form, in the **Характеристики** (Specs) block:

- **Label** — the parameter name ("Объём").
- **Value** — the value ("20").
- **Unit** — the unit of measurement ("л"). Optional.
- **Order** — the position in the specs table.

To add another row, fill in the empty one at the bottom; to remove a row,
tick **Delete**. Everything is saved together with the product.

### Product photos (gallery)

In the **Фото товара** (Product photos) block:

- **Image** — the photo file.
- **Подпись (alt)** — the angle or a description ("вид сбоку", "горловина 55 мм").
  Used as the alt text and the thumbnail caption.
- **Order** — the position in the gallery.

On the product page these photos are shown as a carousel with thumbnails. If no photos
are added, the card shows the main photo without a gallery.

## Change contacts and legal details

Phone numbers, the address, opening hours and bank details are edited in one place —
**Настройки сайта** (Site settings; it is a single record, not a list).

1. **Настройки сайта** (Site settings) → a form with these sections opens:
   - **Контакты** (Contacts) — company name, phone numbers (sales / production /
     accounting), contact persons, e-mail.
   - **Адрес и режим** (Address and hours) — address, opening hours, the Yandex.Maps query.
   - **Реквизиты** (Legal details) — INN, KPP, OGRN, bank account, bank and so on.
   - **Уведомления и аналитика** (Notifications and analytics) — see below and
     [Notification channels](enable-notification-channels.md).
2. Make the changes → **Сохранить** (Save).

!!! tip "Phone numbers are entered once"
    A phone number is entered in a display-friendly form (`+7 495 000-00-00`).
    The clickable `tel:` link is assembled from it automatically — there is no
    need to set it separately.

## Upload certificates

Certificates are simply an image gallery on the "About" page.

1. **Сертификаты** (Certificates) → **Добавить сертификат** (Add certificate).
2. Fill in **Title**, **Image** (a scan or photo), **Order**,
   **Is active** (show or hide).
3. **Сохранить** (Save).

The order and visibility can be changed right in the certificate list, without opening
each one. If there are no active certificates, the section is hidden from the site entirely.

## Leads from the site

The **Заявки** (Leads) section holds the submissions left through the site forms. The lead
fields are **read-only** (a lead cannot be forged or altered from the admin).

Only one attribute can be changed — **Статус** (status: `Новая` / `Обработана`, i.e. new /
processed). The lead list can be filtered by status and type.
