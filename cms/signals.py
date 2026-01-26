import os
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.dispatch import receiver

from wagtail.documents.models import Document

# whitelist of allowed document extensions (lowercase)
ALLOWED_DOC_EXT = {".pdf", ".docx", ".txt", ".xlsx", ".pptx"}
MAX_DOC_UPLOAD_MB = 10


@receiver(pre_save, sender=Document)
def validate_wagtail_document(sender, instance, **kwargs):
    """Validate uploaded documents: extension whitelist + max size."""
    if not getattr(instance, "file", None):
        return

    name = getattr(instance.file, "name", "")
    ext = os.path.splitext(name)[1].lower()
    if ext and ext not in ALLOWED_DOC_EXT:
        raise ValidationError(f"Files with extension '{ext}' are not allowed.")

    try:
        size = instance.file.size
    except Exception:
        size = None
    if size and size > MAX_DOC_UPLOAD_MB * 1024 * 1024:
        raise ValidationError(f"Document too large (max {MAX_DOC_UPLOAD_MB} MB).")
