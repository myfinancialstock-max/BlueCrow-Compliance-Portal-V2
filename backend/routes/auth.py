from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.auth_service import (
    authenticate_user,
    create_access_token,
    generate_qr_code_base64,
    generate_totp_secret,
    get_totp_uri,
    verify_totp,
)

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")


# ---------------------------------------------------------------------------
# Schemas de entrada
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    username: str
    password: str


class TOTPRequest(BaseModel):
    username: str
    code: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """Página de login."""
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """
    1ª etapa: valida username + password.
    Se o utilizador tiver 2FA activo, devolve indicação para pedir o código TOTP.
    """
    user = authenticate_user(db, body.username, body.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas.")

    if user.totp_enabled:
        # Frontend redireciona para o ecrã de 2FA
        return {"requires_2fa": True, "username": user.username}

    # Sem 2FA: emite token directamente
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/verify-2fa")
def verify_2fa(body: TOTPRequest, db: Session = Depends(get_db)):
    """
    2ª etapa: valida o código TOTP de 6 dígitos.
    """
    from backend.models.user import User
    user = db.query(User).filter(User.username == body.username).first()

    if not user or not user.totp_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Utilizador inválido.")

    if not verify_totp(user.totp_secret, body.code):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Código 2FA inválido.")

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/setup-2fa")
def setup_2fa(username: str, db: Session = Depends(get_db)):
    """
    Gera o segredo TOTP e o QR Code para o utilizador configurar o 2FA.
    Chamado uma única vez no primeiro login ou em /perfil.
    """
    from backend.models.user import User
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="Utilizador não encontrado.")

    secret = generate_totp_secret()
    uri = get_totp_uri(secret, username)
    qr_base64 = generate_qr_code_base64(uri)

    # Guarda o segredo (ainda não activo até o utilizador confirmar com um código válido)
    user.totp_secret = secret
    db.commit()

    return {"qr_code": qr_base64, "secret": secret}


@router.post("/logout")
def logout():
    """
    O JWT é stateless — o logout é feito no cliente apagando o token.
    Este endpoint existe para uniformidade e futura implementação de blacklist.
    """
    return {"message": "Sessão terminada. Apague o token no cliente."}
