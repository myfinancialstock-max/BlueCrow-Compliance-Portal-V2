"""
Modelos da área: Controlo Interno

As colunas serão definidas quando os headers forem fornecidos.
"""

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


# TODO: adicionar colunas após receber os headers
class ControloInternoRecord(Base):
    __tablename__ = "controlo_interno"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
