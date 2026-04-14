"""
Serviço de importação de dados.

Suporta:
- Excel (.xlsx, .xls)  → via openpyxl / pandas
- PDF                  → via pdfplumber

Uso futuro: cada área (Compliance, RGPD, etc.) chamará este serviço
passando o ficheiro e o modelo SQLAlchemy destino.
"""

import pandas as pd
import pdfplumber
from fastapi import UploadFile
from sqlalchemy.orm import Session


async def import_excel(file: UploadFile, db: Session) -> dict:
    """
    Lê um ficheiro Excel e devolve os dados como lista de dicionários.
    A lógica de mapeamento para cada modelo será adicionada por área.
    """
    contents = await file.read()

    # pandas lê directamente de bytes
    df = pd.read_excel(contents, engine="openpyxl")

    # Remove linhas completamente vazias
    df.dropna(how="all", inplace=True)

    rows = df.to_dict(orient="records")

    # TODO: mapear `rows` para o modelo SQLAlchemy correcto e inserir na DB

    return {"imported": len(rows), "preview": rows[:5]}


async def import_pdf(file: UploadFile, db: Session) -> dict:
    """
    Extrai texto de um PDF página a página.
    A lógica de parsing estruturado será adicionada por área.
    """
    contents = await file.read()

    pages_text = []
    with pdfplumber.open(contents) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text.strip())

    # TODO: parsear `pages_text` e mapear para o modelo correcto

    return {"pages": len(pages_text), "preview": pages_text[:2]}
