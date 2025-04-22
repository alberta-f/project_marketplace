"""add GIN index for fulltext search

Revision ID: 93c63a49cb33
Revises: 283d4d571465
Create Date: 2025-04-13 19:25:29.549350

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93c63a49cb33'
down_revision: Union[str, None] = '283d4d571465'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.execute("""
        CREATE INDEX articles_fulltext_idx ON articles
        USING GIN (to_tsvector('russian', title || ' ' || content));
    """)

def downgrade():
    op.execute("DROP INDEX articles_fulltext_idx;")
