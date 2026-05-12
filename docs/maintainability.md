# Maintainability Notes

Honest notes on the current state of the codebase — things to keep in mind when adding features or doing cleanup.

---

## Known Issues / Tech Debt

### Duplicate block definitions
`cms/blocks.py` has a comment referencing a "legacy" duplicate. If there are two copies of the block registry (or an old import), consolidate them. Any block defined twice will cause confusion when adding new blocks.

### Legacy templates in `main/`
Several templates exist that appear to be from before Wagtail was added:
- `portfolio.html` / `portfolio_detail.html` — portfolio listing/detail that's now handled by `PortfolioIndexPage` / `PortfolioProjectPage`
- `services.html` — skills/services page that may be unused

Before deleting these, confirm no URL route points to them (search `urls.py` and views for the template names).

### Two Markdown libraries in requirements
Both `Markdown` and `markdown2` are installed. The `|markdownify` template tag uses `markdown2`. The `Markdown` package and `django-markdownx` may be unused — check imports before removing.

### `WAGTAIL_SITE_NAME = "test"` in settings
Still set to `"test"`. Should be updated to the real site name.

### `WAGTAILADMIN_BASE_URL = "http://localhost:8000"`
Should point to the production domain. Affects email links sent from Wagtail (page revision notifications, etc.).

### Single-settings file
There is one `settings.py` with no dev/prod split. Currently `DEBUG` is controlled by an env var (`DJANGO_DEBUG`), which works but means you have to be careful about which settings apply only in dev. If the project grows, consider splitting into `settings/base.py`, `settings/dev.py`, `settings/prod.py`.

---

## Patterns to Follow

### Adding a new CV section (Education, Experience, etc.)
1. Add a model in `main/models.py` extending `Timestamped`
2. Register it in `main/admin.py`
3. Create and run a migration
4. Add it to the relevant view context in `main/views.py`
5. Render it in the corresponding template

### Adding a new StreamField block
1. Define the block class in `cms/blocks.py`
2. Add it to `BlogPage.body` and/or `PortfolioProjectPage.body` stream definitions
3. Create a block template in `cms/templates/cms/blocks/`
4. Run `makemigrations` + `migrate` (StreamField schema changes need migrations)

### Adding a new Wagtail page type
1. Define the page model in `cms/models.py` (subclass `Page` or `RoutablePageMixin`)
2. Set `parent_page_types` and `subpage_types` to control the page tree
3. Create a template at `cms/templates/cms/<snake_case_model_name>.html`
4. Run migrations

### SiteCopy / SiteAsset
Use these for any text or image that needs to be editable without a code deploy. Access via `SiteCopy.objects.filter(key="your_key", active=True).first()` in views. Only one active row per key is enforced at the model level.

---

## Upgrade Notes

### Django 5.x → 6.x (future)
No immediate concerns. Watch for deprecations in `django.utils.encoding`, `request.META` patterns, and anything using `contrib.postgres` features.

### Wagtail 6.x → 7.x (future)
Check Wagtail changelog for StreamField API changes — block value access patterns occasionally change between major versions. Also check `RoutablePageMixin` method signatures.

### Pillow
Pin upgrades manually and test image upload/validation after each bump — the `Image.open()` / `verify()` API occasionally has behavior changes.

---

## Testing

Tests live in `main/tests.py` and `cms/tests.py`. Run with:

```bash
python manage.py test
```

Current coverage is minimal. Priority areas to add tests:
- `|markdownify` and `|bootstrapify` template filters (already have clear inputs/outputs)
- `SiteAsset` signal (file cleanup on update/delete)
- `cms/signals.py` document upload validation
- View smoke tests (each URL returns 200 with expected context keys)
