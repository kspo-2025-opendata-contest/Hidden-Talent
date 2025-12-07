from sqlalchemy import Column, Integer, String, Float, DateTime, func, Index
from app.database import Base


class Facility(Base):
    """공공체육시설"""
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    facility_type_code = Column(String(20), nullable=True)  # FCLTY_SDIV_CD
    facility_type_name = Column(String(100), nullable=True)  # FCLTY_FLAG_NM
    industry_code = Column(String(20), nullable=True)  # INDUTY_CD
    industry_name = Column(String(100), nullable=True)  # INDUTY_NM (수영장, 체육관 등)
    region_sido_code = Column(String(20), nullable=True)
    region_sido = Column(String(50), nullable=True)
    region_sigungu_code = Column(String(20), nullable=True)
    region_sigungu = Column(String(50), nullable=True)
    emd_code = Column(String(20), nullable=True)  # 읍면동 코드
    emd_name = Column(String(50), nullable=True)
    address = Column(String(500), nullable=True)
    phone = Column(String(50), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    homepage_url = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index("idx_facilities_region", "region_sido", "region_sigungu"),
        Index("idx_facilities_type", "facility_type_name"),
    )


class FacilityStats(Base):
    """지역별 공공체육시설 보급현황 통계"""
    __tablename__ = "facility_stats"

    id = Column(Integer, primary_key=True, index=True)
    base_ym = Column(String(10), nullable=False)  # 기준년월 (예: 202008)
    region_sido_code = Column(String(20), nullable=True)
    region_sido = Column(String(50), nullable=True)
    region_sigungu_code = Column(String(20), nullable=True)
    region_sigungu = Column(String(50), nullable=True)
    facility_count = Column(Integer, nullable=True)  # 시설 수
    population = Column(Integer, nullable=True)  # 인구 수
    facility_per_person = Column(Float, nullable=True)  # 1인당 시설 수
    rank = Column(Integer, nullable=True)  # 순위

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index("idx_facility_stats_region", "region_sido", "region_sigungu"),
    )
