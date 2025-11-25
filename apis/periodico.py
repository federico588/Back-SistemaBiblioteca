from typing import List
from uuid import UUID

from crud.item_crud import ItemCRUD
from crud.periodico_crud import PeriodicoCRUD
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from schemas import (
    ItemResponse,
    PeriodicoCreate,
    PeriodicoResponse,
    PeriodicoUpdate,
    RespuestaAPI,
)
from sqlalchemy.orm import Session
from utils.error_handler import APIErrorHandler

router = APIRouter(prefix="/periodicos", tags=["periodicos"])


@router.get("/", response_model=List[PeriodicoResponse])
async def obtener_periodicos(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Obtener todos los periódicos."""
    try:
        periodico_crud = PeriodicoCRUD(db)
        periodicos = periodico_crud.obtener_periodicos(skip=skip, limit=limit)
        return periodicos
    except Exception as e:
        raise APIErrorHandler.server_error("obtener periódicos", str(e))


@router.get("/{periodico_id}", response_model=PeriodicoResponse)
async def obtener_periodico(periodico_id: UUID, db: Session = Depends(get_db)):
    """Obtener un periódico por ID."""
    try:
        periodico_crud = PeriodicoCRUD(db)
        periodico = periodico_crud.obtener_periodico(periodico_id)
        if not periodico:
            raise APIErrorHandler.not_found_error("Periódico", str(periodico_id))
        return periodico
    except HTTPException:
        raise
    except Exception as e:
        raise APIErrorHandler.server_error("obtener periódico", str(e))


@router.post("/", response_model=PeriodicoResponse, status_code=status.HTTP_201_CREATED)
async def crear_periodico(
    periodico_data: PeriodicoCreate, db: Session = Depends(get_db)
):
    """Crear un nuevo periódico."""
    try:
        periodico_crud = PeriodicoCRUD(db)
        periodico = periodico_crud.crear_periodico(
            titulo=periodico_data.titulo,
            fecha_publicacion=periodico_data.fecha_publicacion,
            id_editorial=periodico_data.id_editorial,
            id_autor=periodico_data.id_autor,
            id_categoria=periodico_data.id_categoria,
            id_usuario_creacion=periodico_data.id_usuario_creacion,
        )
        return periodico
    except ValueError as e:
        raise APIErrorHandler.validation_error(str(e))
    except Exception as e:
        raise APIErrorHandler.server_error("crear periódico", str(e))


@router.put("/{periodico_id}", response_model=PeriodicoResponse)
async def actualizar_periodico(
    periodico_id: UUID, periodico_data: PeriodicoUpdate, db: Session = Depends(get_db)
):
    """Actualizar un periódico existente."""
    try:
        periodico_crud = PeriodicoCRUD(db)
        periodico_existente = periodico_crud.obtener_periodico(periodico_id)
        if not periodico_existente:
            raise APIErrorHandler.not_found_error("Periódico", str(periodico_id))

        campos_actualizacion = {
            k: v
            for k, v in periodico_data.dict(exclude={"id_usuario_edicion"}).items()
            if v is not None
        }

        periodico_actualizado = periodico_crud.actualizar_periodico(
            periodico_id, periodico_data.id_usuario_edicion, **campos_actualizacion
        )
        return periodico_actualizado
    except HTTPException:
        raise
    except ValueError as e:
        raise APIErrorHandler.validation_error(str(e))
    except Exception as e:
        raise APIErrorHandler.server_error("actualizar periódico", str(e))


@router.delete(
    "/{periodico_id}", response_model=RespuestaAPI, status_code=status.HTTP_200_OK
)
async def eliminar_periodico(periodico_id: UUID, db: Session = Depends(get_db)):
    """Eliminar un periódico."""
    try:
        periodico_crud = PeriodicoCRUD(db)
        periodico_existente = periodico_crud.obtener_periodico(periodico_id)
        if not periodico_existente:
            raise APIErrorHandler.not_found_error("Periódico", str(periodico_id))

        eliminado = periodico_crud.eliminar_periodico(periodico_id)
        if eliminado:
            return RespuestaAPI(
                mensaje="Periódico eliminado exitosamente", success=True
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar periódico",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise APIErrorHandler.server_error("eliminar periódico", str(e))


@router.get("/{periodico_id}/items", response_model=List[ItemResponse])
async def obtener_items_periodico(
    periodico_id: UUID,
    solo_disponibles: bool = Query(False, description="Solo items disponibles"),
    db: Session = Depends(get_db),
):
    """Obtener todos los ejemplares (items) de un periódico."""
    try:
        periodico_crud = PeriodicoCRUD(db)
        periodico = periodico_crud.obtener_periodico(periodico_id)
        if not periodico:
            raise APIErrorHandler.not_found_error("Periódico", str(periodico_id))

        item_crud = ItemCRUD(db)
        items = item_crud.obtener_items_por_material(
            tipo="periodico",
            material_id=periodico_id,
            solo_disponibles=solo_disponibles,
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
                    "id": periodico.id,
                    "titulo": periodico.titulo,
                    "fecha_publicacion": periodico.fecha_publicacion,
                }
                if item.id_periodico
                else None,
            }
            items_response.append(item_dict)

        return items_response
    except HTTPException:
        raise
    except Exception as e:
        raise APIErrorHandler.server_error("obtener items del periódico", str(e))
