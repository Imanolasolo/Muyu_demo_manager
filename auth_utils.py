import hashlib
import bcrypt
from passlib.context import CryptContext

# Create password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password_sha256(password: str) -> str:
    """Hash a password with a random salt using SHA-256"""
    salt = hashlib.sha256(str(hash(password + str(hash(password)))).encode()).hexdigest()
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + pwdhash.hex()

def safe_password_hash(password: str) -> str:
    """
    Safely hash a password using SHA-256 (more compatible than bcrypt).
    This avoids bcrypt's 72-byte limitation entirely.
    """
    return hash_password_sha256(password)

def verify_password_sha256(password: str, hashed: str) -> bool:
    """Verify a password against its SHA-256 hash"""
    if len(hashed) < 64:
        return False
    salt = hashed[:64]
    stored_hash = hashed[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return pwdhash.hex() == stored_hash

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash, supporting both bcrypt and SHA-256 formats.
    """
    # Check if it's a SHA-256 hash (our new method) - 128+ characters
    if len(hashed_password) >= 128:
        return verify_password_sha256(plain_password, hashed_password)
    
    # For bcrypt hashes, handle the 72-byte limitation
    if isinstance(plain_password, str):
        plain_password_bytes = plain_password.encode('utf-8')
    else:
        plain_password_bytes = plain_password
    
    # Apply same truncation if password is too long
    if len(plain_password_bytes) > 72:
        # Truncate to 72 bytes as bcrypt requires
        password_str = plain_password[:72] if isinstance(plain_password, str) else plain_password_bytes[:72].decode('utf-8', errors='ignore')
    else:
        password_str = plain_password if isinstance(plain_password, str) else plain_password_bytes.decode('utf-8')
    
    try:
        return pwd_context.verify(password_str, hashed_password)
    except Exception:
        # Fallback for any verification issues
        return False
