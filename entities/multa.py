import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.config import Base


class Multa(Base):
    """Entidad que representa una multa por retraso en la devolución de un préstamo."""

    __tablename__ = "multas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    id_prestamo = Column(
        UUID(as_uuid=True), ForeignKey("prestamos.id"), nullable=False, unique=True
    )
    id_usuario = Column(
        UUID(as_uuid=True), ForeignKey("tbl_usuarios.id"), nullable=False
    )
    monto = Column(Numeric(10, 2), nullable=False)
    motivo = Column(String(255), nullable=True)
    fecha_multa = Column(DateTime(timezone=True), server_default=func.now())
    fecha_pago = Column(DateTime(timezone=True), nullable=True)
    estado = Column(String(20), default="pendiente")
    id_usuario_creacion = Column(UUID(as_uuid=True), nullable=False)
    id_usuario_edicion = Column(UUID(as_uuid=True), nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    prestamo = relationship("Prestamo", back_populates="multa")
    usuario = relationship("Usuario", back_populates="multas")

    def __repr__(self):
        return (
            f"<Multa(id={self.id}, prestamo='{self.id_prestamo}', monto={self.monto})>"
        )
