from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.config import settings
from backend.routes import (
    auth,
    compliance,
    controlo_interno,
    pbcft,
    cmvm,
    pareceres,
    rgpd,
)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    # Docs disponíveis em /docs (Swagger) e /redoc
)

# Ficheiros estáticos (CSS, JS, imagens)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Templates Jinja2
templates = Jinja2Templates(directory="frontend/templates")

# Rotas por área
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
app.include_router(compliance.router, prefix="/compliance", tags=["Compliance"])
app.include_router(controlo_interno.router, prefix="/controlo-interno", tags=["Controlo Interno"])
app.include_router(pbcft.router, prefix="/pbcft", tags=["PBC/FT"])
app.include_router(cmvm.router, prefix="/cmvm", tags=["CMVM"])
app.include_router(pareceres.router, prefix="/pareceres", tags=["Pareceres"])
app.include_router(rgpd.router, prefix="/rgpd", tags=["RGPD"])


@app.get("/", include_in_schema=False)
def root():
    """Redireciona para a página de login."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/auth/login")
