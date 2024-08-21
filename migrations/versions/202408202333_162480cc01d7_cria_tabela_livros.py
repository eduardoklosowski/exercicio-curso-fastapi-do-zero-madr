"""cria tabela livros

Revision ID: 162480cc01d7
Revises: 643dd8d47c7f
Create Date: 2024-08-20 23:33:29.339394-03:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '162480cc01d7'
down_revision: str | None = '643dd8d47c7f'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'livros',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('romancista_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('title'),
        sa.ForeignKeyConstraint(
            ['romancista_id'],
            ['romancistas.id'],
        ),
    )


def downgrade() -> None:
    op.drop_table('livros')
