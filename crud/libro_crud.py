from typing import List, Optional
from uuid import UUID

from entities.autores import Autor
from entities.editoriales import Editorial
from entities.libros import Libro
from sqlalchemy.orm import Session


class LibroCRUD:
    def __init__(self, db: Session):
        self.db = db

    def crear_libro(
        self,
        titulo: str,
        id_editorial: UUID,
        id_autor: UUID,
        id_usuario_creacion: UUID,
        isbn: Optional[str] = None,
        numero_paginas: Optional[str] = None,
        id_categoria: Optional[UUID] = None,
    ) -> Libro:
        """Crear un nuevo libro."""
        if not titulo or len(titulo.strip()) == 0:
            raise ValueError("El título es obligatorio")
        if len(titulo) > 255:
            raise ValueError("El título no puede exceder 255 caracteres")

        if isbn and len(isbn) > 20:
            raise ValueError("El ISBN no puede exceder 20 caracteres")

        if isbn and self.obtener_libro_por_isbn(isbn):
            raise ValueError("Ya existe un libro con ese ISBN")

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

        libro = Libro(
            titulo=titulo.strip(),
            isbn=isbn.strip() if isbn else None,
            numero_paginas=numero_paginas.strip() if numero_paginas else None,
            id_editorial=id_editorial,
            id_autor=id_autor,
            id_categoria=id_categoria,
            id_usuario_creacion=id_usuario_creacion,
            id_usuario_edicion=id_usuario_creacion,
        )
        self.db.add(libro)
        self.db.commit()
        self.db.refresh(libro)
        return libro

    def obtener_libros(self, skip: int = 0, limit: int = 1000) -> List[Libro]:
        """Obtener todos los libros."""
        return self.db.query(Libro).offset(skip).limit(limit).all()

    def obtener_libro(self, libro_id: UUID) -> Optional[Libro]:
        """Obtener un libro por ID."""
        return self.db.query(Libro).filter(Libro.id == libro_id).first()

    def obtener_libro_por_isbn(self, isbn: str) -> Optional[Libro]:
        """Obtener un libro por ISBN."""
        return self.db.query(Libro).filter(Libro.isbn == isbn.strip()).first()

    def actualizar_libro(
        self, libro_id: UUID, id_usuario_edicion: UUID, **kwargs
    ) -> Optional[Libro]:
        """Actualizar un libro."""
        libro = self.obtener_libro(libro_id)
        if not libro:
            return None

        if "titulo" in kwargs:
            titulo = kwargs["titulo"]
            if not titulo or len(titulo.strip()) == 0:
                raise ValueError("El título es obligatorio")
            if len(titulo) > 255:
                raise ValueError("El título no puede exceder 255 caracteres")
            kwargs["titulo"] = titulo.strip()

        if "isbn" in kwargs and kwargs["isbn"]:
            isbn = kwargs["isbn"]
            if len(isbn) > 20:
                raise ValueError("El ISBN no puede exceder 20 caracteres")
            existing = self.obtener_libro_por_isbn(isbn)
            if existing and existing.id != libro_id:
                raise ValueError("Ya existe un libro con ese ISBN")
            kwargs["isbn"] = isbn.strip()

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

        libro.id_usuario_edicion = id_usuario_edicion

        for key, value in kwargs.items():
            if hasattr(libro, key):
                setattr(libro, key, value)
        self.db.commit()
        self.db.refresh(libro)
        return libro

    def eliminar_libro(self, libro_id: UUID) -> bool:
        """Eliminar un libro."""
        libro = self.obtener_libro(libro_id)
        if libro:
            self.db.delete(libro)
            self.db.commit()
            return True
        return False
