from typing import List
from uuid import UUID

from crud.autor_crud import AutorCRUD
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from schemas import AutorCreate, AutorResponse, AutorUpdate, RespuestaAPI
from sqlalchemy.orm import Session
from utils.error_handler import APIErrorHandler

router = APIRouter(prefix="/autores", tags=["autores"])


@router.get("/", response_model=List[AutorResponse])
async def obtener_autores(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Obtener todos los autores."""
    try:
        autor_crud = AutorCRUD(db)
        autores = autor_crud.obtener_autores(skip=skip, limit=limit)
        return autores
    except Exception as e:
        raise APIErrorHandler.server_error("obtener autores", str(e))


@router.get("/{autor_id}", response_model=AutorResponse)
async def obtener_autor(autor_id: UUID, db: Session = Depends(get_db)):
    """Obtener un autor por ID."""
    try:
        autor_crud = AutorCRUD(db)
        autor = autor_crud.obtener_autor(autor_id)
        if not autor:
            raise APIErrorHandler.not_found_error("Autor", str(autor_id))
        return autor
    except HTTPException:
        raise
    except Exception as e:
        raise APIErrorHandler.server_error("obtener autor", str(e))


@router.post("/", response_model=AutorResponse, status_code=status.HTTP_201_CREATED)
async def crear_autor(autor_data: AutorCreate, db: Session = Depends(get_db)):
    """Crear un nuevo autor."""
    try:
        autor_crud = AutorCRUD(db)
        autor = autor_crud.crear_autor(
            nombre=autor_data.nombre,
            nacionalidad=autor_data.nacionalidad,
            bibliografia=autor_data.bibliografia,
            id_usuario_creacion=autor_data.id_usuario_creacion,
        )
        return autor
    except ValueError as e:
        raise APIErrorHandler.validation_error(str(e))
    except Exception as e:
        raise APIErrorHandler.server_error("crear autor", str(e))


@router.put("/{autor_id}", response_model=AutorResponse)
async def actualizar_autor(
    autor_id: UUID, autor_data: AutorUpdate, db: Session = Depends(get_db)
):
    """Actualizar un autor existente."""
    try:
        autor_crud = AutorCRUD(db)
        autor_existente = autor_crud.obtener_autor(autor_id)
        if not autor_existente:
            raise APIErrorHandler.not_found_error("Autor", str(autor_id))

        campos_actualizacion = {
            k: v
            for k, v in autor_data.dict(exclude={"id_usuario_edicion"}).items()
            if v is not None
        }

        autor_actualizado = autor_crud.actualizar_autor(
            autor_id, autor_data.id_usuario_edicion, **campos_actualizacion
        )
        return autor_actualizado
    except HTTPException:
        raise
    except ValueError as e:
        raise APIErrorHandler.validation_error(str(e))
    except Exception as e:
        raise APIErrorHandler.server_error("actualizar autor", str(e))


@router.delete(
    "/{autor_id}", response_model=RespuestaAPI, status_code=status.HTTP_200_OK
)
async def eliminar_autor(autor_id: UUID, db: Session = Depends(get_db)):
    """Eliminar un autor."""
    try:
        autor_crud = AutorCRUD(db)
        autor_existente = autor_crud.obtener_autor(autor_id)
        if not autor_existente:
            raise APIErrorHandler.not_found_error("Autor", str(autor_id))

        eliminado = autor_crud.eliminar_autor(autor_id)
        if eliminado:
            return RespuestaAPI(mensaje="Autor eliminado exitosamente", success=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar autor",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise APIErrorHandler.server_error("eliminar autor", str(e))
