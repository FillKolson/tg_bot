from passlib.context import CryptContext
import os

pwd_ctx = CryptContext(schemes=["argon2"], deprecated="auto")
PEPPER = os.getenv("PASSWORD_PEPPER", "")


def hash_password(password: str) -> str:
    """Hash a password with optional pepper."""
    return pwd_ctx.hash(password + PEPPER)


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against given hash."""
    return pwd_ctx.verify(password + PEPPER, hashed)


# Common / primitive passwords blacklist
COMMON_PASSWORDS = {
    "123456", "password", "123456789", "12345678", "12345",
    "111111", "1234567", "qwerty", "abc123", "password1",
    "iloveyou", "admin", "welcome", "monkey", "login",
    "123123", "1234", "passw0rd", "dragon", "sunshine",
    "princess", "qwerty123",
}


def is_common_password(pw: str) -> bool:
    s = pw.strip().lower()
    return s in COMMON_PASSWORDS or len(s) < 4
