import os
import uuid
from werkzeug.utils import secure_filename
from backend.config import Config

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

def is_allowed_image(file_storage) -> tuple[bool, str]:
    """Validate image file MIME type, extension, and non-empty content."""
    if not file_storage or not file_storage.filename:
        return False, "No file uploaded."
    
    filename = file_storage.filename
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Disallowed file extension '{ext}'. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check MIME type
    mimetype = file_storage.mimetype.lower() if hasattr(file_storage, 'mimetype') else ''
    if mimetype and mimetype not in ALLOWED_MIME_TYPES:
        return False, f"Disallowed MIME type '{mimetype}'. Only valid images are allowed."

    return True, ""

def save_crop_image(file_storage) -> str:
    """
    Save uploaded crop image with a secure UUID-generated filename.
    Returns the relative URL path to access the image.
    """
    is_valid, err_msg = is_allowed_image(file_storage)
    if not is_valid:
        raise ValueError(err_msg)

    # Ensure uploads directory exists
    crops_upload_dir = os.path.join(Config.UPLOAD_FOLDER, "crops")
    os.makedirs(crops_upload_dir, exist_ok=True)

    # Generate safe randomized filename (never trust user input filename)
    ext = os.path.splitext(secure_filename(file_storage.filename))[1].lower()
    if not ext or ext not in ALLOWED_EXTENSIONS:
        ext = ".jpg"
    
    safe_name = f"crop_{uuid.uuid4().hex}{ext}"
    dest_path = os.path.join(crops_upload_dir, safe_name)

    file_storage.save(dest_path)
    return f"/uploads/crops/{safe_name}"
