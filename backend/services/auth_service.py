from datetime import datetime, timedelta, timezone

import pyotp
import qrcode
from io import BytesIO
import base64

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.config import settings
from backend.models.user import User


# Contexto bcrypt para hash de palavras-passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------------
# Palavra-passe
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------

def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None


# ---------------------------------------------------------------------------
# 2FA — TOTP (compatível com Google Authenticator / Authy)
# ---------------------------------------------------------------------------

def generate_totp_secret() -> str:
    """Gera um segredo TOTP único para o utilizador."""
    return pyotp.random_base32()


def get_totp_uri(secret: str, username: str) -> str:
    """URI usado para gerar o QR Code."""
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=username,
        issuer_name=settings.app_name,
    )


def generate_qr_code_base64(totp_uri: str) -> str:
    """Gera o QR Code em base64 para enviar ao frontend."""
    img = qrcode.make(totp_uri)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


def verify_totp(secret: str, code: str) -> bool:
    """Valida o código de 6 dígitos introduzido pelo utilizador."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code)
