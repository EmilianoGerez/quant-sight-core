"""add watchlist filter fields

Revision ID: 3dfaa5008d92
Revises: 7c876843c76b
Create Date: 2025-07-10 14:42:04.825539

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3dfaa5008d92'
down_revision: Union[str, Sequence[str], None] = '7c876843c76b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
