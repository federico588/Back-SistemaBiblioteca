from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from entities.multa import Multa
from sqlalchemy.orm import Session


class MultaCRUD:
    def __init__(self, db: Session):
        self.db = db

    def crear_multa(
        self,
        id_prestamo: UUID,
        id_usuario: UUID,
        monto: Decimal,
        id_usuario_creacion: UUID,
        motivo: Optional[str] = None,
    ) -> Multa:
        """Crear una nueva multa."""
        if monto <= 0:
            raise ValueError("El monto debe ser mayor a cero")

        if self.obtener_multa_por_prestamo(id_prestamo):
            raise ValueError("Ya existe una multa para este préstamo")

        if motivo and len(motivo) > 255:
            raise ValueError("El motivo no puede exceder 255 caracteres")

        multa = Multa(
            id_prestamo=id_prestamo,
            id_usuario=id_usuario,
            monto=monto,
            motivo=motivo.strip() if motivo else None,
            estado="pendiente",
            id_usuario_creacion=id_usuario_creacion,
            id_usuario_edicion=id_usuario_creacion,
        )
        self.db.add(multa)
        self.db.commit()
        self.db.refresh(multa)
        return multa

    def obtener_multas(
        self,
        skip: int = 0,
        limit: int = 1000,
        estado: Optional[str] = None,
        id_usuario: Optional[UUID] = None,
    ) -> List[Multa]:
        """Obtener todas las multas."""
        query = self.db.query(Multa)
        if estado:
            query = query.filter(Multa.estado == estado)
        if id_usuario:
            query = query.filter(Multa.id_usuario == id_usuario)
        return query.offset(skip).limit(limit).all()

    def obtener_multa(self, multa_id: UUID) -> Optional[Multa]:
        """Obtener una multa por ID."""
        return self.db.query(Multa).filter(Multa.id == multa_id).first()

    def obtener_multa_por_prestamo(self, id_prestamo: UUID) -> Optional[Multa]:
        """Obtener una multa por préstamo."""
        return self.db.query(Multa).filter(Multa.id_prestamo == id_prestamo).first()

    def actualizar_multa(
        self, multa_id: UUID, id_usuario_edicion: UUID, **kwargs
    ) -> Optional[Multa]:
        """Actualizar una multa."""
        multa = self.obtener_multa(multa_id)
        if not multa:
            return None

        if "monto" in kwargs:
            monto = kwargs["monto"]
            if monto <= 0:
                raise ValueError("El monto debe ser mayor a cero")
            kwargs["monto"] = monto

        if "motivo" in kwargs and kwargs["motivo"]:
            if len(kwargs["motivo"]) > 255:
                raise ValueError("El motivo no puede exceder 255 caracteres")
            kwargs["motivo"] = kwargs["motivo"].strip()

        if "estado" in kwargs:
            valid_states = ["pendiente", "pagada", "cancelada"]
            if kwargs["estado"] not in valid_states:
                raise ValueError(
                    f"El estado debe ser uno de: {', '.join(valid_states)}"
                )

        multa.id_usuario_edicion = id_usuario_edicion

        for key, value in kwargs.items():
            if hasattr(multa, key):
                setattr(multa, key, value)
        self.db.commit()
        self.db.refresh(multa)
        return multa

    def pagar_multa(self, multa_id: UUID, id_usuario_edicion: UUID) -> Optional[Multa]:
        """Marcar una multa como pagada."""
        multa = self.obtener_multa(multa_id)
        if not multa:
            return None

        multa.fecha_pago = datetime.utcnow()
        multa.estado = "pagada"
        multa.id_usuario_edicion = id_usuario_edicion
        self.db.commit()
        self.db.refresh(multa)
        return multa

    def eliminar_multa(self, multa_id: UUID) -> bool:
        """Eliminar una multa."""
        multa = self.obtener_multa(multa_id)
        if multa:
            self.db.delete(multa)
            self.db.commit()
            return True
        return False
