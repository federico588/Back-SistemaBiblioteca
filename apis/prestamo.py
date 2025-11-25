from typing import List, Optional
from uuid import UUID

from crud.prestamo_crud import PrestamoCRUD
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from schemas import (
    PrestamoCreate,
    PrestamoDevolver,
    PrestamoResponse,
    PrestamoUpdate,
    RespuestaAPI,
)
from sqlalchemy.orm import Session
from utils.error_handler import APIErrorHandler

router = APIRouter(prefix="/prestamos", tags=["prestamos"])


@router.get("/", response_model=List[PrestamoResponse])
async def obtener_prestamos(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    id_usuario: Optional[UUID] = Query(None, description="Filtrar por usuario"),
    db: Session = Depends(get_db),
):
    """Obtener todos los préstamos."""
    try:
        prestamo_crud = PrestamoCRUD(db)
        prestamos = prestamo_crud.obtener_prestamos(
            skip=skip, limit=limit, estado=estado, id_usuario=id_usuario
        )
        return prestamos
    except Exception as e:
        raise APIErrorHandler.server_error("obtener préstamos", str(e))


@router.get("/{prestamo_id}", response_model=PrestamoResponse)
async def obtener_prestamo(prestamo_id: UUID, db: Session = Depends(get_db)):
    """Obtener un préstamo por ID."""
    try:
        prestamo_crud = PrestamoCRUD(db)
        prestamo = prestamo_crud.obtener_prestamo(prestamo_id)
        if not prestamo:
            raise APIErrorHandler.not_found_error("Préstamo", str(prestamo_id))
        return prestamo
    except HTTPException:
        raise
    except Exception as e:
        raise APIErrorHandler.server_error("obtener préstamo", str(e))


@router.post("/", response_model=PrestamoResponse, status_code=status.HTTP_201_CREATED)
async def crear_prestamo(prestamo_data: PrestamoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo préstamo."""
    try:
        prestamo_crud = PrestamoCRUD(db)
        prestamo = prestamo_crud.crear_prestamo(
            id_item=prestamo_data.id_item,
            id_usuario=prestamo_data.id_usuario,
            id_usuario_creacion=prestamo_data.id_usuario_creacion,
            fecha_devolucion_estimada=prestamo_data.fecha_devolucion_estimada,
        )
        return prestamo
    except ValueError as e:
        raise APIErrorHandler.validation_error(str(e))
    except Exception as e:
        raise APIErrorHandler.server_error("crear préstamo", str(e))


@router.put("/{prestamo_id}", response_model=PrestamoResponse)
async def actualizar_prestamo(
    prestamo_id: UUID, prestamo_data: PrestamoUpdate, db: Session = Depends(get_db)
):
    """Actualizar un préstamo existente."""
    try:
        prestamo_crud = PrestamoCRUD(db)
        prestamo_existente = prestamo_crud.obtener_prestamo(prestamo_id)
        if not prestamo_existente:
            raise APIErrorHandler.not_found_error("Préstamo", str(prestamo_id))

        campos_actualizacion = {
            k: v
            for k, v in prestamo_data.dict(exclude={"id_usuario_edicion"}).items()
            if v is not None
        }

        prestamo_actualizado = prestamo_crud.actualizar_prestamo(
            prestamo_id, prestamo_data.id_usuario_edicion, **campos_actualizacion
        )
        return prestamo_actualizado
    except HTTPException:
        raise
    except ValueError as e:
        raise APIErrorHandler.validation_error(str(e))
    except Exception as e:
        raise APIErrorHandler.server_error("actualizar préstamo", str(e))


@router.post("/{prestamo_id}/devolver", response_model=PrestamoResponse)
async def devolver_prestamo(
    prestamo_id: UUID, request_data: PrestamoDevolver, db: Session = Depends(get_db)
):
    """Marcar un préstamo como devuelto."""
    try:
        if not request_data.id_usuario_edicion:
            raise APIErrorHandler.validation_error(
                "El campo id_usuario_edicion es obligatorio"
            )

        prestamo_crud = PrestamoCRUD(db)
        prestamo = prestamo_crud.devolver_prestamo(
            prestamo_id, request_data.id_usuario_edicion
        )
        if not prestamo:
            raise APIErrorHandler.not_found_error("Préstamo", str(prestamo_id))
        return prestamo
    except HTTPException:
        raise
    except ValueError as e:
        raise APIErrorHandler.validation_error(str(e))
    except Exception as e:
        raise APIErrorHandler.server_error("devolver préstamo", str(e))


@router.delete(
    "/{prestamo_id}", response_model=RespuestaAPI, status_code=status.HTTP_200_OK
)
async def eliminar_prestamo(prestamo_id: UUID, db: Session = Depends(get_db)):
    """Eliminar un préstamo."""
    try:
        prestamo_crud = PrestamoCRUD(db)
        prestamo_existente = prestamo_crud.obtener_prestamo(prestamo_id)
        if not prestamo_existente:
            raise APIErrorHandler.not_found_error("Préstamo", str(prestamo_id))

        eliminado = prestamo_crud.eliminar_prestamo(prestamo_id)
        if eliminado:
            return RespuestaAPI(mensaje="Préstamo eliminado exitosamente", success=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar préstamo",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise APIErrorHandler.server_error("eliminar préstamo", str(e))
