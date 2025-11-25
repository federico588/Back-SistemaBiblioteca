import logging
from typing import Any, Dict, Optional

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class APIErrorHandler:
    """Manejador de errores personalizado para la API"""

    @staticmethod
    def create_error_response(
        error_type: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> HTTPException:
        """
        Crear una respuesta de error estructurada

        Args:
            error_type: Tipo de error (VALIDATION_ERROR, NOT_FOUND, etc.)
            message: Mensaje descriptivo del error
            details: Detalles adicionales del error
            status_code: Código de estado HTTP

        Returns:
            HTTPException con error estructurado
        """
        error_response = {
            "error_type": error_type,
            "message": message,
            "success": False,
        }

        if details:
            error_response["details"] = details

        return HTTPException(status_code=status_code, detail=error_response)

    @staticmethod
    def validation_error(
        message: str, field: str = None, value: str = None
    ) -> HTTPException:
        """Error de validación de datos"""
        logger.warning(
            f"Error de validación: {message} (campo: {field}, valor: {value})"
        )
        details = {}
        if field:
            details["field"] = field
        if value:
            details["value"] = value

        return APIErrorHandler.create_error_response(
            error_type="VALIDATION_ERROR",
            message=message,
            details=details,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @staticmethod
    def not_found_error(resource: str, identifier: str = None) -> HTTPException:
        """Error de recurso no encontrado"""
        details = {"resource": resource}
        if identifier:
            details["identifier"] = identifier

        return APIErrorHandler.create_error_response(
            error_type="NOT_FOUND",
            message=f"{resource} no encontrado",
            details=details,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    @staticmethod
    def duplicate_error(resource: str, field: str, value: str) -> HTTPException:
        """Error de duplicado"""
        return APIErrorHandler.create_error_response(
            error_type="DUPLICATE_ERROR",
            message=f"Ya existe un {resource} con {field}: {value}",
            details={"field": field, "value": value},
            status_code=status.HTTP_409_CONFLICT,
        )

    @staticmethod
    def authentication_error(
        message: str = "Credenciales incorrectas",
    ) -> HTTPException:
        """Error de autenticación"""
        return APIErrorHandler.create_error_response(
            error_type="AUTHENTICATION_ERROR",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    @staticmethod
    def authorization_error(
        message: str = "No tiene permisos para realizar esta acción",
    ) -> HTTPException:
        """Error de autorización"""
        return APIErrorHandler.create_error_response(
            error_type="AUTHORIZATION_ERROR",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )

    @staticmethod
    def server_error(operation: str, original_error: str) -> HTTPException:
        """Error interno del servidor"""
        logger.error(f"Error al {operation}: {str(original_error)}", exc_info=True)
        return APIErrorHandler.create_error_response(
            error_type="SERVER_ERROR",
            message=f"Error interno al {operation}",
            details={"original_error": str(original_error)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @staticmethod
    def business_logic_error(
        message: str, details: Optional[Dict[str, Any]] = None
    ) -> HTTPException:
        """Error de lógica de negocio"""
        return APIErrorHandler.create_error_response(
            error_type="BUSINESS_LOGIC_ERROR",
            message=message,
            details=details,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
