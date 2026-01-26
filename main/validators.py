from PIL import Image, UnidentifiedImageError
from django.core.exceptions import ValidationError

# maximum upload size in megabytes
MAX_IMAGE_UPLOAD_MB = 10


def validate_image_file(file):
    """Validate uploaded images:
    - enforce a maximum file size
    - check provided content_type if available
    - verify actual image bytes with Pillow
    Raises ``ValidationError`` on failure.
    """
    if not file:
        return

    # size check
    try:
        size = file.size
    except Exception:
        size = None
    if size and size > MAX_IMAGE_UPLOAD_MB * 1024 * 1024:
        raise ValidationError(f"Image file too large (max {MAX_IMAGE_UPLOAD_MB} MB).")

    # basic content-type hint check (some uploaders provide this)
    content_type = getattr(file, "content_type", "")
    if content_type and not content_type.startswith("image/"):
        raise ValidationError("Uploaded file does not appear to be an image.")

    # verify image can be opened by Pillow
    try:
        # Pillow can fail if file is a non-image with an image extension
        img = Image.open(file)
        img.verify()
    except UnidentifiedImageError:
        raise ValidationError("Uploaded file is not a valid image.")
    except Exception:
        # Any other errors are treated as invalid image
        raise ValidationError("Uploaded file could not be validated as an image.")
