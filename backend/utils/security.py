import re
import datetime
import bcrypt
import jwt
from backend.config import Config

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?[0-9]{10,15}$")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt with automatic salt generation."""
    if not password or not isinstance(password, str):
        raise ValueError("Password must be a non-empty string.")
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    if not password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def generate_token(user_id: str, role: str, email: str) -> str:
    """Generate a signed JWT token containing user identity and role."""
    payload = {
        "sub": str(user_id),
        "role": role.lower(),
        "email": email.lower(),
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=Config.JWT_ACCESS_TOKEN_EXPIRES_HOURS)
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

def decode_token(token: str) -> dict:
    """Verify and decode a JWT token. Returns payload or None if invalid/expired."""
    if not token or not isinstance(token, str):
        return None
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def validate_email(email: str) -> bool:
    """Check if email matches valid RFC pattern."""
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))

def validate_phone(phone: str) -> bool:
    """Check if phone number is a valid 10-15 digit string."""
    if not phone or not isinstance(phone, str):
        return False
    clean_phone = phone.replace(" ", "").replace("-", "")
    return bool(PHONE_REGEX.match(clean_phone))

def sanitize_string(val: str, max_length: int = 250) -> str:
    """Sanitize string inputs to prevent NoSQL operator injection and XSS."""
    if not isinstance(val, str):
        return ""
    # Strip dangerous leading MongoDB query operators
    cleaned = val.strip()
    if cleaned.startswith("$"):
        cleaned = cleaned.lstrip("$")
    return cleaned[:max_length]

def sanitize_user(user_doc: dict) -> dict:
    """Remove password and sensitive hashes before returning user dictionary."""
    if not user_doc:
        return None
    cleaned = dict(user_doc)
    cleaned.pop("password", None)
    cleaned.pop("password_hash", None)
    if "_id" in cleaned:
        cleaned["id"] = str(cleaned["_id"])
        cleaned.pop("_id", None)
    return cleaned
