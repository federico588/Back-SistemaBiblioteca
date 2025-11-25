import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.config import Base


class Revista(Base):
    """Entidad que representa una revista."""

    __tablename__ = "revistas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    titulo = Column(String(255), nullable=False)
    numero_publicacion = Column(String(50), nullable=True)
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

    editorial = relationship("Editorial", back_populates="revistas")
    autor = relationship("Autor", back_populates="revistas")
    categoria = relationship("Categoria", back_populates="revistas")
    items = relationship("Item", back_populates="revista")

    def __repr__(self):
        return f"<Revista(id={self.id}, titulo='{self.titulo}', numero='{self.numero_publicacion}')>"
