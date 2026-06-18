"""
Data migration: move the legacy SiteCopy / SiteAsset key-value rows into the
single SiteContent settings object. SiteAsset image files are imported into the
Wagtail image library so they gain renditions. Non-destructive: the old
SiteCopy / SiteAsset rows are left in place (removed in a later cleanup).
"""
import hashlib
import io
import os

from django.core.files.base import ContentFile
from django.db import migrations

COPY_FIELDS = [
    "about_title", "about_lead", "about_intro_headline",
    "about_intro_body", "about_quote", "skills_title", "skills_lead",
]
IMAGE_KEYS = ["about_profile", "home_profile"]


def _import_to_wagtail_image(asset):
    # Use the real Wagtail image model: its file field's upload_to needs
    # instance.get_upload_to(), which the historical migration model lacks.
    from wagtail.images import get_image_model
    from wagtail.models import Collection

    Image = get_image_model()

    try:
        asset.image.open("rb")
        data = asset.image.read()
        asset.image.close()
    except Exception:
        return None

    try:
        from PIL import Image as PImage
        width, height = PImage.open(io.BytesIO(data)).size
    except Exception:
        width, height = 1, 1

    img = Image(
        title=asset.alt_text or asset.key,
        collection=Collection.get_first_root_node(),
    )
    # Assign the file first (Wagtail resets dimension/size fields on file set),
    # then populate metadata before the final save.
    img.file.save(os.path.basename(asset.image.name), ContentFile(data), save=False)
    img.width = width
    img.height = height
    img.file_size = len(data)
    img.file_hash = hashlib.sha1(data).hexdigest()
    img.save()
    return img


def forwards(apps, schema_editor):
    SiteCopy = apps.get_model("main", "SiteCopy")
    SiteAsset = apps.get_model("main", "SiteAsset")
    SiteContent = apps.get_model("main", "SiteContent")

    # Latest active copy per key (most recent wins).
    copy = {}
    for row in SiteCopy.objects.filter(active=True).order_by("updated_at", "id"):
        copy[row.key] = row.text

    content = SiteContent.objects.first() or SiteContent()
    for field in COPY_FIELDS:
        if copy.get(field):
            setattr(content, field, copy[field])

    # Latest active asset per relevant key, imported into Wagtail images.
    latest_asset = {}
    for asset in SiteAsset.objects.filter(active=True, key__in=IMAGE_KEYS).order_by("updated_at", "id"):
        latest_asset[asset.key] = asset
    for key, asset in latest_asset.items():
        img = _import_to_wagtail_image(asset)
        if img is not None:
            # Assign by id: the real Image instance isn't the historical FK's class.
            setattr(content, f"{key}_id", img.pk)

    content.save()


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0016_sitecontent"),
        ("wagtailimages", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
