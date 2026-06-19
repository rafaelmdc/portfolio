import json

from django.db import migrations

# Default homepage layout, preserving the previous fixed order. Research is off
# by default now (it is a toggleable section rather than auto-detected).
DEFAULT_SECTIONS = ["about", "skills", "timeline", "work", "contact"]


def seed_sections(apps, schema_editor):
    HomePage = apps.get_model("cms", "HomePage")
    for hp in HomePage.objects.all():
        if hp.sections:  # already configured — leave it alone
            continue
        raw = [{"type": t, "value": {"title": ""}} for t in DEFAULT_SECTIONS]
        hp.sections = json.dumps(raw)
        hp.save(update_fields=["sections"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0011_homepage_sections"),
    ]

    operations = [
        migrations.RunPython(seed_sections, noop),
    ]
