import uuid

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.config import Base


class Categoria(Base):
    """Entidad que representa una categoría de items de la biblioteca."""

    __tablename__ = "categorias"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(String(500), nullable=True)
    id_usuario_creacion = Column(UUID(as_uuid=True), nullable=False)
    id_usuario_edicion = Column(UUID(as_uuid=True), nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    libros = relationship("Libro", back_populates="categoria")
    revistas = relationship("Revista", back_populates="categoria")
    periodicos = relationship("Periodico", back_populates="categoria")

    def __repr__(self):
        return f"<Categoria(id={self.id}, nombre='{self.nombre}')>"
