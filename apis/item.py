from typing import List
from uuid import UUID

from crud.item_crud import ItemCRUD
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from schemas import ItemCreate, ItemResponse, ItemUpdate, RespuestaAPI
from sqlalchemy.orm import Session
from utils.error_handler import APIErrorHandler

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=List[ItemResponse])
async def obtener_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    solo_disponibles: bool = Query(False, description="Solo items disponibles"),
    id_libro: UUID = Query(None, description="Filtrar por libro"),
    id_revista: UUID = Query(None, description="Filtrar por revista"),
    id_periodico: UUID = Query(None, description="Filtrar por periódico"),
    db: Session = Depends(get_db),
):
    """Obtener todos los items (ejemplares físicos)."""
    try:
        item_crud = ItemCRUD(db)
        items = item_crud.obtener_items(
            skip=skip,
            limit=limit,
            solo_disponibles=solo_disponibles,
            id_libro=id_libro,
            id_revista=id_revista,
            id_periodico=id_periodico,
        )

        if not items or len(items) == 0:
            return []

        items_response = []
        for item in items:
            try:
                material_info = None
                tipo_item = "desconocido"
                if item.id_libro:
                    tipo_item = "libro"
                    try:
                        if hasattr(item, "libro") and item.libro is not None:
                            libro = item.libro
                            material_info = {
                                "id": str(libro.id),
                                "titulo": libro.titulo,
                                "isbn": getattr(libro, "isbn", None),
                                "tipo": "libro",
                            }
                    except (AttributeError, Exception):
                        material_info = None
                elif item.id_revista:
                    tipo_item = "revista"
                    try:
                        if hasattr(item, "revista") and item.revista is not None:
                            revista = item.revista
                            material_info = {
                                "id": str(revista.id),
                                "titulo": revista.titulo,
                                "numero_publicacion": getattr(
                                    revista, "numero_publicacion", None
                                ),
                                "tipo": "revista",
                            }
                    except (AttributeError, Exception):
                        material_info = None
                elif item.id_periodico:
                    tipo_item = "periodico"
                    try:
                        if hasattr(item, "periodico") and item.periodico is not None:
                            periodico = item.periodico
                            fecha_pub = getattr(periodico, "fecha_publicacion", None)
                            material_info = {
                                "id": str(periodico.id),
                                "titulo": periodico.titulo,
                                "fecha_publicacion": fecha_pub.isoformat()
                                if fecha_pub
                                else None,
                                "tipo": "periodico",
                            }
                    except (AttributeError, Exception):
                        material_info = None

                item_response = ItemResponse(
                    id=item.id,
                    id_libro=item.id_libro,
                    id_revista=item.id_revista,
                    id_periodico=item.id_periodico,
                    tipo_item=tipo_item,
                    codigo_barras=item.codigo_barras,
                    ubicacion=item.ubicacion,
                    estado_fisico=item.estado_fisico or "bueno",
                    disponible=item.disponible if item.disponible is not None else True,
                    observaciones=item.observaciones,
                    fecha_creacion=item.fecha_creacion,
                    fecha_actualizacion=item.fecha_actualizacion,
                    material=material_info,
                )
                items_response.append(item_response)
            except Exception:
                continue

        return items_response
    except Exception as e:
        raise APIErrorHandler.server_error("obtener items", str(e))


@router.get("/{item_id}", response_model=ItemResponse)
async def obtener_item(item_id: UUID, db: Session = Depends(get_db)):
    """Obtener un item por ID."""
    try:
        item_crud = ItemCRUD(db)
        item = item_crud.obtener_item(item_id)
        if not item:
            raise APIErrorHandler.not_found_error("Item", str(item_id))

        # Enriquecer con información del material
        material_info = None
        if item.id_libro and item.libro:
            material_info = {
                "id": item.libro.id,
                "titulo": item.libro.titulo,
                "isbn": item.libro.isbn,
                "tipo": "libro",
            }
        elif item.id_revista and item.revista:
            material_info = {
                "id": item.revista.id,
                "titulo": item.revista.titulo,
                "numero_publicacion": item.revista.numero_publicacion,
                "tipo": "revista",
            }
        elif item.id_periodico and item.periodico:
            material_info = {
                "id": item.periodico.id,
                "titulo": item.periodico.titulo,
                "fecha_publicacion": item.periodico.fecha_publicacion,
                "tipo": "periodico",
            }

        return {
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
            "material": material_info,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise APIErrorHandler.server_error("obtener item", str(e))


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def crear_item(item_data: ItemCreate, db: Session = Depends(get_db)):
    """Crear un nuevo item (ejemplar físico)."""
    try:
        item_crud = ItemCRUD(db)
        item = item_crud.crear_item(
            id_libro=item_data.id_libro,
            id_revista=item_data.id_revista,
            id_periodico=item_data.id_periodico,
            codigo_barras=item_data.codigo_barras,
            ubicacion=item_data.ubicacion,
            estado_fisico=item_data.estado_fisico or "bueno",
            disponible=item_data.disponible,
            observaciones=item_data.observaciones,
            id_usuario_creacion=item_data.id_usuario_creacion,
        )

        # Enriquecer con información del material
        material_info = None
        if item.id_libro and item.libro:
            material_info = {
                "id": item.libro.id,
                "titulo": item.libro.titulo,
                "isbn": item.libro.isbn,
                "tipo": "libro",
            }
        elif item.id_revista and item.revista:
            material_info = {
                "id": item.revista.id,
                "titulo": item.revista.titulo,
                "numero_publicacion": item.revista.numero_publicacion,
                "tipo": "revista",
            }
        elif item.id_periodico and item.periodico:
            material_info = {
                "id": item.periodico.id,
                "titulo": item.periodico.titulo,
                "fecha_publicacion": item.periodico.fecha_publicacion,
                "tipo": "periodico",
            }

        return {
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
            "material": material_info,
        }
    except ValueError as e:
        raise APIErrorHandler.validation_error(str(e))
    except Exception as e:
        raise APIErrorHandler.server_error("crear item", str(e))


@router.put("/{item_id}", response_model=ItemResponse)
async def actualizar_item(
    item_id: UUID, item_data: ItemUpdate, db: Session = Depends(get_db)
):
    """Actualizar un item existente."""
    try:
        item_crud = ItemCRUD(db)
        item_existente = item_crud.obtener_item(item_id)
        if not item_existente:
            raise APIErrorHandler.not_found_error("Item", str(item_id))

        campos_actualizacion = {
            k: v
            for k, v in item_data.dict(exclude={"id_usuario_edicion"}).items()
            if v is not None
        }

        item_actualizado = item_crud.actualizar_item(
            item_id, item_data.id_usuario_edicion, **campos_actualizacion
        )

        if not item_actualizado:
            raise APIErrorHandler.not_found_error("Item", str(item_id))

        # Enriquecer con información del material
        material_info = None
        if item_actualizado.id_libro and item_actualizado.libro:
            material_info = {
                "id": item_actualizado.libro.id,
                "titulo": item_actualizado.libro.titulo,
                "isbn": item_actualizado.libro.isbn,
                "tipo": "libro",
            }
        elif item_actualizado.id_revista and item_actualizado.revista:
            material_info = {
                "id": item_actualizado.revista.id,
                "titulo": item_actualizado.revista.titulo,
                "numero_publicacion": item_actualizado.revista.numero_publicacion,
                "tipo": "revista",
            }
        elif item_actualizado.id_periodico and item_actualizado.periodico:
            material_info = {
                "id": item_actualizado.periodico.id,
                "titulo": item_actualizado.periodico.titulo,
                "fecha_publicacion": item_actualizado.periodico.fecha_publicacion,
                "tipo": "periodico",
            }

        return {
            "id": item_actualizado.id,
            "id_libro": item_actualizado.id_libro,
            "id_revista": item_actualizado.id_revista,
            "id_periodico": item_actualizado.id_periodico,
            "tipo_item": item_actualizado.tipo_item,
            "codigo_barras": item_actualizado.codigo_barras,
            "ubicacion": item_actualizado.ubicacion,
            "estado_fisico": item_actualizado.estado_fisico,
            "disponible": item_actualizado.disponible,
            "observaciones": item_actualizado.observaciones,
            "fecha_creacion": item_actualizado.fecha_creacion,
            "fecha_actualizacion": item_actualizado.fecha_actualizacion,
            "material": material_info,
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise APIErrorHandler.validation_error(str(e))
    except Exception as e:
        raise APIErrorHandler.server_error("actualizar item", str(e))


@router.delete(
    "/{item_id}", response_model=RespuestaAPI, status_code=status.HTTP_200_OK
)
async def eliminar_item(item_id: UUID, db: Session = Depends(get_db)):
    """Eliminar un item."""
    try:
        item_crud = ItemCRUD(db)
        item_existente = item_crud.obtener_item(item_id)
        if not item_existente:
            raise APIErrorHandler.not_found_error("Item", str(item_id))

        eliminado = item_crud.eliminar_item(item_id)
        if eliminado:
            return RespuestaAPI(mensaje="Item eliminado exitosamente", success=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar item",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise APIErrorHandler.server_error("eliminar item", str(e))


@router.get("/por-material/{tipo}/{material_id}", response_model=List[ItemResponse])
async def obtener_items_por_material(
    tipo: str,
    material_id: UUID,
    solo_disponibles: bool = Query(False, description="Solo items disponibles"),
    db: Session = Depends(get_db),
):
    """Obtener todos los items (ejemplares) de un material específico."""
    try:
        item_crud = ItemCRUD(db)
        items = item_crud.obtener_items_por_material(
            tipo=tipo, material_id=material_id, solo_disponibles=solo_disponibles
        )

        # Enriquecer con información del material
        items_response = []
        for item in items:
            material_info = None
            if item.id_libro and item.libro:
                material_info = {
                    "id": item.libro.id,
                    "titulo": item.libro.titulo,
                    "isbn": item.libro.isbn,
                    "tipo": "libro",
                }
            elif item.id_revista and item.revista:
                material_info = {
                    "id": item.revista.id,
                    "titulo": item.revista.titulo,
                    "numero_publicacion": item.revista.numero_publicacion,
                    "tipo": "revista",
                }
            elif item.id_periodico and item.periodico:
                material_info = {
                    "id": item.periodico.id,
                    "titulo": item.periodico.titulo,
                    "fecha_publicacion": item.periodico.fecha_publicacion,
                    "tipo": "periodico",
                }

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
                "material": material_info,
            }
            items_response.append(item_dict)

        return items_response
    except ValueError as e:
        raise APIErrorHandler.validation_error(str(e))
    except Exception as e:
        raise APIErrorHandler.server_error("obtener items por material", str(e))
