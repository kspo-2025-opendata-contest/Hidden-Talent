"""Update GradeLevel enum to 5 levels

Revision ID: 9ee536e38dfe
Revises: f4979a6c8396
Create Date: 2025-12-07 23:14:47.032671

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ee536e38dfe'
down_revision: Union[str, None] = 'f4979a6c8396'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL enum 타입 업데이트 (3단계 -> 5단계)
    # 1. 기존 데이터 삭제 (medium, low -> 새 값으로 변환 불가)
    op.execute("DELETE FROM talent_scores WHERE grade_level IN ('medium', 'low')")

    # 2. 새 enum 값 추가
    op.execute("ALTER TYPE gradelevel ADD VALUE IF NOT EXISTS 'excellent'")
    op.execute("ALTER TYPE gradelevel ADD VALUE IF NOT EXISTS 'above_average'")
    op.execute("ALTER TYPE gradelevel ADD VALUE IF NOT EXISTS 'average'")
    op.execute("ALTER TYPE gradelevel ADD VALUE IF NOT EXISTS 'below_average'")

    # 참고: PostgreSQL에서는 ALTER TYPE으로 enum 값 삭제가 불가하므로
    # medium, low 값은 남아있지만 코드에서 사용하지 않음


def downgrade() -> None:
    # Downgrade는 지원하지 않음 (enum 값 삭제 불가)
    pass
