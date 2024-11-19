"""create company table

Revision ID: db77465bda32
Revises: b941d95ff179
Create Date: 2024-11-19 14:47:55.463671

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db77465bda32'
down_revision: Union[str, None] = 'b941d95ff179'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
