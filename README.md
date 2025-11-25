# Sistema de Gestión de Biblioteca - Backend

API REST desarrollada con FastAPI para la gestión de una biblioteca, incluyendo libros, revistas, periódicos, préstamos, multas y usuarios.

## Instalación y Compilación

### Requisitos Previos

- Python 3.8 o superior
- PostgreSQL (base de datos en Neon o local)
- pip (gestor de paquetes de Python)

### Paso 1: Instalar Python

Asegúrate de tener Python 3.8 o superior instalado. Verifica la versión:

```bash
python --version
```

### Paso 2: Crear Entorno Virtual (Recomendado)

Es recomendable crear un entorno virtual para aislar las dependencias:

```bash
python -m venv venv
```

Activar el entorno virtual:

- **Windows:**
```bash
venv\Scripts\activate
```

- **Linux/Mac:**
```bash
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

Instala todas las dependencias del proyecto:

```bash
pip install -r requirements.txt
```

Las dependencias incluyen:
- FastAPI
- SQLAlchemy
- PostgreSQL (psycopg2-binary)
- Alembic
- python-dotenv
- python-jose[cryptography]
- pydantic
- uvicorn
- black

### Paso 4: Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto BACK con las siguientes variables:

```
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/nombre_bd
SECRET_KEY=tu-secret-key-super-segura-cambiar-en-produccion
```

**Ejemplo para Neon:**
```
DATABASE_URL=postgresql://usuario:password@ep-morning-bird-xxxxx-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
SECRET_KEY=mi-clave-secreta-muy-segura-123456789
```

### Paso 5: Ejecutar Migraciones

Aplica las migraciones de la base de datos:

```bash
python -m alembic upgrade head
```

### Paso 6: Iniciar el Servidor

Inicia el servidor de desarrollo:

```bash
python main.py
```

El servidor estará disponible en:
- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Tecnologías

- **Python 3.8+**
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para PostgreSQL
- **PostgreSQL** - Base de datos (Neon)
- **Alembic** - Migraciones de base de datos
- **JWT** - Autenticación con tokens
- **Pydantic** - Validación de datos
- **Black** - Formateador de código

## Estructura del Proyecto

```
BACK/
├── apis/              # Endpoints de la API
│   ├── auth.py        # Autenticación
│   ├── usuario.py     # Gestión de usuarios
│   ├── libro.py        # Gestión de libros
│   ├── revista.py      # Gestión de revistas
│   ├── periodico.py    # Gestión de periódicos
│   ├── item.py         # Gestión de items (ejemplares)
│   ├── prestamo.py     # Gestión de préstamos
│   ├── multa.py        # Gestión de multas
│   ├── autor.py        # Gestión de autores
│   ├── editorial.py    # Gestión de editoriales
│   └── categoria.py    # Gestión de categorías
├── auth/              # Módulo de seguridad
│   └── security.py    # Gestión de contraseñas y JWT
├── crud/              # Operaciones CRUD
│   ├── usuario_crud.py
│   ├── libro_crud.py
│   ├── revista_crud.py
│   ├── periodico_crud.py
│   ├── item_crud.py
│   ├── prestamo_crud.py
│   ├── multa_crud.py
│   ├── autor_crud.py
│   ├── editorial_crud.py
│   └── categoria_crud.py
├── database/          # Configuración de base de datos
│   └── config.py
├── entities/          # Modelos de SQLAlchemy
│   ├── usuario.py
│   ├── libro.py
│   ├── revista.py
│   ├── periodico.py
│   ├── items.py
│   ├── prestamo.py
│   ├── multa.py
│   ├── autores.py
│   ├── editoriales.py
│   └── categoria.py
├── migrations/        # Migraciones de Alembic
│   └── versions/
├── utils/             # Utilidades
│   └── error_handler.py
├── main.py            # Punto de entrada
├── schemas.py         # Esquemas Pydantic
├── requirements.txt   # Dependencias
├── alembic.ini        # Configuración de Alembic
└── .env               # Variables de entorno (no se sube al repo)
```

## Endpoints Principales

### Autenticación
- `POST /api/auth/login` - Iniciar sesión

### Usuarios
- `GET /api/usuarios` - Listar usuarios
- `POST /api/usuarios` - Crear usuario
- `GET /api/usuarios/{id}` - Obtener usuario
- `PUT /api/usuarios/{id}` - Actualizar usuario
- `DELETE /api/usuarios/{id}` - Eliminar usuario

### Libros
- `GET /api/libros` - Listar libros
- `POST /api/libros` - Crear libro
- `GET /api/libros/{id}` - Obtener libro
- `PUT /api/libros/{id}` - Actualizar libro
- `DELETE /api/libros/{id}` - Eliminar libro
- `GET /api/libros/{id}/items` - Obtener items de un libro

### Revistas
- `GET /api/revistas` - Listar revistas
- `POST /api/revistas` - Crear revista
- `GET /api/revistas/{id}` - Obtener revista
- `PUT /api/revistas/{id}` - Actualizar revista
- `DELETE /api/revistas/{id}` - Eliminar revista
- `GET /api/revistas/{id}/items` - Obtener items de una revista

### Periódicos
- `GET /api/periodicos` - Listar periódicos
- `POST /api/periodicos` - Crear periódico
- `GET /api/periodicos/{id}` - Obtener periódico
- `PUT /api/periodicos/{id}` - Actualizar periódico
- `DELETE /api/periodicos/{id}` - Eliminar periódico
- `GET /api/periodicos/{id}/items` - Obtener items de un periódico

### Items (Ejemplares)
- `GET /api/items` - Listar items
- `POST /api/items` - Crear item
- `GET /api/items/{id}` - Obtener item
- `PUT /api/items/{id}` - Actualizar item
- `DELETE /api/items/{id}` - Eliminar item

### Préstamos
- `GET /api/prestamos` - Listar préstamos
- `POST /api/prestamos` - Crear préstamo
- `GET /api/prestamos/{id}` - Obtener préstamo
- `PUT /api/prestamos/{id}` - Actualizar préstamo
- `POST /api/prestamos/{id}/devolver` - Devolver préstamo
- `DELETE /api/prestamos/{id}` - Eliminar préstamo

### Multas
- `GET /api/multas` - Listar multas
- `POST /api/multas` - Crear multa
- `GET /api/multas/{id}` - Obtener multa
- `PUT /api/multas/{id}` - Actualizar multa
- `POST /api/multas/{id}/pagar` - Pagar multa
- `DELETE /api/multas/{id}` - Eliminar multa

## Requisitos de Contraseña

Las contraseñas deben cumplir con los siguientes requisitos:
- Mínimo 8 caracteres
- Al menos una letra mayúscula
- Al menos una letra minúscula
- Al menos un número
- Al menos un carácter especial (!@#$%^&*()_+-=[]{}|;:,.<>?)

## Migraciones

Para crear una nueva migración:

```bash
python -m alembic revision --autogenerate -m "descripción"
```

Para aplicar migraciones:

```bash
python -m alembic upgrade head
```

Para revertir la última migración:

```bash
python -m alembic downgrade -1
```

## Formateo de Código

El proyecto utiliza Black para formatear el código. Para formatear todos los archivos:

```bash
black .
```

## Desarrollo

El proyecto utiliza:
- **Type hints** para mejor documentación del código
- **Pydantic** para validación de datos
- **SQLAlchemy ORM** para interacción con la base de datos
- **Alembic** para versionado de esquemas
- **Docstrings** para documentación de funciones y clases

## Notas

- El puerto por defecto es 8000, pero puede cambiarse mediante la variable de entorno `PORT`
- La documentación interactiva está disponible en `/docs` (Swagger) y `/redoc`
- Todos los endpoints requieren autenticación excepto `/api/auth/login`
- Las credenciales por defecto del administrador son: usuario `admin`, contraseña `Admin123!`

## Lógica de Negocio

### Entidades Principales

1. **Material Bibliográfico** (Libro/Revista/Periódico): Información del material en el catálogo. NO se presta directamente.
2. **Item**: Ejemplar físico específico que SÍ se puede prestar. Pertenece a un Material.
3. **Préstamo**: Registro de préstamo de un Item específico.
4. **Multa**: Penalización por retraso en la devolución de un préstamo.

### Relaciones

```
Material (Libro/Revista/Periodico) [1] → [N] Items → [N] Préstamos → [0-1] Multas
```

### Validaciones Importantes

- Al crear Item: validar que exactamente uno de id_libro/id_revista/id_periodico esté presente
- Al crear Item: validar que el material existe
- Al crear Item: validar código_barras único (si se proporciona)
- Al crear Libro/Revista/Periodico: validar que autor y editorial existen
- Al eliminar Material: CASCADE eliminará todos sus Items (y sus préstamos si no hay validación)
- Al crear Préstamo: validar que Item existe y está disponible
- No se puede cambiar el tipo de material de un Item existente
