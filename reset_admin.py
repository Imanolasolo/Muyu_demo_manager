#!/usr/bin/env python3
"""
Script to reset the admin user password with the new hashing format
Run this if you need to reset the admin password after the migration
"""

import sqlite3
import hashlib
import secrets
import os

DB_NAME = "db/muyudemo.db"

def hash_password(password: str) -> str:
    """Hash a password with a random salt using SHA-256"""
    salt = secrets.token_hex(32)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + pwdhash.hex()

def reset_admin_password():
    """Reset admin password to 'admin123' with new hash format"""
    if not os.path.exists(DB_NAME):
        print(f"❌ Database not found at {DB_NAME}")
        return
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    admin_email = "admin@muyu.com"
    new_password = "admin123"
    
    # Check if admin user exists
    c.execute("SELECT * FROM usuarios WHERE email = ?", (admin_email,))
    user = c.fetchone()
    
    if user:
        # Update password with new hash
        new_hash = hash_password(new_password)
        c.execute("UPDATE usuarios SET password = ? WHERE email = ?", (new_hash, admin_email))
        conn.commit()
        print("✅ Admin password reset successfully!")
        print(f"   Email: {admin_email}")
        print(f"   Password: {new_password}")
    else:
        # Create admin user if it doesn't exist
        admin_nombre = "Admin"
        admin_rol = "admin"
        hashed = hash_password(new_password)
        c.execute(
            "INSERT INTO usuarios (nombre, email, password, rol) VALUES (?, ?, ?, ?)",
            (admin_nombre, admin_email, hashed, admin_rol)
        )
        conn.commit()
        print("✅ Admin user created successfully!")
        print(f"   Email: {admin_email}")
        print(f"   Password: {new_password}")
    
    conn.close()

if __name__ == "__main__":
    reset_admin_password()