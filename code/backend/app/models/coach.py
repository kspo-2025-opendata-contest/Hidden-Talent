from sqlalchemy import Column, Integer, DateTime, func
from app.database import Base


class CoachStats(Base):
    """체육지도자 자격취득현황 (연도별 집계 데이터)"""
    __tablename__ = "coach_stats"

    id = Column(Integer, primary_key=True, index=True)
    qualification_year = Column(Integer, nullable=False)  # 자격취득년도

    # 자격 유형별 취득자 수
    health_exercise_manager = Column(Integer, default=0)  # 건강운동관리사
    professional_sports_1 = Column(Integer, default=0)  # 1급 전문스포츠지도사
    professional_sports_2 = Column(Integer, default=0)  # 2급 전문스포츠지도사
    living_sports_1 = Column(Integer, default=0)  # 1급 생활스포츠지도사
    living_sports_2 = Column(Integer, default=0)  # 2급 생활스포츠지도사
    youth_sports = Column(Integer, default=0)  # 유소년스포츠지도사
    senior_sports = Column(Integer, default=0)  # 노인스포츠지도사
    disabled_sports_1 = Column(Integer, default=0)  # 1급 장애인스포츠지도사
    disabled_sports_2 = Column(Integer, default=0)  # 2급 장애인스포츠지도사

    created_at = Column(DateTime(timezone=True), server_default=func.now())
