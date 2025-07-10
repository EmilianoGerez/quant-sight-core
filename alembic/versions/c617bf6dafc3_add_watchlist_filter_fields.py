"""add watchlist filter fields

Revision ID: c617bf6dafc3
Revises: 3dfaa5008d92
Create Date: 2025-07-10 14:50:17.969305

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c617bf6dafc3'
down_revision: Union[str, Sequence[str], None] = '3dfaa5008d92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    # ── add category, sector, industry, asset_class, region ─────────────────
    op.add_column('watchlist',
        sa.Column('category',    sa.String(), nullable=False, server_default='stock')
    )
    op.add_column('watchlist',
        sa.Column('sector',      sa.String(), nullable=True)
    )
    op.add_column('watchlist',
        sa.Column('industry',    sa.String(), nullable=True)
    )
    op.add_column('watchlist',
        sa.Column('asset_class', sa.String(), nullable=True)
    )
    op.add_column('watchlist',
        sa.Column('region',      sa.String(), nullable=True)
    )

    # ── add track_iv, is_active, added_by ────────────────────────────────────
    op.add_column('watchlist',
        sa.Column('track_iv',  sa.Boolean(), nullable=False, server_default=sa.text('false'))
    )
    op.add_column('watchlist',
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true'))
    )
    op.add_column('watchlist',
        sa.Column('added_by',  sa.String(),  nullable=True)
    )

    # ── clean up server defaults if you don’t want them persisted ───────────
    op.alter_column('watchlist', 'category',    server_default=None)
    op.alter_column('watchlist', 'track_iv',     server_default=None)
    op.alter_column('watchlist', 'is_active',    server_default=None)


def downgrade() -> None:
    # ── drop in reverse order ───────────────────────────────────────────────
    op.drop_column('watchlist', 'added_by')
    op.drop_column('watchlist', 'is_active')
    op.drop_column('watchlist', 'track_iv')

    op.drop_column('watchlist', 'region')
    op.drop_column('watchlist', 'asset_class')
    op.drop_column('watchlist', 'industry')
    op.drop_column('watchlist', 'sector')
    op.drop_column('watchlist', 'category')