from typing import List
from uuid import UUID

from crud.item_crud import ItemCRUD
from crud.revista_crud import RevistaCRUD
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from schemas import (
    ItemResponse,
    RespuestaAPI,
    RevistaCreate,
    RevistaResponse,
    RevistaUpdate,
)
from sqlalchemy.orm import Session
from utils.error_handler import APIErrorHandler

router = APIRouter(prefix="/revistas", tags=["revistas"])


@router.get("/", response_model=List[RevistaResponse])
async def obtener_revistas(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Obtener todas las revistas."""
    try:
        revista_crud = RevistaCRUD(db)
        revistas = revista_crud.obtener_revistas(skip=skip, limit=limit)
        return revistas
    except Exception as e:
        raise APIErrorHandler.server_error("obtener revistas", str(e))


@router.get("/{revista_id}", response_model=RevistaResponse)
async def obtener_revista(revista_id: UUID, db: Session = Depends(get_db)):
    """Obtener una revista por ID."""
    try:
        revista_crud = RevistaCRUD(db)
        revista = revista_crud.obtener_revista(revista_id)
        if not revista:
            raise APIErrorHandler.not_found_error("Revista", str(revista_id))
        return revista
    except HTTPException:
        raise
    except Exception as e:
        raise APIErrorHandler.server_error("obtener revista", str(e))


@router.post("/", response_model=RevistaResponse, status_code=status.HTTP_201_CREATED)
async def crear_revista(revista_data: RevistaCreate, db: Session = Depends(get_db)):
    """Crear una nueva revista."""
    try:
        revista_crud = RevistaCRUD(db)
        revista = revista_crud.crear_revista(
            titulo=revista_data.titulo,
            numero_publicacion=revista_data.numero_publicacion,
            id_editorial=revista_data.id_editorial,
            id_autor=revista_data.id_autor,
            id_categoria=revista_data.id_categoria,
            id_usuario_creacion=revista_data.id_usuario_creacion,
        )
        return revista
    except ValueError as e:
        raise APIErrorHandler.validation_error(str(e))
    except Exception as e:
        raise APIErrorHandler.server_error("crear revista", str(e))


@router.put("/{revista_id}", response_model=RevistaResponse)
async def actualizar_revista(
    revista_id: UUID, revista_data: RevistaUpdate, db: Session = Depends(get_db)
):
    """Actualizar una revista existente."""
    try:
        revista_crud = RevistaCRUD(db)
        revista_existente = revista_crud.obtener_revista(revista_id)
        if not revista_existente:
            raise APIErrorHandler.not_found_error("Revista", str(revista_id))

        campos_actualizacion = {
            k: v
            for k, v in revista_data.dict(exclude={"id_usuario_edicion"}).items()
            if v is not None
        }

        revista_actualizada = revista_crud.actualizar_revista(
            revista_id, revista_data.id_usuario_edicion, **campos_actualizacion
        )
        return revista_actualizada
    except HTTPException:
        raise
    except ValueError as e:
        raise APIErrorHandler.validation_error(str(e))
    except Exception as e:
        raise APIErrorHandler.server_error("actualizar revista", str(e))


@router.delete(
    "/{revista_id}", response_model=RespuestaAPI, status_code=status.HTTP_200_OK
)
async def eliminar_revista(revista_id: UUID, db: Session = Depends(get_db)):
    """Eliminar una revista."""
    try:
        revista_crud = RevistaCRUD(db)
        revista_existente = revista_crud.obtener_revista(revista_id)
        if not revista_existente:
            raise APIErrorHandler.not_found_error("Revista", str(revista_id))

        eliminada = revista_crud.eliminar_revista(revista_id)
        if eliminada:
            return RespuestaAPI(mensaje="Revista eliminada exitosamente", success=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar revista",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise APIErrorHandler.server_error("eliminar revista", str(e))


@router.get("/{revista_id}/items", response_model=List[ItemResponse])
async def obtener_items_revista(
    revista_id: UUID,
    solo_disponibles: bool = Query(False, description="Solo items disponibles"),
    db: Session = Depends(get_db),
):
    """Obtener todos los ejemplares (items) de una revista."""
    try:
        revista_crud = RevistaCRUD(db)
        revista = revista_crud.obtener_revista(revista_id)
        if not revista:
            raise APIErrorHandler.not_found_error("Revista", str(revista_id))

        item_crud = ItemCRUD(db)
        items = item_crud.obtener_items_por_material(
            tipo="revista", material_id=revista_id, solo_disponibles=solo_disponibles
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
                    "id": revista.id,
                    "titulo": revista.titulo,
                    "numero_publicacion": revista.numero_publicacion,
                }
                if item.id_revista
                else None,
            }
            items_response.append(item_dict)

        return items_response
    except HTTPException:
        raise
    except Exception as e:
        raise APIErrorHandler.server_error("obtener items de la revista", str(e))
