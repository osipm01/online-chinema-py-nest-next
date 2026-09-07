"""add poster  url:

Revision ID: f3108630711b
Revises: f9ee53a8d26f
Create Date: 2026-09-07 12:05:36.286418

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3108630711b'
down_revision: Union[str, Sequence[str], None] = 'f9ee53a8d26f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
