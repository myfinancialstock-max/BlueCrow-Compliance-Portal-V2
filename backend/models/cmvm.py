"""
Modelos da área: CMVM (Comissão do Mercado de Valores Mobiliários)

As colunas serão definidas quando os headers forem fornecidos.
"""

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


# TODO: adicionar colunas após receber os headers
class CMVMRecord(Base):
    __tablename__ = "cmvm"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
