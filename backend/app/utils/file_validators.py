"""
Server-side file validation for PDF uploads.
All validations run before any file is written to disk.
"""
import os
from flask import current_app


ALLOWED_EXTENSIONS = {"pdf"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def allowed_file(filename: str) -> bool:
    """Check that the filename has a .pdf extension."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def validate_pdf_upload(file_storage, required: bool = True) -> tuple[bool, str]:
    """
    Validate a werkzeug FileStorage object for PDF upload.

    Returns:
        (True, "") on success
        (False, "error message") on failure
    """
    if file_storage is None or not file_storage.filename or file_storage.filename == "":
        if not required:
            return True, ""
        return False, "No PDF file provided"

    filename = file_storage.filename
    if not allowed_file(filename):
        return False, "Only PDF files are allowed (must have .pdf extension)"

    # Read a small header to verify it's actually a PDF
    header = file_storage.read(5)
    file_storage.seek(0)  # reset stream for later saving
    if header != b"%PDF-":
        return False, "File does not appear to be a valid PDF (bad magic bytes)"

    # Check size — read stream length without loading it all into memory
    file_storage.seek(0, os.SEEK_END)
    file_size = file_storage.tell()
    file_storage.seek(0)

    if file_size == 0:
        return False, "File is empty"

    max_size = current_app.config.get("MAX_CONTENT_LENGTH", MAX_FILE_SIZE)
    if file_size > max_size:
        max_mb = max_size // (1024 * 1024)
        return False, f"File too large — maximum allowed size is {max_mb} MB"

    return True, ""


def safe_filename(filename: str) -> str:
    """Sanitize filename for safe storage on disk."""
    from werkzeug.utils import secure_filename
    return secure_filename(filename)


ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB


def validate_image_upload(file_storage) -> tuple[bool, str]:
    """
    Validate a werkzeug FileStorage object for an optional cover image upload.

    Returns:
        (True, "") on success
        (False, "error message") on failure
    """
    if file_storage is None or not file_storage.filename:
        return True, ""  # Optional, so None is valid

    filename = file_storage.filename
    ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return False, f"Only image files ({', '.join(ALLOWED_IMAGE_EXTENSIONS)}) are allowed for cover image"

    file_storage.seek(0, os.SEEK_END)
    file_size = file_storage.tell()
    file_storage.seek(0)

    if file_size == 0:
        return False, "Cover image file is empty"

    if file_size > MAX_IMAGE_SIZE:
        return False, "Cover image file is too large (maximum allowed size is 10 MB)"

    return True, ""
