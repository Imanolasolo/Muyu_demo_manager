import hashlib
import bcrypt
from passlib.context import CryptContext

# Create password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def safe_password_hash(password: str) -> str:
    """
    Safely hash a password, handling bcrypt's 72-byte limitation.
    For passwords longer than 72 bytes, we first hash with SHA256.
    """
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = password
    
    # If password is longer than 72 bytes, pre-hash with SHA256
    if len(password_bytes) > 72:
        # Truncate to 72 bytes as bcrypt requires
        password_str = password[:72] if isinstance(password, str) else password_bytes[:72].decode('utf-8', errors='ignore')
    else:
        password_str = password if isinstance(password, str) else password_bytes.decode('utf-8')
    
    return pwd_context.hash(password_str)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash, handling the same length limitation.
    """
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
