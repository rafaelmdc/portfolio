# Maintainability Notes

Honest notes on the current state of the codebase — things to keep in mind when adding features or doing cleanup.

---

## Open Items

### Single-settings file
There is one `settings.py` with no dev/prod split. Currently `DEBUG` is controlled by an env var (`DJANGO_DEBUG`), which works fine for a small project. If the project grows, consider splitting into `settings/base.py`, `settings/dev.py`, `settings/prod.py`.

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
2. Add it to `BlogBodyStreamBlock` and/or `PortfolioProjectPage.body` stream definitions in `cms/models.py`
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
