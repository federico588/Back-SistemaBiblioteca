from typing import List
from uuid import UUID

from crud.usuario_crud import UsuarioCRUD
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from schemas import RespuestaAPI, UsuarioCreate, UsuarioResponse, UsuarioUpdate
from sqlalchemy.orm import Session
from utils.error_handler import APIErrorHandler

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("/", response_model=List[UsuarioResponse])
async def obtener_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    include_inactive: bool = Query(False, description="Incluir usuarios inactivos"),
    db: Session = Depends(get_db),
):
    """Obtener todos los usuarios con paginación."""
    try:
        usuario_crud = UsuarioCRUD(db)
        usuarios = usuario_crud.obtener_usuarios(
            skip=skip, limit=limit, include_inactive=include_inactive
        )
        if not usuarios:
            return []
        return usuarios
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuarios: {str(e)}",
        )


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def obtener_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    """Obtener un usuario por ID."""
    try:
        usuario_crud = UsuarioCRUD(db)
        usuario = usuario_crud.obtener_usuario(usuario_id)
        if not usuario:
            raise APIErrorHandler.not_found_error("Usuario", str(usuario_id))
        return usuario
    except HTTPException:
        raise
    except Exception as e:
        raise APIErrorHandler.server_error("obtener usuario", str(e))


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario_data: UsuarioCreate, db: Session = Depends(get_db)):
    """Crear un nuevo usuario."""
    try:
        usuario_crud = UsuarioCRUD(db)
        usuario = usuario_crud.crear_usuario(
            nombre=usuario_data.nombre,
            nombre_usuario=usuario_data.nombre_usuario,
            email=usuario_data.email,
            contraseña=usuario_data.contraseña,
            id_usuario_creacion=usuario_data.id_usuario_creacion,
            telefono=usuario_data.telefono,
            es_admin=usuario_data.es_admin,
        )
        return usuario
    except ValueError as e:
        error_message = str(e)
        if "nombre de usuario ya está registrado" in error_message:
            raise APIErrorHandler.duplicate_error(
                "usuario", "nombre de usuario", usuario_data.nombre_usuario
            )
        elif "email ya está registrado" in error_message:
            raise APIErrorHandler.duplicate_error(
                "usuario", "email", usuario_data.email
            )
        else:
            raise APIErrorHandler.validation_error(error_message)
    except Exception as e:
        raise APIErrorHandler.server_error("crear usuario", str(e))


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def actualizar_usuario(
    usuario_id: UUID, usuario_data: UsuarioUpdate, db: Session = Depends(get_db)
):
    """Actualizar un usuario existente."""
    try:
        usuario_crud = UsuarioCRUD(db)
        usuario_existente = usuario_crud.obtener_usuario(usuario_id)
        if not usuario_existente:
            raise APIErrorHandler.not_found_error("Usuario", str(usuario_id))

        campos_actualizacion = {
            k: v
            for k, v in usuario_data.dict(exclude={"id_usuario_edicion"}).items()
            if v is not None
        }

        if not campos_actualizacion and not usuario_data.id_usuario_edicion:
            return usuario_existente

        usuario_actualizado = usuario_crud.actualizar_usuario(
            usuario_id,
            usuario_data.id_usuario_edicion,
            **campos_actualizacion,
        )
        return usuario_actualizado
    except HTTPException:
        raise
    except ValueError as e:
        raise APIErrorHandler.validation_error(str(e))
    except Exception as e:
        raise APIErrorHandler.server_error("actualizar usuario", str(e))


@router.delete(
    "/{usuario_id}", response_model=RespuestaAPI, status_code=status.HTTP_200_OK
)
async def eliminar_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    """Eliminar un usuario (soft delete)."""
    try:
        usuario_crud = UsuarioCRUD(db)
        usuario_existente = usuario_crud.obtener_usuario(usuario_id)
        if not usuario_existente:
            raise APIErrorHandler.not_found_error("Usuario", str(usuario_id))

        eliminado = usuario_crud.eliminar_usuario(usuario_id)
        if eliminado:
            return RespuestaAPI(mensaje="Usuario eliminado exitosamente", success=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar usuario",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise APIErrorHandler.server_error("eliminar usuario", str(e))
