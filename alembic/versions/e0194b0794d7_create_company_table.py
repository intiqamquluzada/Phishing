"""create company table

Revision ID: e0194b0794d7
Revises: ee43560fd013
Create Date: 2024-11-19 15:06:51.062833

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e0194b0794d7'
down_revision: Union[str, None] = 'ee43560fd013'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
