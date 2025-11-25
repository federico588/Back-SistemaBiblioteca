import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.config import Base


class Libro(Base):
    """Entidad que representa un libro."""

    __tablename__ = "libros"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    titulo = Column(String(255), nullable=False)
    isbn = Column(String(20), unique=True, nullable=True)
    numero_paginas = Column(String(10), nullable=True)
    id_editorial = Column(
        UUID(as_uuid=True), ForeignKey("editoriales.id"), nullable=False
    )
    id_autor = Column(UUID(as_uuid=True), ForeignKey("autores.id"), nullable=False)
    id_categoria = Column(
        UUID(as_uuid=True), ForeignKey("categorias.id"), nullable=True
    )
    id_usuario_creacion = Column(UUID(as_uuid=True), nullable=False)
    id_usuario_edicion = Column(UUID(as_uuid=True), nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    editorial = relationship("Editorial", back_populates="libros")
    autor = relationship("Autor", back_populates="libros")
    categoria = relationship("Categoria", back_populates="libros")
    items = relationship("Item", back_populates="libro")

    def __repr__(self):
        return f"<Libro(id={self.id}, titulo='{self.titulo}', isbn='{self.isbn}')>"
