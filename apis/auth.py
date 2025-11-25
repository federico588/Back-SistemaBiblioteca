import os
from datetime import datetime, timedelta
from uuid import UUID

from crud.usuario_crud import UsuarioCRUD
from database.config import get_db
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from schemas import LoginResponse, RespuestaAPI, UsuarioLogin
from sqlalchemy.orm import Session
from utils.error_handler import APIErrorHandler

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "tu-secret-key-super-segura-cambiar-en-produccion")
ALGORITHM = "HS256"

router = APIRouter(prefix="/auth", tags=["autenticación"])


@router.post("/login", response_model=LoginResponse)
async def login(login_data: UsuarioLogin, db: Session = Depends(get_db)):
    """Autenticar un usuario con nombre de usuario/email y contraseña."""
    try:
        usuario_crud = UsuarioCRUD(db)
        usuario = usuario_crud.autenticar_usuario(
            login_data.nombre_usuario, login_data.contraseña
        )

        if not usuario:
            raise APIErrorHandler.authentication_error(
                "Credenciales incorrectas o usuario inactivo"
            )

        expire = datetime.utcnow() + timedelta(hours=24)
        token_data = {
            "sub": str(usuario.id),
            "email": usuario.email,
            "es_admin": usuario.es_admin,
            "exp": expire,
        }
        access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": str(usuario.id),
                "email": usuario.email,
                "nombre": usuario.nombre,
                "nombre_usuario": usuario.nombre_usuario,
                "es_admin": usuario.es_admin,
                "activo": usuario.activo,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise APIErrorHandler.server_error("autenticar usuario", str(e))
