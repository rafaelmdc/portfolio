# main/signals.py
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.db.models import Q
from django.core.files.storage import default_storage
import re

from .models import PortfolioItem, SiteAsset


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


# Pattern to find CKEditor-uploaded images in saved HTML.
# Matches src="/media/ckeditor/...." OR src="ckeditor/...."
CKE_IMG_RE = re.compile(r'src="(?:/media/)?ckeditor/([^"]+)"', re.IGNORECASE)


def _delete_ck_paths(paths):
    for rel in paths:
        path = f"ckeditor/{rel}"
        try:
            if default_storage.exists(path):
                default_storage.delete(path)
        except Exception:
            pass


# -------- PortfolioItem: update ----------------------------------------------
@receiver(pre_save, sender=PortfolioItem)
def portfolioitem_cleanup_on_update(sender, instance: PortfolioItem, **kwargs):
    """
    Before saving a PortfolioItem:
      - If image/hero/lightbox_image are replaced, delete the old files.
      - If CKEditor images were removed from body_html, delete those files.
    """
    if not instance.pk:
        return

    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    # Delete replaced file fields
    for field in ["image", "hero", "lightbox_image"]:
        old_file = getattr(old, field, None)
        new_file = getattr(instance, field, None)
        old_name = getattr(old_file, "name", None)
        new_name = getattr(new_file, "name", None)
        if old_name and old_name != new_name:
            _safe_delete_field_file(old, field)

    # CKEditor: delete files that were removed from body_html
    old_imgs = set(CKE_IMG_RE.findall(old.body_html or ""))
    new_imgs = set(CKE_IMG_RE.findall(instance.body_html or ""))
    removed = old_imgs - new_imgs
    _delete_ck_paths(removed)


# -------- PortfolioItem: delete ----------------------------------------------
@receiver(post_delete, sender=PortfolioItem)
def portfolioitem_cleanup_on_delete(sender, instance: PortfolioItem, **kwargs):
    """
    When a PortfolioItem is deleted, remove its image files and any CKEditor uploads
    referenced in its body_html.
    """
    for field in ["image", "hero", "lightbox_image"]:
        _safe_delete_field_file(instance, field)

    ck_imgs = set(CKE_IMG_RE.findall(instance.body_html or ""))
    _delete_ck_paths(ck_imgs)


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
