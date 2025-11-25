import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.config import Base


class Item(Base):
    """Entidad que representa un ejemplar físico prestable de la biblioteca."""

    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Relación con Material Bibliográfico (solo uno debe estar presente)
    id_libro = Column(
        UUID(as_uuid=True),
        ForeignKey("libros.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    id_revista = Column(
        UUID(as_uuid=True),
        ForeignKey("revistas.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    id_periodico = Column(
        UUID(as_uuid=True),
        ForeignKey("periodicos.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Información del ejemplar
    codigo_barras = Column(String(50), unique=True, nullable=True, index=True)
    ubicacion = Column(String(100), nullable=True)
    estado_fisico = Column(
        String(50), default="bueno"
    )  # bueno, regular, malo, reparacion
    disponible = Column(Boolean, default=True, index=True)
    observaciones = Column(Text, nullable=True)

    # Auditoría
    id_usuario_creacion = Column(UUID(as_uuid=True), nullable=False)
    id_usuario_edicion = Column(UUID(as_uuid=True), nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    libro = relationship("Libro", back_populates="items")
    revista = relationship("Revista", back_populates="items")
    periodico = relationship("Periodico", back_populates="items")
    prestamos = relationship("Prestamo", back_populates="item")

    # Constraint: Solo uno de los tres IDs debe estar presente
    __table_args__ = (
        CheckConstraint(
            "(id_libro IS NOT NULL AND id_revista IS NULL AND id_periodico IS NULL) OR "
            "(id_libro IS NULL AND id_revista IS NOT NULL AND id_periodico IS NULL) OR "
            "(id_libro IS NULL AND id_revista IS NULL AND id_periodico IS NOT NULL)",
            name="chk_item_tipo",
        ),
    )

    @property
    def tipo_item(self):
        """Determina el tipo de item basado en qué relación está presente"""
        if self.id_libro:
            return "libro"
        elif self.id_revista:
            return "revista"
        elif self.id_periodico:
            return "periodico"
        return None

    @property
    def material(self):
        """Retorna el material bibliográfico asociado"""
        return self.libro or self.revista or self.periodico

    def __repr__(self):
        tipo = self.tipo_item or "desconocido"
        return f"<Item(id={self.id}, tipo='{tipo}', disponible={self.disponible})>"
