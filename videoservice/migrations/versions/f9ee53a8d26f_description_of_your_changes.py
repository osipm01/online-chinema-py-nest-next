"""description of your changes

Revision ID: f9ee53a8d26f
Revises: db2a94561b35
Create Date: 2026-09-07 12:05:15.292487

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9ee53a8d26f'
down_revision: Union[str, Sequence[str], None] = 'db2a94561b35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
