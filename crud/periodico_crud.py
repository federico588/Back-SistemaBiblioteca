from datetime import datetime
from typing import List, Optional
from uuid import UUID

from entities.autores import Autor
from entities.editoriales import Editorial
from entities.periodico import Periodico
from sqlalchemy.orm import Session


class PeriodicoCRUD:
    def __init__(self, db: Session):
        self.db = db

    def crear_periodico(
        self,
        titulo: str,
        fecha_publicacion: datetime,
        id_editorial: UUID,
        id_autor: UUID,
        id_usuario_creacion: UUID,
        id_categoria: Optional[UUID] = None,
    ) -> Periodico:
        """Crear un nuevo periódico."""
        if not titulo or len(titulo.strip()) == 0:
            raise ValueError("El título es obligatorio")
        if len(titulo) > 255:
            raise ValueError("El título no puede exceder 255 caracteres")

        if not fecha_publicacion:
            raise ValueError("La fecha de publicación es obligatoria")

        # Validar que el autor existe
        autor = self.db.query(Autor).filter(Autor.id == id_autor).first()
        if not autor:
            raise ValueError("El autor especificado no existe")

        # Validar que la editorial existe
        editorial = (
            self.db.query(Editorial).filter(Editorial.id == id_editorial).first()
        )
        if not editorial:
            raise ValueError("La editorial especificada no existe")

        # Validar que la categoría existe si se proporciona
        if id_categoria:
            from entities.categoria import Categoria

            categoria = (
                self.db.query(Categoria).filter(Categoria.id == id_categoria).first()
            )
            if not categoria:
                raise ValueError("La categoría especificada no existe")

        periodico = Periodico(
            titulo=titulo.strip(),
            fecha_publicacion=fecha_publicacion,
            id_editorial=id_editorial,
            id_autor=id_autor,
            id_categoria=id_categoria,
            id_usuario_creacion=id_usuario_creacion,
            id_usuario_edicion=id_usuario_creacion,
        )
        self.db.add(periodico)
        self.db.commit()
        self.db.refresh(periodico)
        return periodico

    def obtener_periodicos(self, skip: int = 0, limit: int = 1000) -> List[Periodico]:
        """Obtener todos los periódicos."""
        return self.db.query(Periodico).offset(skip).limit(limit).all()

    def obtener_periodico(self, periodico_id: UUID) -> Optional[Periodico]:
        """Obtener un periódico por ID."""
        return self.db.query(Periodico).filter(Periodico.id == periodico_id).first()

    def actualizar_periodico(
        self, periodico_id: UUID, id_usuario_edicion: UUID, **kwargs
    ) -> Optional[Periodico]:
        """Actualizar un periódico."""
        periodico = self.obtener_periodico(periodico_id)
        if not periodico:
            return None

        if "titulo" in kwargs:
            titulo = kwargs["titulo"]
            if not titulo or len(titulo.strip()) == 0:
                raise ValueError("El título es obligatorio")
            if len(titulo) > 255:
                raise ValueError("El título no puede exceder 255 caracteres")
            kwargs["titulo"] = titulo.strip()

        if "fecha_publicacion" in kwargs and not kwargs["fecha_publicacion"]:
            raise ValueError("La fecha de publicación es obligatoria")

        if "id_autor" in kwargs and kwargs["id_autor"]:
            autor = self.db.query(Autor).filter(Autor.id == kwargs["id_autor"]).first()
            if not autor:
                raise ValueError("El autor especificado no existe")

        if "id_editorial" in kwargs and kwargs["id_editorial"]:
            editorial = (
                self.db.query(Editorial)
                .filter(Editorial.id == kwargs["id_editorial"])
                .first()
            )
            if not editorial:
                raise ValueError("La editorial especificada no existe")

        if "id_categoria" in kwargs and kwargs["id_categoria"]:
            from entities.categoria import Categoria

            categoria = (
                self.db.query(Categoria)
                .filter(Categoria.id == kwargs["id_categoria"])
                .first()
            )
            if not categoria:
                raise ValueError("La categoría especificada no existe")

        periodico.id_usuario_edicion = id_usuario_edicion

        for key, value in kwargs.items():
            if hasattr(periodico, key):
                setattr(periodico, key, value)
        self.db.commit()
        self.db.refresh(periodico)
        return periodico

    def eliminar_periodico(self, periodico_id: UUID) -> bool:
        """Eliminar un periódico."""
        periodico = self.obtener_periodico(periodico_id)
        if periodico:
            self.db.delete(periodico)
            self.db.commit()
            return True
        return False
