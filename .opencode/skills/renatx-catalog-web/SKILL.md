---
name: Renatx Bilingual Catalog & Web UI
description: Use this skill when adding or modifying commercial products, pricing, Stripe checkout flows, RustDesk status widgets, or bilingual Spanish/German (ES/DE) content in service-web and service-api.
---

# Renatx Bilingual Catalog & Web UI (`renatx-catalog-web`)

## 1. Bilingual Requirement (Spanish 🇪🇸 + German 🇩🇪)
All customer-facing text in `service-web/app/page.tsx` and `service-api/app/routers/billing.py` must be maintained in both **Spanish (`es`)** and **German (`de`)** to serve Franco Renato Palavecino's clients and students in Hamburg/Germany and the Spanish-speaking market.

## 2. Synchronizing Products & Pricing
When adding, renaming, or changing the price of a service or mentoring package, update both locations together:
1. **Backend Catalog (`service-api/app/routers/billing.py`):**
   - Update the `CATALOG` dictionary (`title_es`, `title_de`, `amount_eur`, `mode`).
2. **Frontend Catalog (`service-web/app/page.tsx`):**
   - Update `I18N.es.services` and `I18N.de.services` with matching `id`, `price`, `title`, `desc`, and `features`.

## 3. Rebuilding After Changes
Because `service-web` uses Next.js `output: "standalone"` inside a Podman container, any change to `service-web/` or `service-api/` requires running:
```bash
make up
```
Verify the result at `http://renatx.localhost:8080` and check `curl -s http://localhost:8080/api/billing/catalog`.
