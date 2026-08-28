import enum
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class PerfilEnum(str, enum.Enum):
    PROFESSOR = "Professor"
    ALUNO = "Aluno"

class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    foto: Mapped[str | None] = mapped_column(String(500), nullable=True)
    perfil: Mapped[PerfilEnum] = mapped_column(Enum(PerfilEnum), nullable=False)
    provedor: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_id: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)