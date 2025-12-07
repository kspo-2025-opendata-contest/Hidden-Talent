"""Add disability_type to talent_tests

Revision ID: f4979a6c8396
Revises: 25caf1590184
Create Date: 2025-12-07 21:02:38.716047

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4979a6c8396'
down_revision: Union[str, None] = '25caf1590184'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the enum type first
    disability_type_enum = sa.Enum('physical', 'visual', 'hearing', 'intellectual', name='disabilitytype')
    disability_type_enum.create(op.get_bind(), checkfirst=True)

    # Add the column
    op.add_column('talent_tests', sa.Column('disability_type', disability_type_enum, nullable=True))


def downgrade() -> None:
    op.drop_column('talent_tests', 'disability_type')
    # Drop the enum type
    sa.Enum(name='disabilitytype').drop(op.get_bind(), checkfirst=True)
