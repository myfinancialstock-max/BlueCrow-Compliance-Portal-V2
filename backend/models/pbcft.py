"""
Modelos da área: PBC/FT (Prevenção de Branqueamento de Capitais / Financiamento do Terrorismo)
"""

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Integer, JSON, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class PBCFTRecord(Base):
    __tablename__ = "pbcft"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Identificação e investimento
    nome: Mapped[str] = mapped_column(String(256), nullable=False)
    investimento: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    # Fundos — lista de nomes armazenada como JSON (ex: ["Fundo A", "Fundo B"])
    fundos: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # Perfil de risco: "baixo" | "medio" | "alto"
    perfil_risco: Mapped[str] = mapped_column(String(10), nullable=False)

    # PEP — Pessoa Politicamente Exposta
    is_pep: Mapped[bool] = mapped_column(Boolean, default=False)

    # Documentação recebida
    doc_identificacao: Mapped[bool] = mapped_column(Boolean, default=False)
    doc_morada: Mapped[bool] = mapped_column(Boolean, default=False)
    doc_rendimentos: Mapped[bool] = mapped_column(Boolean, default=False)

    # Datas de processo
    data_entrada_compliance: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_decisao: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Tipo de decisão: "info_solicitada" | "aprovado"
    tipo_decisao: Mapped[str | None] = mapped_column(String(32), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
