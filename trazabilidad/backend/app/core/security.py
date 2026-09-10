import re
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import jwt
from pwdlib import PasswordHash

from app.core.config import settings

# Inicializar el hasheador de contraseñas Argon2
password_hash_context = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hashear contraseña usando Argon2id."""
    return password_hash_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña en texto plano contra el hash."""
    try:
        return password_hash_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validar robustez de la contraseña según requisitos:
    - Mínimo 8 caracteres
    - Al menos 1 mayúscula
    - Al menos 1 minúscula
    - Al menos 1 número
    - Al menos 1 carácter especial (!@#$%^&*()_-+=.,)
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres."
    if not re.search(r"[A-Z]", password):
        return False, "La contraseña debe contener al menos una letra mayúscula."
    if not re.search(r"[a-z]", password):
        return False, "La contraseña debe contener al menos una letra minúscula."
    if not re.search(r"[0-9]", password):
        return False, "La contraseña debe contener al menos un número."
    if not re.search(r"[!@#$%^&*()_\-+=\.,]", password):
        return False, "La contraseña debe contener al menos un carácter especial (!@#$%^&*()_-+=.,)."
    return True, ""


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crear token de acceso JWT."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"iat": now, "exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decodificar y validar token de acceso JWT."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


def generate_secure_raw_token() -> str:
    """Generar una cadena de token criptográficamente segura."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Generar hash SHA-256 de un token para guardado seguro en base de datos."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
