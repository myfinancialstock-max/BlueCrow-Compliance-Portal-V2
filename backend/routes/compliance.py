"""
Rotas da área: Compliance
"""

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.import_service import import_excel, import_pdf

router = APIRouter()


@router.get("/")
def list_records(db: Session = Depends(get_db)):
    # TODO: devolver registos da tabela compliance
    return {"area": "Compliance", "records": []}


@router.post("/import/excel")
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # TODO: mapear colunas para ComplianceRecord após definir os headers
    return await import_excel(file, db)


@router.post("/import/pdf")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # TODO: mapear texto extraído para ComplianceRecord após definir os headers
    return await import_pdf(file, db)


@router.post("/")
def create_record(db: Session = Depends(get_db)):
    # TODO: receber body com os campos e inserir na DB
    return {"message": "Endpoint de criação manual — aguarda definição dos headers."}


@router.put("/{record_id}")
def update_record(record_id: int, db: Session = Depends(get_db)):
    # TODO: actualizar registo por ID
    return {"message": f"Actualizar registo {record_id} — aguarda definição dos headers."}


@router.delete("/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    # TODO: eliminar registo por ID
    return {"message": f"Eliminar registo {record_id}."}
