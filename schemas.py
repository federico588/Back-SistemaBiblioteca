from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UsuarioBase(BaseModel):
    nombre: str
    nombre_usuario: str
    email: EmailStr
    telefono: Optional[str] = None
    es_admin: bool = False


class UsuarioCreate(UsuarioBase):
    contraseña: str
    id_usuario_creacion: Optional[UUID] = None


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    nombre_usuario: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    es_admin: Optional[bool] = None
    activo: Optional[bool] = None
    id_usuario_edicion: Optional[UUID] = None


class UsuarioResponse(UsuarioBase):
    id: UUID
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class UsuarioLogin(BaseModel):
    nombre_usuario: str
    contraseña: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class CambioContraseña(BaseModel):
    contraseña_actual: str
    nueva_contraseña: str


class AutorBase(BaseModel):
    nombre: str
    nacionalidad: str
    bibliografia: Optional[str] = None


class AutorCreate(AutorBase):
    id_usuario_creacion: UUID


class AutorUpdate(BaseModel):
    nombre: Optional[str] = None
    nacionalidad: Optional[str] = None
    bibliografia: Optional[str] = None
    id_usuario_edicion: UUID


class AutorResponse(AutorBase):
    id: UUID
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class EditorialBase(BaseModel):
    nombre: str
    direccion: Optional[str] = None
    telefono: Optional[str] = None


class EditorialCreate(EditorialBase):
    id_usuario_creacion: UUID


class EditorialUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    id_usuario_edicion: UUID


class EditorialResponse(EditorialBase):
    id: UUID
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class CategoriaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class CategoriaCreate(CategoriaBase):
    id_usuario_creacion: UUID


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    id_usuario_edicion: UUID


class CategoriaResponse(CategoriaBase):
    id: UUID
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class LibroBase(BaseModel):
    titulo: str
    isbn: Optional[str] = None
    numero_paginas: Optional[str] = None
    id_editorial: UUID
    id_autor: Optional[
        UUID
    ] = None  # Temporalmente opcional para libros existentes sin autor
    id_categoria: Optional[UUID] = None


class LibroCreate(LibroBase):
    id_autor: UUID  # Obligatorio para creación
    id_usuario_creacion: UUID


class LibroUpdate(BaseModel):
    titulo: Optional[str] = None
    isbn: Optional[str] = None
    numero_paginas: Optional[str] = None
    id_editorial: Optional[UUID] = None
    id_autor: Optional[UUID] = None
    id_categoria: Optional[UUID] = None
    id_usuario_edicion: UUID


class LibroResponse(LibroBase):
    id: UUID
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class RevistaBase(BaseModel):
    titulo: str
    numero_publicacion: Optional[str] = None
    id_editorial: UUID
    id_autor: Optional[
        UUID
    ] = None  # Temporalmente opcional para revistas existentes sin autor
    id_categoria: Optional[UUID] = None


class RevistaCreate(RevistaBase):
    id_autor: UUID  # Obligatorio para creación
    id_usuario_creacion: UUID


class RevistaUpdate(BaseModel):
    titulo: Optional[str] = None
    numero_publicacion: Optional[str] = None
    id_editorial: Optional[UUID] = None
    id_autor: Optional[UUID] = None
    id_categoria: Optional[UUID] = None
    id_usuario_edicion: UUID


class RevistaResponse(RevistaBase):
    id: UUID
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class PeriodicoBase(BaseModel):
    titulo: str
    fecha_publicacion: datetime
    id_editorial: UUID
    id_autor: Optional[
        UUID
    ] = None  # Temporalmente opcional para periódicos existentes sin autor
    id_categoria: Optional[UUID] = None


class PeriodicoCreate(PeriodicoBase):
    id_autor: UUID  # Obligatorio para creación
    id_usuario_creacion: UUID


class PeriodicoUpdate(BaseModel):
    titulo: Optional[str] = None
    fecha_publicacion: Optional[datetime] = None
    id_editorial: Optional[UUID] = None
    id_autor: Optional[UUID] = None
    id_categoria: Optional[UUID] = None
    id_usuario_edicion: UUID


class PeriodicoResponse(PeriodicoBase):
    id: UUID
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class ItemCreate(BaseModel):
    id_libro: Optional[UUID] = None
    id_revista: Optional[UUID] = None
    id_periodico: Optional[UUID] = None
    codigo_barras: Optional[str] = None
    ubicacion: Optional[str] = None
    estado_fisico: Optional[str] = "bueno"
    disponible: bool = True
    observaciones: Optional[str] = None
    id_usuario_creacion: UUID


class ItemUpdate(BaseModel):
    id_libro: Optional[UUID] = None
    id_revista: Optional[UUID] = None
    id_periodico: Optional[UUID] = None
    codigo_barras: Optional[str] = None
    ubicacion: Optional[str] = None
    estado_fisico: Optional[str] = None
    disponible: Optional[bool] = None
    observaciones: Optional[str] = None
    id_usuario_edicion: UUID


class ItemResponse(BaseModel):
    id: UUID
    id_libro: Optional[UUID] = None
    id_revista: Optional[UUID] = None
    id_periodico: Optional[UUID] = None
    tipo_item: str  # Calculado: "libro", "revista", "periodico"
    codigo_barras: Optional[str] = None
    ubicacion: Optional[str] = None
    estado_fisico: str
    disponible: bool
    observaciones: Optional[str] = None
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    # Información del material asociado (se poblará en el endpoint)
    material: Optional[dict] = None

    class Config:
        from_attributes = True


class PrestamoBase(BaseModel):
    id_item: UUID
    id_usuario: UUID
    fecha_devolucion_estimada: datetime


class PrestamoCreate(BaseModel):
    id_item: UUID
    id_usuario: UUID
    id_usuario_creacion: UUID
    fecha_devolucion_estimada: Optional[datetime] = None


class PrestamoUpdate(BaseModel):
    fecha_devolucion_estimada: Optional[datetime] = None
    fecha_devolucion_real: Optional[datetime] = None
    estado: Optional[str] = None
    id_usuario_edicion: UUID


class PrestamoDevolver(BaseModel):
    id_usuario_edicion: UUID


class MultaPagar(BaseModel):
    id_usuario_edicion: UUID


class PrestamoResponse(PrestamoBase):
    id: UUID
    fecha_prestamo: datetime
    fecha_devolucion_real: Optional[datetime] = None
    estado: str
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class MultaBase(BaseModel):
    id_prestamo: UUID
    id_usuario: UUID
    monto: Decimal
    motivo: Optional[str] = None


class MultaCreate(MultaBase):
    id_usuario_creacion: UUID


class MultaUpdate(BaseModel):
    monto: Optional[Decimal] = None
    motivo: Optional[str] = None
    fecha_pago: Optional[datetime] = None
    estado: Optional[str] = None
    id_usuario_edicion: UUID


class MultaResponse(MultaBase):
    id: UUID
    fecha_multa: datetime
    fecha_pago: Optional[datetime] = None
    estado: str
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True


class RespuestaAPI(BaseModel):
    mensaje: str
    success: bool = True
    datos: Optional[dict] = None


class RespuestaError(BaseModel):
    mensaje: str
    exito: bool = False
    error: str
    codigo: int
