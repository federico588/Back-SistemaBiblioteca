from typing import List
from uuid import UUID

from crud.item_crud import ItemCRUD
from crud.libro_crud import LibroCRUD
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from schemas import ItemResponse, LibroCreate, LibroResponse, LibroUpdate, RespuestaAPI
from sqlalchemy.orm import Session
from utils.error_handler import APIErrorHandler

router = APIRouter(prefix="/libros", tags=["libros"])


@router.get("/", response_model=List[LibroResponse])
async def obtener_libros(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Obtener todos los libros."""
    try:
        libro_crud = LibroCRUD(db)
        libros = libro_crud.obtener_libros(skip=skip, limit=limit)
        return libros
    except Exception as e:
        raise APIErrorHandler.server_error("obtener libros", str(e))


@router.get("/{libro_id}", response_model=LibroResponse)
async def obtener_libro(libro_id: UUID, db: Session = Depends(get_db)):
    """Obtener un libro por ID."""
    try:
        libro_crud = LibroCRUD(db)
        libro = libro_crud.obtener_libro(libro_id)
        if not libro:
            raise APIErrorHandler.not_found_error("Libro", str(libro_id))
        return libro
    except HTTPException:
        raise
    except Exception as e:
        raise APIErrorHandler.server_error("obtener libro", str(e))


@router.post("/", response_model=LibroResponse, status_code=status.HTTP_201_CREATED)
async def crear_libro(libro_data: LibroCreate, db: Session = Depends(get_db)):
    """Crear un nuevo libro."""
    try:
        libro_crud = LibroCRUD(db)
        libro = libro_crud.crear_libro(
            titulo=libro_data.titulo,
            isbn=libro_data.isbn,
            numero_paginas=libro_data.numero_paginas,
            id_editorial=libro_data.id_editorial,
            id_autor=libro_data.id_autor,
            id_categoria=libro_data.id_categoria,
            id_usuario_creacion=libro_data.id_usuario_creacion,
        )
        return libro
    except ValueError as e:
        raise APIErrorHandler.validation_error(str(e))
    except Exception as e:
        raise APIErrorHandler.server_error("crear libro", str(e))


@router.put("/{libro_id}", response_model=LibroResponse)
async def actualizar_libro(
    libro_id: UUID, libro_data: LibroUpdate, db: Session = Depends(get_db)
):
    """Actualizar un libro existente."""
    try:
        libro_crud = LibroCRUD(db)
        libro_existente = libro_crud.obtener_libro(libro_id)
        if not libro_existente:
            raise APIErrorHandler.not_found_error("Libro", str(libro_id))

        campos_actualizacion = {
            k: v
            for k, v in libro_data.dict(exclude={"id_usuario_edicion"}).items()
            if v is not None
        }

        libro_actualizado = libro_crud.actualizar_libro(
            libro_id, libro_data.id_usuario_edicion, **campos_actualizacion
        )
        return libro_actualizado
    except HTTPException:
        raise
    except ValueError as e:
        raise APIErrorHandler.validation_error(str(e))
    except Exception as e:
        raise APIErrorHandler.server_error("actualizar libro", str(e))


@router.delete(
    "/{libro_id}", response_model=RespuestaAPI, status_code=status.HTTP_200_OK
)
async def eliminar_libro(libro_id: UUID, db: Session = Depends(get_db)):
    """Eliminar un libro."""
    try:
        libro_crud = LibroCRUD(db)
        libro_existente = libro_crud.obtener_libro(libro_id)
        if not libro_existente:
            raise APIErrorHandler.not_found_error("Libro", str(libro_id))

        eliminado = libro_crud.eliminar_libro(libro_id)
        if eliminado:
            return RespuestaAPI(mensaje="Libro eliminado exitosamente", success=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar libro",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise APIErrorHandler.server_error("eliminar libro", str(e))


@router.get("/{libro_id}/items", response_model=List[ItemResponse])
async def obtener_items_libro(
    libro_id: UUID,
    solo_disponibles: bool = Query(False, description="Solo items disponibles"),
    db: Session = Depends(get_db),
):
    """Obtener todos los ejemplares (items) de un libro."""
    try:
        libro_crud = LibroCRUD(db)
        libro = libro_crud.obtener_libro(libro_id)
        if not libro:
            raise APIErrorHandler.not_found_error("Libro", str(libro_id))

        item_crud = ItemCRUD(db)
        items = item_crud.obtener_items_por_material(
            tipo="libro", material_id=libro_id, solo_disponibles=solo_disponibles
        )

        # Enriquecer con información del material
        items_response = []
        for item in items:
            item_dict = {
                "id": item.id,
                "id_libro": item.id_libro,
                "id_revista": item.id_revista,
                "id_periodico": item.id_periodico,
                "tipo_item": item.tipo_item,
                "codigo_barras": item.codigo_barras,
                "ubicacion": item.ubicacion,
                "estado_fisico": item.estado_fisico,
                "disponible": item.disponible,
                "observaciones": item.observaciones,
                "fecha_creacion": item.fecha_creacion,
                "fecha_actualizacion": item.fecha_actualizacion,
                "material": {
                    "id": libro.id,
                    "titulo": libro.titulo,
                    "isbn": libro.isbn,
                }
                if item.id_libro
                else None,
            }
            items_response.append(item_dict)

        return items_response
    except HTTPException:
        raise
    except Exception as e:
        raise APIErrorHandler.server_error("obtener items del libro", str(e))
