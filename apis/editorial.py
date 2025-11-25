from typing import List
from uuid import UUID

from crud.editorial_crud import EditorialCRUD
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from schemas import EditorialCreate, EditorialResponse, EditorialUpdate, RespuestaAPI
from sqlalchemy.orm import Session
from utils.error_handler import APIErrorHandler

router = APIRouter(prefix="/editoriales", tags=["editoriales"])


@router.get("/", response_model=List[EditorialResponse])
async def obtener_editoriales(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Obtener todas las editoriales."""
    try:
        editorial_crud = EditorialCRUD(db)
        editoriales = editorial_crud.obtener_editoriales(skip=skip, limit=limit)
        return editoriales
    except Exception as e:
        raise APIErrorHandler.server_error("obtener editoriales", str(e))


@router.get("/{editorial_id}", response_model=EditorialResponse)
async def obtener_editorial(editorial_id: UUID, db: Session = Depends(get_db)):
    """Obtener una editorial por ID."""
    try:
        editorial_crud = EditorialCRUD(db)
        editorial = editorial_crud.obtener_editorial(editorial_id)
        if not editorial:
            raise APIErrorHandler.not_found_error("Editorial", str(editorial_id))
        return editorial
    except HTTPException:
        raise
    except Exception as e:
        raise APIErrorHandler.server_error("obtener editorial", str(e))


@router.post("/", response_model=EditorialResponse, status_code=status.HTTP_201_CREATED)
async def crear_editorial(
    editorial_data: EditorialCreate, db: Session = Depends(get_db)
):
    """Crear una nueva editorial."""
    try:
        editorial_crud = EditorialCRUD(db)
        editorial = editorial_crud.crear_editorial(
            nombre=editorial_data.nombre,
            direccion=editorial_data.direccion,
            telefono=editorial_data.telefono,
            id_usuario_creacion=editorial_data.id_usuario_creacion,
        )
        return editorial
    except ValueError as e:
        raise APIErrorHandler.validation_error(str(e))
    except Exception as e:
        raise APIErrorHandler.server_error("crear editorial", str(e))


@router.put("/{editorial_id}", response_model=EditorialResponse)
async def actualizar_editorial(
    editorial_id: UUID, editorial_data: EditorialUpdate, db: Session = Depends(get_db)
):
    """Actualizar una editorial existente."""
    try:
        editorial_crud = EditorialCRUD(db)
        editorial_existente = editorial_crud.obtener_editorial(editorial_id)
        if not editorial_existente:
            raise APIErrorHandler.not_found_error("Editorial", str(editorial_id))

        campos_actualizacion = {
            k: v
            for k, v in editorial_data.dict(exclude={"id_usuario_edicion"}).items()
            if v is not None
        }

        editorial_actualizada = editorial_crud.actualizar_editorial(
            editorial_id, editorial_data.id_usuario_edicion, **campos_actualizacion
        )
        return editorial_actualizada
    except HTTPException:
        raise
    except ValueError as e:
        raise APIErrorHandler.validation_error(str(e))
    except Exception as e:
        raise APIErrorHandler.server_error("actualizar editorial", str(e))


@router.delete(
    "/{editorial_id}", response_model=RespuestaAPI, status_code=status.HTTP_200_OK
)
async def eliminar_editorial(editorial_id: UUID, db: Session = Depends(get_db)):
    """Eliminar una editorial."""
    try:
        editorial_crud = EditorialCRUD(db)
        editorial_existente = editorial_crud.obtener_editorial(editorial_id)
        if not editorial_existente:
            raise APIErrorHandler.not_found_error("Editorial", str(editorial_id))

        eliminada = editorial_crud.eliminar_editorial(editorial_id)
        if eliminada:
            return RespuestaAPI(
                mensaje="Editorial eliminada exitosamente", success=True
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar editorial",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise APIErrorHandler.server_error("eliminar editorial", str(e))
