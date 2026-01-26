# main/signals.py
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.db.models import Q
from django.core.files.storage import default_storage
import re

from .models import SiteAsset


# -------- utility -------------------------------------------------------------
def _safe_delete_field_file(instance, field_name: str):
    """
    Safely delete a FileField/ImageField using Django's storage.
    Deletes only if no other row on the SAME model references the same file.
    Works with any storage backend (local, S3, Cloudinary).
    """
    f = getattr(instance, field_name, None)
    if not f or not getattr(f, "name", ""):
        return

    model = type(instance)
    # Another instance still points to this file? Keep it.
    if model.objects.filter(~Q(pk=getattr(instance, "pk", None)), **{field_name: f.name}).exists():
        return

    try:
        if default_storage.exists(f.name):
            default_storage.delete(f.name)
    except Exception:
        # Never break saves/deletes because of storage errors
        pass

# -------- SiteAsset: update/delete -------------------------------------------
@receiver(pre_save, sender=SiteAsset)
def siteasset_cleanup_on_update(sender, instance: SiteAsset, **kwargs):
    """Delete old file when a SiteAsset's image is replaced."""
    if not instance.pk:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    old_file = getattr(old, "image", None)
    new_file = getattr(instance, "image", None)
    old_name = getattr(old_file, "name", None)
    new_name = getattr(new_file, "name", None)
    if old_name and old_name != new_name:
        _safe_delete_field_file(old, "image")


@receiver(post_delete, sender=SiteAsset)
def siteasset_cleanup_on_delete(sender, instance: SiteAsset, **kwargs):
    """Delete the file when a SiteAsset is deleted."""
    _safe_delete_field_file(instance, "image")
