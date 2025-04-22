"""restore deleted

Revision ID: 6aa1f68a1635
Revises: 921767ad9245
Create Date: 2025-04-13 13:38:53.525538

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6aa1f68a1635'
down_revision: Union[str, None] = '921767ad9245'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
