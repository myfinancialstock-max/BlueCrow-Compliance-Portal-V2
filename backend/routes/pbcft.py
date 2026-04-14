"""
Rotas da área: PBC/FT
"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.pbcft import PBCFTRecord

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class PBCFTCreate(BaseModel):
    nome: str
    investimento: float
    fundos: List[str] = []
    perfil_risco: str           # baixo | medio | alto
    is_pep: bool = False
    doc_identificacao: bool = False
    doc_morada: bool = False
    doc_rendimentos: bool = False
    data_entrada_compliance: Optional[date] = None
    data_decisao: Optional[date] = None
    tipo_decisao: Optional[str] = None   # info_solicitada | aprovado


class PBCFTUpdate(PBCFTCreate):
    pass


# ---------------------------------------------------------------------------
# Página HTML
# ---------------------------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
def pbcft_page(request: Request):
    return templates.TemplateResponse("pbcft/index.html", {"request": request})


# ---------------------------------------------------------------------------
# API JSON
# ---------------------------------------------------------------------------

def _serialize(r: PBCFTRecord) -> dict:
    return {
        "id": r.id,
        "nome": r.nome,
        "investimento": float(r.investimento),
        "fundos": r.fundos or [],
        "perfil_risco": r.perfil_risco,
        "is_pep": r.is_pep,
        "doc_identificacao": r.doc_identificacao,
        "doc_morada": r.doc_morada,
        "doc_rendimentos": r.doc_rendimentos,
        "data_entrada_compliance": r.data_entrada_compliance.isoformat() if r.data_entrada_compliance else None,
        "data_decisao": r.data_decisao.isoformat() if r.data_decisao else None,
        "tipo_decisao": r.tipo_decisao,
    }


@router.get("/records")
def list_records(db: Session = Depends(get_db)):
    records = db.query(PBCFTRecord).order_by(PBCFTRecord.created_at.desc()).all()
    return [_serialize(r) for r in records]


@router.post("/", status_code=201)
def create_record(body: PBCFTCreate, db: Session = Depends(get_db)):
    record = PBCFTRecord(**body.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return _serialize(record)


@router.put("/{record_id}")
def update_record(record_id: int, body: PBCFTUpdate, db: Session = Depends(get_db)):
    record = db.query(PBCFTRecord).filter(PBCFTRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Registo não encontrado.")
    for field, value in body.model_dump().items():
        setattr(record, field, value)
    db.commit()
    return _serialize(record)


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(PBCFTRecord).filter(PBCFTRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Registo não encontrado.")
    db.delete(record)
    db.commit()
