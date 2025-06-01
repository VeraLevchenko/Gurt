"""Add PhysicalPerson, LegalEntity and update Contract

Revision ID: ce2dc3860cc0
Revises: 43fa26595b36
Create Date: <дата создания, например, 2025-06-01 08:00:00>
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ce2dc3860cc0'
down_revision = '43fa26595b36'
branch_labels = None
depends_on = None

def upgrade():
    # Создание новых таблиц
    op.create_table('physical_persons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('passport', sa.String(length=50), nullable=False),
        sa.Column('address', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('passport')
    )
    op.create_table('legal_entities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('inn', sa.String(length=50), nullable=False),
        sa.Column('legal_address', sa.String(length=255), nullable=False),
        sa.Column('director_full_name', sa.String(length=255), nullable=False),
        sa.Column('payment_details', sa.Text(), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('inn'),
        sa.UniqueConstraint('name')
    )
    # Обновление таблицы contracts
    op.add_column('contracts', sa.Column('physical_person_id', sa.Integer(), nullable=True))
    op.add_column('contracts', sa.Column('legal_entity_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'contracts', 'physical_persons', ['physical_person_id'], ['id'])
    op.create_foreign_key(None, 'contracts', 'legal_entities', ['legal_entity_id'], ['id'])
    op.drop_column('contracts', 'subject')

def downgrade():
    op.add_column('contracts', sa.Column('subject', sa.String(length=255), nullable=False))
    op.drop_constraint(None, 'contracts', type_='foreignkey')
    op.drop_constraint(None, 'contracts', type_='foreignkey')
    op.drop_column('contracts', 'legal_entity_id')
    op.drop_column('contracts', 'physical_person_id')
    op.drop_table('legal_entities')
    op.drop_table('physical_persons')