from datetime import datetime, timedelta, timezone
from typing import List, Optional
from uuid import UUID

from entities.items import Item
from entities.prestamo import Prestamo
from entities.usuario import Usuario
from sqlalchemy.orm import Session


class PrestamoCRUD:
    def __init__(self, db: Session):
        self.db = db

    def crear_prestamo(
        self,
        id_item: UUID,
        id_usuario: UUID,
        id_usuario_creacion: UUID,
        fecha_devolucion_estimada: Optional[datetime] = None,
    ) -> Prestamo:
        """Crear un nuevo préstamo."""
        # Validar UUIDs
        if not id_item:
            raise ValueError("El id_item es obligatorio")
        if not id_usuario:
            raise ValueError("El id_usuario es obligatorio")
        if not id_usuario_creacion:
            raise ValueError("El id_usuario_creacion es obligatorio")

        # Validar que id_usuario_creacion no sea el UUID por defecto
        default_uuid = UUID("00000000-0000-0000-0000-000000000000")
        if id_usuario_creacion == default_uuid:
            raise ValueError(
                "El id_usuario_creacion no puede ser el UUID por defecto. Debe estar autenticado."
            )

        # Validar que el item existe
        try:
            item = self.db.query(Item).filter(Item.id == id_item).first()
        except Exception as e:
            raise ValueError(f"Error al buscar el item: {str(e)}")

        if not item:
            raise ValueError("El item especificado no existe")

        # Validar que el item tiene la estructura correcta (nueva estructura)
        if not hasattr(item, "disponible"):
            raise ValueError(
                "Error: La base de datos no está actualizada. Por favor ejecuta la migración de Alembic: alembic upgrade head"
            )

        # Validar que el item está disponible
        try:
            disponible = item.disponible
        except AttributeError:
            raise ValueError(
                "Error: La base de datos no está actualizada. El campo 'disponible' no existe en Item. Ejecuta: alembic upgrade head"
            )

        if not disponible:
            raise ValueError("El item no está disponible para préstamo")

        # Validar que no hay un préstamo activo del mismo item
        prestamo_activo = (
            self.db.query(Prestamo)
            .filter(Prestamo.id_item == id_item)
            .filter(Prestamo.estado == "activo")
            .first()
        )
        if prestamo_activo:
            raise ValueError("El item ya tiene un préstamo activo")

        # Validar que el usuario existe
        usuario = self.db.query(Usuario).filter(Usuario.id == id_usuario).first()
        if not usuario:
            raise ValueError("El usuario especificado no existe")

        if not usuario.activo:
            raise ValueError("El usuario no está activo")

        # Manejar fecha de devolución estimada
        now = datetime.now(timezone.utc)
        if not fecha_devolucion_estimada:
            fecha_devolucion_estimada = now + timedelta(days=15)
        else:
            # Si viene como string, convertirlo a datetime
            if isinstance(fecha_devolucion_estimada, str):
                try:
                    # Intentar parsear formato ISO
                    fecha_str = fecha_devolucion_estimada.replace("Z", "+00:00")
                    fecha_devolucion_estimada = datetime.fromisoformat(fecha_str)
                except (ValueError, AttributeError) as e:
                    raise ValueError(f"Formato de fecha inválido: {str(e)}")

            # Asegurar que la fecha tiene timezone
            if isinstance(fecha_devolucion_estimada, datetime):
                if fecha_devolucion_estimada.tzinfo is None:
                    fecha_devolucion_estimada = fecha_devolucion_estimada.replace(
                        tzinfo=timezone.utc
                    )
            else:
                raise ValueError(
                    "La fecha de devolución estimada debe ser un datetime válido"
                )

        if fecha_devolucion_estimada <= now:
            raise ValueError("La fecha de devolución estimada debe ser futura")

        prestamo = Prestamo(
            id_item=id_item,
            id_usuario=id_usuario,
            fecha_devolucion_estimada=fecha_devolucion_estimada,
            estado="activo",
            id_usuario_creacion=id_usuario_creacion,
            id_usuario_edicion=id_usuario_creacion,
        )
        self.db.add(prestamo)

        # Marcar el item como no disponible
        item.disponible = False
        self.db.commit()
        self.db.refresh(prestamo)
        return prestamo

    def obtener_prestamos(
        self,
        skip: int = 0,
        limit: int = 1000,
        estado: Optional[str] = None,
        id_usuario: Optional[UUID] = None,
    ) -> List[Prestamo]:
        """Obtener todos los préstamos."""
        query = self.db.query(Prestamo)
        if estado:
            query = query.filter(Prestamo.estado == estado)
        if id_usuario:
            query = query.filter(Prestamo.id_usuario == id_usuario)
        return query.offset(skip).limit(limit).all()

    def obtener_prestamo(self, prestamo_id: UUID) -> Optional[Prestamo]:
        """Obtener un préstamo por ID."""
        return self.db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()

    def actualizar_prestamo(
        self, prestamo_id: UUID, id_usuario_edicion: UUID, **kwargs
    ) -> Optional[Prestamo]:
        """Actualizar un préstamo."""
        prestamo = self.obtener_prestamo(prestamo_id)
        if not prestamo:
            return None

        if "fecha_devolucion_estimada" in kwargs:
            fecha = kwargs["fecha_devolucion_estimada"]
            if fecha:
                # Asegurar que la fecha tiene timezone
                if fecha.tzinfo is None:
                    fecha = fecha.replace(tzinfo=timezone.utc)
                if fecha <= datetime.now(timezone.utc):
                    raise ValueError("La fecha de devolución estimada debe ser futura")

        if "estado" in kwargs:
            valid_states = ["activo", "devuelto", "vencido"]
            if kwargs["estado"] not in valid_states:
                raise ValueError(
                    f"El estado debe ser uno de: {', '.join(valid_states)}"
                )

        prestamo.id_usuario_edicion = id_usuario_edicion

        for key, value in kwargs.items():
            if hasattr(prestamo, key):
                setattr(prestamo, key, value)
        self.db.commit()
        self.db.refresh(prestamo)
        return prestamo

    def devolver_prestamo(
        self, prestamo_id: UUID, id_usuario_edicion: UUID
    ) -> Optional[Prestamo]:
        """Marcar un préstamo como devuelto."""
        prestamo = self.obtener_prestamo(prestamo_id)
        if not prestamo:
            return None

        prestamo.fecha_devolucion_real = datetime.now(timezone.utc)
        prestamo.estado = "devuelto"
        prestamo.id_usuario_edicion = id_usuario_edicion

        # Marcar el item como disponible nuevamente
        item = self.db.query(Item).filter(Item.id == prestamo.id_item).first()
        if item:
            item.disponible = True

        self.db.commit()
        self.db.refresh(prestamo)
        return prestamo

    def eliminar_prestamo(self, prestamo_id: UUID) -> bool:
        """Eliminar un préstamo."""
        prestamo = self.obtener_prestamo(prestamo_id)
        if prestamo:
            # Si el préstamo está activo, marcar el item como disponible
            if prestamo.estado == "activo":
                item = self.db.query(Item).filter(Item.id == prestamo.id_item).first()
                if item:
                    item.disponible = True
            self.db.delete(prestamo)
            self.db.commit()
            return True
        return False
