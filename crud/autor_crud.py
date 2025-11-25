from typing import List, Optional
from uuid import UUID

from entities.autores import Autor
from sqlalchemy.orm import Session


class AutorCRUD:
    def __init__(self, db: Session):
        self.db = db

    def crear_autor(
        self,
        nombre: str,
        nacionalidad: str,
        id_usuario_creacion: UUID,
        bibliografia: Optional[str] = None,
    ) -> Autor:
        """Crear un nuevo autor."""
        if not nombre or len(nombre.strip()) == 0:
            raise ValueError("El nombre es obligatorio")
        if len(nombre) > 100:
            raise ValueError("El nombre no puede exceder 100 caracteres")

        if not nacionalidad or len(nacionalidad.strip()) == 0:
            raise ValueError("La nacionalidad es obligatoria")
        if len(nacionalidad) > 50:
            raise ValueError("La nacionalidad no puede exceder 50 caracteres")

        if bibliografia and len(bibliografia) > 500:
            raise ValueError("La bibliografía no puede exceder 500 caracteres")

        autor = Autor(
            nombre=nombre.strip(),
            nacionalidad=nacionalidad.strip(),
            bibliografia=bibliografia.strip() if bibliografia else None,
            id_usuario_creacion=id_usuario_creacion,
            id_usuario_edicion=id_usuario_creacion,
        )
        self.db.add(autor)
        self.db.commit()
        self.db.refresh(autor)
        return autor

    def obtener_autores(self, skip: int = 0, limit: int = 1000) -> List[Autor]:
        """Obtener todos los autores."""
        return self.db.query(Autor).offset(skip).limit(limit).all()

    def obtener_autor(self, autor_id: UUID) -> Optional[Autor]:
        """Obtener un autor por ID."""
        return self.db.query(Autor).filter(Autor.id == autor_id).first()

    def actualizar_autor(
        self, autor_id: UUID, id_usuario_edicion: UUID, **kwargs
    ) -> Optional[Autor]:
        """Actualizar un autor."""
        autor = self.obtener_autor(autor_id)
        if not autor:
            return None

        if "nombre" in kwargs:
            nombre = kwargs["nombre"]
            if not nombre or len(nombre.strip()) == 0:
                raise ValueError("El nombre es obligatorio")
            if len(nombre) > 100:
                raise ValueError("El nombre no puede exceder 100 caracteres")
            kwargs["nombre"] = nombre.strip()

        if "nacionalidad" in kwargs:
            nacionalidad = kwargs["nacionalidad"]
            if not nacionalidad or len(nacionalidad.strip()) == 0:
                raise ValueError("La nacionalidad es obligatoria")
            if len(nacionalidad) > 50:
                raise ValueError("La nacionalidad no puede exceder 50 caracteres")
            kwargs["nacionalidad"] = nacionalidad.strip()

        if "bibliografia" in kwargs and kwargs["bibliografia"]:
            if len(kwargs["bibliografia"]) > 500:
                raise ValueError("La bibliografía no puede exceder 500 caracteres")
            kwargs["bibliografia"] = kwargs["bibliografia"].strip()

        autor.id_usuario_edicion = id_usuario_edicion

        for key, value in kwargs.items():
            if hasattr(autor, key):
                setattr(autor, key, value)
        self.db.commit()
        self.db.refresh(autor)
        return autor

    def eliminar_autor(self, autor_id: UUID) -> bool:
        """Eliminar un autor."""
        autor = self.obtener_autor(autor_id)
        if autor:
            self.db.delete(autor)
            self.db.commit()
            return True
        return False
