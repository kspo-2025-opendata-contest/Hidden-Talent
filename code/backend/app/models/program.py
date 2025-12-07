from sqlalchemy import Column, Integer, String, Float, Date, DateTime, func, Index
from app.database import Base


class Program(Base):
    """청소년/유아동 이용가능 체육시설 프로그램"""
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)

    # 시설 정보
    facility_name = Column(String(200), nullable=True)
    facility_type_code = Column(String(20), nullable=True)
    facility_type_name = Column(String(100), nullable=True)
    industry_code = Column(String(20), nullable=True)
    industry_name = Column(String(100), nullable=True)  # 수영장, 체육관 등

    # 지역 정보
    region_sido_code = Column(String(20), nullable=True)
    region_sido = Column(String(50), nullable=True)
    region_sigungu_code = Column(String(20), nullable=True)
    region_sigungu = Column(String(50), nullable=True)
    emd_name = Column(String(50), nullable=True)
    address = Column(String(500), nullable=True)

    # 좌표
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # 프로그램 정보
    program_type = Column(String(100), nullable=True)  # PROGRM_TY_NM
    program_name = Column(String(200), nullable=True)  # PROGRM_NM
    target_group = Column(String(100), nullable=True)  # PROGRM_TRGET_NM (성인/청소년, 초등학생 등)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    schedule_weekdays = Column(String(50), nullable=True)  # 월화수목금
    schedule_time = Column(String(50), nullable=True)  # 07:00~07:50
    capacity = Column(Integer, nullable=True)  # 모집인원
    price = Column(Float, nullable=True)  # 가격
    price_type = Column(String(50), nullable=True)  # 가격유형
    homepage_url = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index("idx_programs_region", "region_sido", "region_sigungu"),
        Index("idx_programs_target", "target_group"),
    )
