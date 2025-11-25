import uuid

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.config import Base


class Autor(Base):
    """Entidad que representa un autor de libros, revistas o periódicos."""

    __tablename__ = "autores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nombre = Column(String(100), nullable=False)
    nacionalidad = Column(String(50), nullable=False)
    bibliografia = Column(String(500), nullable=True)
    id_usuario_creacion = Column(UUID(as_uuid=True), nullable=False)
    id_usuario_edicion = Column(UUID(as_uuid=True), nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    libros = relationship("Libro", back_populates="autor")
    revistas = relationship("Revista", back_populates="autor")
    periodicos = relationship("Periodico", back_populates="autor")

    def __repr__(self):
        return f"<Autor(id={self.id}, nombre='{self.nombre}', nacionalidad='{self.nacionalidad}')>"
