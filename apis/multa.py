from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from crud.multa_crud import MultaCRUD
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from schemas import MultaCreate, MultaPagar, MultaResponse, MultaUpdate, RespuestaAPI
from sqlalchemy.orm import Session
from utils.error_handler import APIErrorHandler

router = APIRouter(prefix="/multas", tags=["multas"])


@router.get("/", response_model=List[MultaResponse])
async def obtener_multas(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    id_usuario: Optional[UUID] = Query(None, description="Filtrar por usuario"),
    db: Session = Depends(get_db),
):
    """Obtener todas las multas."""
    try:
        multa_crud = MultaCRUD(db)
        multas = multa_crud.obtener_multas(
            skip=skip, limit=limit, estado=estado, id_usuario=id_usuario
        )
        return multas
    except Exception as e:
        raise APIErrorHandler.server_error("obtener multas", str(e))


@router.get("/{multa_id}", response_model=MultaResponse)
async def obtener_multa(multa_id: UUID, db: Session = Depends(get_db)):
    """Obtener una multa por ID."""
    try:
        multa_crud = MultaCRUD(db)
        multa = multa_crud.obtener_multa(multa_id)
        if not multa:
            raise APIErrorHandler.not_found_error("Multa", str(multa_id))
        return multa
    except HTTPException:
        raise
    except Exception as e:
        raise APIErrorHandler.server_error("obtener multa", str(e))


@router.post("/", response_model=MultaResponse, status_code=status.HTTP_201_CREATED)
async def crear_multa(multa_data: MultaCreate, db: Session = Depends(get_db)):
    """Crear una nueva multa."""
    try:
        multa_crud = MultaCRUD(db)
        multa = multa_crud.crear_multa(
            id_prestamo=multa_data.id_prestamo,
            id_usuario=multa_data.id_usuario,
            monto=multa_data.monto,
            motivo=multa_data.motivo,
            id_usuario_creacion=multa_data.id_usuario_creacion,
        )
        return multa
    except ValueError as e:
        raise APIErrorHandler.validation_error(str(e))
    except Exception as e:
        raise APIErrorHandler.server_error("crear multa", str(e))


@router.put("/{multa_id}", response_model=MultaResponse)
async def actualizar_multa(
    multa_id: UUID, multa_data: MultaUpdate, db: Session = Depends(get_db)
):
    """Actualizar una multa existente."""
    try:
        multa_crud = MultaCRUD(db)
        multa_existente = multa_crud.obtener_multa(multa_id)
        if not multa_existente:
            raise APIErrorHandler.not_found_error("Multa", str(multa_id))

        campos_actualizacion = {
            k: v
            for k, v in multa_data.dict(exclude={"id_usuario_edicion"}).items()
            if v is not None
        }

        multa_actualizada = multa_crud.actualizar_multa(
            multa_id, multa_data.id_usuario_edicion, **campos_actualizacion
        )
        return multa_actualizada
    except HTTPException:
        raise
    except ValueError as e:
        raise APIErrorHandler.validation_error(str(e))
    except Exception as e:
        raise APIErrorHandler.server_error("actualizar multa", str(e))


@router.post("/{multa_id}/pagar", response_model=MultaResponse)
async def pagar_multa(
    multa_id: UUID, request_data: MultaPagar, db: Session = Depends(get_db)
):
    """Marcar una multa como pagada."""
    try:
        if not request_data.id_usuario_edicion:
            raise APIErrorHandler.validation_error(
                "El campo id_usuario_edicion es obligatorio"
            )

        multa_crud = MultaCRUD(db)
        multa = multa_crud.pagar_multa(multa_id, request_data.id_usuario_edicion)
        if not multa:
            raise APIErrorHandler.not_found_error("Multa", str(multa_id))
        return multa
    except HTTPException:
        raise
    except ValueError as e:
        raise APIErrorHandler.validation_error(str(e))
    except Exception as e:
        raise APIErrorHandler.server_error("pagar multa", str(e))


@router.delete(
    "/{multa_id}", response_model=RespuestaAPI, status_code=status.HTTP_200_OK
)
async def eliminar_multa(multa_id: UUID, db: Session = Depends(get_db)):
    """Eliminar una multa."""
    try:
        multa_crud = MultaCRUD(db)
        multa_existente = multa_crud.obtener_multa(multa_id)
        if not multa_existente:
            raise APIErrorHandler.not_found_error("Multa", str(multa_id))

        eliminada = multa_crud.eliminar_multa(multa_id)
        if eliminada:
            return RespuestaAPI(mensaje="Multa eliminada exitosamente", success=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar multa",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise APIErrorHandler.server_error("eliminar multa", str(e))
