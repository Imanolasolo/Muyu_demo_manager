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
        password = password.encode('utf-8')
    
    # If password is longer than 72 bytes, pre-hash with SHA256
    if len(password) > 72:
        password = hashlib.sha256(password).hexdigest().encode('utf-8')
    
    return pwd_context.hash(password.decode('utf-8'))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash, handling the same length limitation.
    """
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    
    # Apply same pre-hashing if password is too long
    if len(plain_password) > 72:
        plain_password = hashlib.sha256(plain_password).hexdigest().encode('utf-8')
    
    return pwd_context.verify(plain_password.decode('utf-8'), hashed_password)
