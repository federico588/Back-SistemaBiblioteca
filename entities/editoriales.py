import uuid

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.config import Base


class Editorial(Base):
    """Entidad que representa una editorial."""

    __tablename__ = "editoriales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nombre = Column(String(100), nullable=False)
    direccion = Column(String(255), nullable=True)
    telefono = Column(String(20), nullable=True)
    id_usuario_creacion = Column(UUID(as_uuid=True), nullable=False)
    id_usuario_edicion = Column(UUID(as_uuid=True), nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    libros = relationship("Libro", back_populates="editorial")
    revistas = relationship("Revista", back_populates="editorial")
    periodicos = relationship("Periodico", back_populates="editorial")

    def __repr__(self):
        return f"<Editorial(id={self.id}, nombre='{self.nombre}')>"
