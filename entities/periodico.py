import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.config import Base


class Periodico(Base):
    """Entidad que representa un periódico."""

    __tablename__ = "periodicos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    titulo = Column(String(255), nullable=False)
    fecha_publicacion = Column(DateTime(timezone=True), nullable=False)
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

    editorial = relationship("Editorial", back_populates="periodicos")
    autor = relationship("Autor", back_populates="periodicos")
    categoria = relationship("Categoria", back_populates="periodicos")
    items = relationship("Item", back_populates="periodico")

    def __repr__(self):
        return f"<Periodico(id={self.id}, titulo='{self.titulo}', fecha='{self.fecha_publicacion}')>"
