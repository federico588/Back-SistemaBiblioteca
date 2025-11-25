"""Reestructurar items y agregar autor/categoria a materiales

Revision ID: a1b2c3d4e5f6
Revises: 3b07d4708b40
Create Date: 2025-01-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "3b07d4708b40"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Agregar columnas id_autor e id_categoria a libros, revistas, periodicos
    op.add_column(
        "libros", sa.Column("id_autor", postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.add_column(
        "libros",
        sa.Column("id_categoria", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key("fk_libros_autor", "libros", "autores", ["id_autor"], ["id"])
    op.create_foreign_key(
        "fk_libros_categoria", "libros", "categorias", ["id_categoria"], ["id"]
    )

    op.add_column(
        "revistas", sa.Column("id_autor", postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.add_column(
        "revistas",
        sa.Column("id_categoria", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_revistas_autor", "revistas", "autores", ["id_autor"], ["id"]
    )
    op.create_foreign_key(
        "fk_revistas_categoria", "revistas", "categorias", ["id_categoria"], ["id"]
    )

    op.add_column(
        "periodicos",
        sa.Column("id_autor", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "periodicos",
        sa.Column("id_categoria", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_periodicos_autor", "periodicos", "autores", ["id_autor"], ["id"]
    )
    op.create_foreign_key(
        "fk_periodicos_categoria", "periodicos", "categorias", ["id_categoria"], ["id"]
    )

    # 2. Eliminar datos existentes en items y préstamos asociados
    # Primero eliminar préstamos que referencian items
    op.execute("DELETE FROM prestamos WHERE id_item IN (SELECT id FROM items)")
    # Luego eliminar items
    op.execute("DELETE FROM items")

    # 3. Eliminar columnas obsoletas de items
    op.drop_constraint("items_id_autor_fkey", "items", type_="foreignkey")
    op.drop_constraint("items_id_categoria_fkey", "items", type_="foreignkey")
    op.drop_column("items", "titulo")
    op.drop_column("items", "tipo_item")
    op.drop_column("items", "id_autor")
    op.drop_column("items", "id_categoria")

    # 4. Agregar nuevas columnas en items
    op.add_column(
        "items", sa.Column("id_libro", postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.add_column(
        "items", sa.Column("id_revista", postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.add_column(
        "items", sa.Column("id_periodico", postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.add_column(
        "items", sa.Column("codigo_barras", sa.String(length=50), nullable=True)
    )
    op.add_column("items", sa.Column("ubicacion", sa.String(length=100), nullable=True))
    op.add_column(
        "items",
        sa.Column(
            "estado_fisico", sa.String(length=50), nullable=True, server_default="bueno"
        ),
    )
    op.add_column("items", sa.Column("observaciones", sa.Text(), nullable=True))

    # 5. Agregar relaciones FK con CASCADE delete
    op.create_foreign_key(
        "fk_items_libro", "items", "libros", ["id_libro"], ["id"], ondelete="CASCADE"
    )
    op.create_foreign_key(
        "fk_items_revista",
        "items",
        "revistas",
        ["id_revista"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_items_periodico",
        "items",
        "periodicos",
        ["id_periodico"],
        ["id"],
        ondelete="CASCADE",
    )

    # 6. Agregar constraint CHECK: solo uno de los tres IDs debe estar presente
    op.create_check_constraint(
        "chk_item_tipo",
        "items",
        "(id_libro IS NOT NULL AND id_revista IS NULL AND id_periodico IS NULL) OR "
        "(id_libro IS NULL AND id_revista IS NOT NULL AND id_periodico IS NULL) OR "
        "(id_libro IS NULL AND id_revista IS NULL AND id_periodico IS NOT NULL)",
    )

    # 7. Agregar índices
    op.create_index("idx_items_libro", "items", ["id_libro"])
    op.create_index("idx_items_revista", "items", ["id_revista"])
    op.create_index("idx_items_periodico", "items", ["id_periodico"])
    op.create_index("idx_items_disponible", "items", ["disponible"])
    op.create_index("idx_items_codigo_barras", "items", ["codigo_barras"], unique=True)

    # 8. Hacer id_autor NOT NULL en materiales (después de agregar datos si es necesario)
    # Por ahora lo dejamos nullable para permitir migración gradual


def downgrade() -> None:
    # Revertir cambios en orden inverso

    # Eliminar índices
    op.drop_index("idx_items_codigo_barras", "items")
    op.drop_index("idx_items_disponible", "items")
    op.drop_index("idx_items_periodico", "items")
    op.drop_index("idx_items_revista", "items")
    op.drop_index("idx_items_libro", "items")

    # Eliminar constraint CHECK
    op.drop_constraint("chk_item_tipo", "items", type_="check")

    # Eliminar relaciones FK
    op.drop_constraint("fk_items_periodico", "items", type_="foreignkey")
    op.drop_constraint("fk_items_revista", "items", type_="foreignkey")
    op.drop_constraint("fk_items_libro", "items", type_="foreignkey")

    # Eliminar nuevas columnas de items
    op.drop_column("items", "observaciones")
    op.drop_column("items", "estado_fisico")
    op.drop_column("items", "ubicacion")
    op.drop_column("items", "codigo_barras")
    op.drop_column("items", "id_periodico")
    op.drop_column("items", "id_revista")
    op.drop_column("items", "id_libro")

    # Restaurar columnas obsoletas de items
    op.add_column(
        "items",
        sa.Column("titulo", sa.String(length=255), nullable=False, server_default=""),
    )
    op.add_column(
        "items",
        sa.Column(
            "tipo_item", sa.String(length=20), nullable=False, server_default="libro"
        ),
    )
    op.add_column(
        "items", sa.Column("id_autor", postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.add_column(
        "items", sa.Column("id_categoria", postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.create_foreign_key(
        "items_id_categoria_fkey", "items", "categorias", ["id_categoria"], ["id"]
    )
    op.create_foreign_key(
        "items_id_autor_fkey", "items", "autores", ["id_autor"], ["id"]
    )

    # Eliminar columnas de materiales
    op.drop_constraint("fk_periodicos_categoria", "periodicos", type_="foreignkey")
    op.drop_constraint("fk_periodicos_autor", "periodicos", type_="foreignkey")
    op.drop_column("periodicos", "id_categoria")
    op.drop_column("periodicos", "id_autor")

    op.drop_constraint("fk_revistas_categoria", "revistas", type_="foreignkey")
    op.drop_constraint("fk_revistas_autor", "revistas", type_="foreignkey")
    op.drop_column("revistas", "id_categoria")
    op.drop_column("revistas", "id_autor")

    op.drop_constraint("fk_libros_categoria", "libros", type_="foreignkey")
    op.drop_constraint("fk_libros_autor", "libros", type_="foreignkey")
    op.drop_column("libros", "id_categoria")
    op.drop_column("libros", "id_autor")
