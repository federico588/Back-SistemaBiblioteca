from typing import List, Optional
from uuid import UUID

from entities.editoriales import Editorial
from sqlalchemy.orm import Session


class EditorialCRUD:
    def __init__(self, db: Session):
        self.db = db

    def crear_editorial(
        self,
        nombre: str,
        id_usuario_creacion: UUID,
        direccion: Optional[str] = None,
        telefono: Optional[str] = None,
    ) -> Editorial:
        """Crear una nueva editorial."""
        if not nombre or len(nombre.strip()) == 0:
            raise ValueError("El nombre es obligatorio")
        if len(nombre) > 100:
            raise ValueError("El nombre no puede exceder 100 caracteres")

        if direccion and len(direccion) > 255:
            raise ValueError("La dirección no puede exceder 255 caracteres")

        if telefono and len(telefono) > 20:
            raise ValueError("El teléfono no puede exceder 20 caracteres")

        editorial = Editorial(
            nombre=nombre.strip(),
            direccion=direccion.strip() if direccion else None,
            telefono=telefono.strip() if telefono else None,
            id_usuario_creacion=id_usuario_creacion,
            id_usuario_edicion=id_usuario_creacion,
        )
        self.db.add(editorial)
        self.db.commit()
        self.db.refresh(editorial)
        return editorial

    def obtener_editoriales(self, skip: int = 0, limit: int = 1000) -> List[Editorial]:
        """Obtener todas las editoriales."""
        return self.db.query(Editorial).offset(skip).limit(limit).all()

    def obtener_editorial(self, editorial_id: UUID) -> Optional[Editorial]:
        """Obtener una editorial por ID."""
        return self.db.query(Editorial).filter(Editorial.id == editorial_id).first()

    def actualizar_editorial(
        self, editorial_id: UUID, id_usuario_edicion: UUID, **kwargs
    ) -> Optional[Editorial]:
        """Actualizar una editorial."""
        editorial = self.obtener_editorial(editorial_id)
        if not editorial:
            return None

        if "nombre" in kwargs:
            nombre = kwargs["nombre"]
            if not nombre or len(nombre.strip()) == 0:
                raise ValueError("El nombre es obligatorio")
            if len(nombre) > 100:
                raise ValueError("El nombre no puede exceder 100 caracteres")
            kwargs["nombre"] = nombre.strip()

        if "direccion" in kwargs and kwargs["direccion"]:
            if len(kwargs["direccion"]) > 255:
                raise ValueError("La dirección no puede exceder 255 caracteres")
            kwargs["direccion"] = kwargs["direccion"].strip()

        if "telefono" in kwargs and kwargs["telefono"]:
            if len(kwargs["telefono"]) > 20:
                raise ValueError("El teléfono no puede exceder 20 caracteres")
            kwargs["telefono"] = kwargs["telefono"].strip()

        editorial.id_usuario_edicion = id_usuario_edicion

        for key, value in kwargs.items():
            if hasattr(editorial, key):
                setattr(editorial, key, value)
        self.db.commit()
        self.db.refresh(editorial)
        return editorial

    def eliminar_editorial(self, editorial_id: UUID) -> bool:
        """Eliminar una editorial."""
        editorial = self.obtener_editorial(editorial_id)
        if editorial:
            self.db.delete(editorial)
            self.db.commit()
            return True
        return False
