from sqlalchemy import Column, Integer, String, DateTime, func, Index
from app.database import Base


class SupportStats(Base):
    """스포츠강좌이용권 활용 통계"""
    __tablename__ = "support_stats"

    id = Column(Integer, primary_key=True, index=True)
    base_year = Column(Integer, nullable=False)  # 기준년도
    region_sido_code = Column(String(20), nullable=True)
    region_sido = Column(String(50), nullable=True)
    region_sigungu_code = Column(String(20), nullable=True)
    region_sigungu = Column(String(50), nullable=True)
    population = Column(Integer, nullable=True)  # 시군구별 인구수
    facility_count = Column(Integer, nullable=True)  # 시군구별 시설수
    recipient_type_code = Column(String(10), nullable=True)  # N: 차상위, S: 기초수급
    recipient_type_name = Column(String(100), nullable=True)
    target_count = Column(Integer, nullable=True)  # 대상 인원
    recipient_count = Column(Integer, nullable=True)  # 수혜 인원

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index("idx_support_stats_region", "region_sido", "region_sigungu"),
        Index("idx_support_stats_year", "base_year"),
    )
