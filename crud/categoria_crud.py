from typing import List, Optional
from uuid import UUID

from entities.categoria import Categoria
from sqlalchemy.orm import Session


class CategoriaCRUD:
    def __init__(self, db: Session):
        self.db = db

    def crear_categoria(
        self,
        nombre: str,
        id_usuario_creacion: UUID,
        descripcion: Optional[str] = None,
    ) -> Categoria:
        """Crear una nueva categoría."""
        if not nombre or len(nombre.strip()) == 0:
            raise ValueError("El nombre es obligatorio")
        if len(nombre) > 100:
            raise ValueError("El nombre no puede exceder 100 caracteres")

        if self.obtener_categoria_por_nombre(nombre):
            raise ValueError("Ya existe una categoría con ese nombre")

        if descripcion and len(descripcion) > 500:
            raise ValueError("La descripción no puede exceder 500 caracteres")

        categoria = Categoria(
            nombre=nombre.strip(),
            descripcion=descripcion.strip() if descripcion else None,
            id_usuario_creacion=id_usuario_creacion,
            id_usuario_edicion=id_usuario_creacion,
        )
        self.db.add(categoria)
        self.db.commit()
        self.db.refresh(categoria)
        return categoria

    def obtener_categorias(self, skip: int = 0, limit: int = 1000) -> List[Categoria]:
        """Obtener todas las categorías."""
        return self.db.query(Categoria).offset(skip).limit(limit).all()

    def obtener_categoria(self, categoria_id: UUID) -> Optional[Categoria]:
        """Obtener una categoría por ID."""
        return self.db.query(Categoria).filter(Categoria.id == categoria_id).first()

    def obtener_categoria_por_nombre(self, nombre: str) -> Optional[Categoria]:
        """Obtener una categoría por nombre."""
        return (
            self.db.query(Categoria).filter(Categoria.nombre == nombre.strip()).first()
        )

    def actualizar_categoria(
        self, categoria_id: UUID, id_usuario_edicion: UUID, **kwargs
    ) -> Optional[Categoria]:
        """Actualizar una categoría."""
        categoria = self.obtener_categoria(categoria_id)
        if not categoria:
            return None

        if "nombre" in kwargs:
            nombre = kwargs["nombre"]
            if not nombre or len(nombre.strip()) == 0:
                raise ValueError("El nombre es obligatorio")
            if len(nombre) > 100:
                raise ValueError("El nombre no puede exceder 100 caracteres")
            existing = self.obtener_categoria_por_nombre(nombre)
            if existing and existing.id != categoria_id:
                raise ValueError("Ya existe una categoría con ese nombre")
            kwargs["nombre"] = nombre.strip()

        if "descripcion" in kwargs and kwargs["descripcion"]:
            if len(kwargs["descripcion"]) > 500:
                raise ValueError("La descripción no puede exceder 500 caracteres")
            kwargs["descripcion"] = kwargs["descripcion"].strip()

        categoria.id_usuario_edicion = id_usuario_edicion

        for key, value in kwargs.items():
            if hasattr(categoria, key):
                setattr(categoria, key, value)
        self.db.commit()
        self.db.refresh(categoria)
        return categoria

    def eliminar_categoria(self, categoria_id: UUID) -> bool:
        """Eliminar una categoría."""
        categoria = self.obtener_categoria(categoria_id)
        if categoria:
            self.db.delete(categoria)
            self.db.commit()
            return True
        return False
