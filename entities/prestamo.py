import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.config import Base


class Prestamo(Base):
    """Entidad que representa un préstamo de un item de la biblioteca."""

    __tablename__ = "prestamos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    id_item = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)
    id_usuario = Column(
        UUID(as_uuid=True), ForeignKey("tbl_usuarios.id"), nullable=False
    )
    fecha_prestamo = Column(DateTime(timezone=True), server_default=func.now())
    fecha_devolucion_estimada = Column(DateTime(timezone=True), nullable=False)
    fecha_devolucion_real = Column(DateTime(timezone=True), nullable=True)
    estado = Column(String(20), default="activo")
    id_usuario_creacion = Column(UUID(as_uuid=True), nullable=False)
    id_usuario_edicion = Column(UUID(as_uuid=True), nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    item = relationship("Item", back_populates="prestamos")
    usuario = relationship("Usuario", back_populates="prestamos")
    multa = relationship("Multa", back_populates="prestamo", uselist=False)

    def __repr__(self):
        return f"<Prestamo(id={self.id}, item='{self.id_item}', usuario='{self.id_usuario}')>"
