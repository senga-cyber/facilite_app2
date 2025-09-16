"""Fusion heads

Revision ID: db99849563ab
Revises: f706cc0ea202, 08f46a4f26ba
Create Date: 2025-09-16 04:38:16.723209

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db99849563ab'
down_revision: Union[str, Sequence[str], None] = ('f706cc0ea202', '08f46a4f26ba')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
