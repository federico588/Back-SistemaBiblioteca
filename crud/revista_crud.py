from typing import List, Optional
from uuid import UUID

from entities.autores import Autor
from entities.editoriales import Editorial
from entities.revista import Revista
from sqlalchemy.orm import Session


class RevistaCRUD:
    def __init__(self, db: Session):
        self.db = db

    def crear_revista(
        self,
        titulo: str,
        id_editorial: UUID,
        id_autor: UUID,
        id_usuario_creacion: UUID,
        numero_publicacion: Optional[str] = None,
        id_categoria: Optional[UUID] = None,
    ) -> Revista:
        """Crear una nueva revista."""
        if not titulo or len(titulo.strip()) == 0:
            raise ValueError("El título es obligatorio")
        if len(titulo) > 255:
            raise ValueError("El título no puede exceder 255 caracteres")

        if numero_publicacion and len(numero_publicacion) > 50:
            raise ValueError("El número de publicación no puede exceder 50 caracteres")

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

        revista = Revista(
            titulo=titulo.strip(),
            numero_publicacion=numero_publicacion.strip()
            if numero_publicacion
            else None,
            id_editorial=id_editorial,
            id_autor=id_autor,
            id_categoria=id_categoria,
            id_usuario_creacion=id_usuario_creacion,
            id_usuario_edicion=id_usuario_creacion,
        )
        self.db.add(revista)
        self.db.commit()
        self.db.refresh(revista)
        return revista

    def obtener_revistas(self, skip: int = 0, limit: int = 1000) -> List[Revista]:
        """Obtener todas las revistas."""
        return self.db.query(Revista).offset(skip).limit(limit).all()

    def obtener_revista(self, revista_id: UUID) -> Optional[Revista]:
        """Obtener una revista por ID."""
        return self.db.query(Revista).filter(Revista.id == revista_id).first()

    def actualizar_revista(
        self, revista_id: UUID, id_usuario_edicion: UUID, **kwargs
    ) -> Optional[Revista]:
        """Actualizar una revista."""
        revista = self.obtener_revista(revista_id)
        if not revista:
            return None

        if "titulo" in kwargs:
            titulo = kwargs["titulo"]
            if not titulo or len(titulo.strip()) == 0:
                raise ValueError("El título es obligatorio")
            if len(titulo) > 255:
                raise ValueError("El título no puede exceder 255 caracteres")
            kwargs["titulo"] = titulo.strip()

        if "numero_publicacion" in kwargs and kwargs["numero_publicacion"]:
            if len(kwargs["numero_publicacion"]) > 50:
                raise ValueError(
                    "El número de publicación no puede exceder 50 caracteres"
                )
            kwargs["numero_publicacion"] = kwargs["numero_publicacion"].strip()

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

        revista.id_usuario_edicion = id_usuario_edicion

        for key, value in kwargs.items():
            if hasattr(revista, key):
                setattr(revista, key, value)
        self.db.commit()
        self.db.refresh(revista)
        return revista

    def eliminar_revista(self, revista_id: UUID) -> bool:
        """Eliminar una revista."""
        revista = self.obtener_revista(revista_id)
        if revista:
            self.db.delete(revista)
            self.db.commit()
            return True
        return False
