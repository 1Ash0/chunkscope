"""
Add full-text search and parent_chunk_id

Revision ID: b3d9f1e7a2b0
Revises: 59791fc8d3c3
Create Date: 2026-02-13 12:05:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b3d9f1e7a2b0"
down_revision: Union[str, None] = "59791fc8d3c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add parent_chunk_id column
    op.add_column('chunks', sa.Column('parent_chunk_id', sa.Uuid(), nullable=True))
    op.create_foreign_key('fk_chunks_parent_chunk_id', 'chunks', 'chunks', ['parent_chunk_id'], ['id'], ondelete='SET NULL')
    op.create_index(op.f('ix_chunks_parent_chunk_id'), 'chunks', ['parent_chunk_id'], unique=False)

    # 2. Add tsv (Full-Text Search) column
    op.add_column('chunks', sa.Column('tsv', postgresql.TSVECTOR(), nullable=True))
    
    # 3. Create GIN index for tsv
    op.create_index('ix_chunks_tsv', 'chunks', ['tsv'], unique=False, postgresql_using='gin')

    # 4. Create trigger to update tsv from text
    # We use 'english' configuration by default
    op.execute("""
        CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
        ON chunks FOR EACH ROW EXECUTE FUNCTION
        tsvector_update_trigger(tsv, 'pg_catalog.english', text);
    """)
    
    # 5. Initialize tsv for existing data
    op.execute("UPDATE chunks SET tsv = to_tsvector('english', COALESCE(text, ''));")


def downgrade() -> None:
    # Remove trigger
    op.execute("DROP TRIGGER IF EXISTS tsvectorupdate ON chunks;")
    
    # Remove index
    op.drop_index('ix_chunks_tsv', table_name='chunks')
    
    # Remove columns
    op.drop_column('chunks', 'tsv')
    op.drop_index(op.f('ix_chunks_parent_chunk_id'), table_name='chunks')
    op.drop_constraint('fk_chunks_parent_chunk_id', 'chunks', type_='foreignkey')
    op.drop_column('chunks', 'parent_chunk_id')
