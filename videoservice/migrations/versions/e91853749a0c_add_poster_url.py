"""add poster url

Revision ID: e91853749a0c
Revises: f3108630711b
Create Date: 2026-09-07 12:12:39.111410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e91853749a0c'
down_revision: Union[str, Sequence[str], None] = 'f3108630711b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
