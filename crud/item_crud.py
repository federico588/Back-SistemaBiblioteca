from typing import List, Optional
from uuid import UUID

from entities.items import Item
from entities.libros import Libro
from entities.periodico import Periodico
from entities.revista import Revista
from sqlalchemy.orm import Session, joinedload


class ItemCRUD:
    def __init__(self, db: Session):
        self.db = db

    def crear_item(
        self,
        id_libro: Optional[UUID] = None,
        id_revista: Optional[UUID] = None,
        id_periodico: Optional[UUID] = None,
        codigo_barras: Optional[str] = None,
        ubicacion: Optional[str] = None,
        estado_fisico: str = "bueno",
        disponible: bool = True,
        observaciones: Optional[str] = None,
        id_usuario_creacion: UUID = None,
    ) -> Item:
        """Crear un nuevo item (ejemplar físico)."""
        # Validar que exactamente uno de los tres IDs esté presente
        tipos_presentes = sum(
            [id_libro is not None, id_revista is not None, id_periodico is not None]
        )

        if tipos_presentes != 1:
            raise ValueError(
                "Debe especificar exactamente uno: id_libro, id_revista o id_periodico"
            )

        # Validar que el material existe
        if id_libro:
            libro = self.db.query(Libro).filter(Libro.id == id_libro).first()
            if not libro:
                raise ValueError("El libro especificado no existe")
        elif id_revista:
            revista = self.db.query(Revista).filter(Revista.id == id_revista).first()
            if not revista:
                raise ValueError("La revista especificada no existe")
        elif id_periodico:
            periodico = (
                self.db.query(Periodico).filter(Periodico.id == id_periodico).first()
            )
            if not periodico:
                raise ValueError("El periódico especificado no existe")

        # Validar código de barras único si se proporciona
        if codigo_barras:
            if len(codigo_barras) > 50:
                raise ValueError("El código de barras no puede exceder 50 caracteres")
            existing = (
                self.db.query(Item)
                .filter(Item.codigo_barras == codigo_barras.strip())
                .first()
            )
            if existing:
                raise ValueError("Ya existe un item con ese código de barras")
            codigo_barras = codigo_barras.strip()

        # Validar estado_fisico
        estados_validos = ["bueno", "regular", "malo", "reparacion"]
        if estado_fisico not in estados_validos:
            raise ValueError(
                f"El estado físico debe ser uno de: {', '.join(estados_validos)}"
            )

        # Validar ubicacion
        if ubicacion and len(ubicacion) > 100:
            raise ValueError("La ubicación no puede exceder 100 caracteres")

        item = Item(
            id_libro=id_libro,
            id_revista=id_revista,
            id_periodico=id_periodico,
            codigo_barras=codigo_barras,
            ubicacion=ubicacion.strip() if ubicacion else None,
            estado_fisico=estado_fisico,
            disponible=disponible,
            observaciones=observaciones,
            id_usuario_creacion=id_usuario_creacion,
            id_usuario_edicion=id_usuario_creacion,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def obtener_items(
        self,
        skip: int = 0,
        limit: int = 1000,
        solo_disponibles: bool = False,
        id_libro: Optional[UUID] = None,
        id_revista: Optional[UUID] = None,
        id_periodico: Optional[UUID] = None,
    ) -> List[Item]:
        """Obtener todos los items con opciones de filtrado."""
        # Cargar relaciones explícitamente para evitar lazy loading
        try:
            query = self.db.query(Item).options(
                joinedload(Item.libro),
                joinedload(Item.revista),
                joinedload(Item.periodico),
            )
        except Exception:
            # Si joinedload falla, usar query simple
            query = self.db.query(Item)

        if solo_disponibles:
            query = query.filter(Item.disponible == True)

        if id_libro:
            query = query.filter(Item.id_libro == id_libro)
        elif id_revista:
            query = query.filter(Item.id_revista == id_revista)
        elif id_periodico:
            query = query.filter(Item.id_periodico == id_periodico)

        return query.offset(skip).limit(limit).all()

    def obtener_item(self, item_id: UUID) -> Optional[Item]:
        """Obtener un item por ID."""
        return (
            self.db.query(Item)
            .options(
                joinedload(Item.libro),
                joinedload(Item.revista),
                joinedload(Item.periodico),
            )
            .filter(Item.id == item_id)
            .first()
        )

    def obtener_items_por_material(
        self,
        tipo: str,
        material_id: UUID,
        solo_disponibles: bool = False,
    ) -> List[Item]:
        """Obtener todos los items de un material específico."""
        if tipo == "libro":
            return self.obtener_items(
                id_libro=material_id, solo_disponibles=solo_disponibles
            )
        elif tipo == "revista":
            return self.obtener_items(
                id_revista=material_id, solo_disponibles=solo_disponibles
            )
        elif tipo == "periodico":
            return self.obtener_items(
                id_periodico=material_id, solo_disponibles=solo_disponibles
            )
        else:
            raise ValueError("Tipo inválido. Debe ser: libro, revista o periodico")

    def actualizar_item(
        self, item_id: UUID, id_usuario_edicion: UUID, **kwargs
    ) -> Optional[Item]:
        """Actualizar un item."""
        item = self.obtener_item(item_id)
        if not item:
            return None

        # Validar que no se intente cambiar el tipo de material
        if any(k in kwargs for k in ["id_libro", "id_revista", "id_periodico"]):
            raise ValueError(
                "No se puede cambiar el tipo de material de un item existente"
            )

        # Validar código de barras único si se proporciona
        if "codigo_barras" in kwargs and kwargs["codigo_barras"]:
            codigo_barras = kwargs["codigo_barras"]
            if len(codigo_barras) > 50:
                raise ValueError("El código de barras no puede exceder 50 caracteres")
            existing = (
                self.db.query(Item)
                .filter(Item.codigo_barras == codigo_barras.strip(), Item.id != item_id)
                .first()
            )
            if existing:
                raise ValueError("Ya existe un item con ese código de barras")
            kwargs["codigo_barras"] = codigo_barras.strip()

        # Validar estado_fisico
        if "estado_fisico" in kwargs:
            estados_validos = ["bueno", "regular", "malo", "reparacion"]
            if kwargs["estado_fisico"] not in estados_validos:
                raise ValueError(
                    f"El estado físico debe ser uno de: {', '.join(estados_validos)}"
                )

        # Validar ubicacion
        if "ubicacion" in kwargs and kwargs["ubicacion"]:
            if len(kwargs["ubicacion"]) > 100:
                raise ValueError("La ubicación no puede exceder 100 caracteres")
            kwargs["ubicacion"] = kwargs["ubicacion"].strip()

        item.id_usuario_edicion = id_usuario_edicion

        for key, value in kwargs.items():
            if hasattr(item, key):
                setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def eliminar_item(self, item_id: UUID) -> bool:
        """Eliminar un item."""
        item = self.obtener_item(item_id)
        if item:
            self.db.delete(item)
            self.db.commit()
            return True
        return False
