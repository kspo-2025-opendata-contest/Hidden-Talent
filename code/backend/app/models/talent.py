from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, func, Index, Text
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class GradeLevel(str, enum.Enum):
    """재능 등급 (5단계)"""
    excellent = "excellent"  # 최우수 - 상위 5%
    high = "high"  # 우수 - 상위 15%
    above_average = "above_average"  # 평균 이상 - 상위 35%
    average = "average"  # 평균 - 상위 55%
    below_average = "below_average"  # 평균 이하


class Gender(str, enum.Enum):
    """성별"""
    M = "M"
    F = "F"


class DisabilityType(str, enum.Enum):
    """장애 유형"""
    physical = "physical"  # 지체장애
    visual = "visual"  # 시각장애
    hearing = "hearing"  # 청각장애
    intellectual = "intellectual"  # 지적장애


class TalentTest(Base):
    """체력 측정 입력 기록"""
    __tablename__ = "talent_tests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # nullable: 비로그인도 가능

    # 기본 정보
    age = Column(Integer, nullable=False)
    grade = Column(String(20), nullable=True)  # 학년
    gender = Column(Enum(Gender), nullable=False)
    region_sido = Column(String(50), nullable=True)
    region_sigungu = Column(String(50), nullable=True)
    disability_type = Column(Enum(DisabilityType), nullable=True)  # 장애 유형

    # 체력 측정 항목 (국민체력100 기준)
    height = Column(Float, nullable=True)  # 신장 (cm)
    weight = Column(Float, nullable=True)  # 체중 (kg)
    bmi = Column(Float, nullable=True)
    grip_strength = Column(Float, nullable=True)  # 악력 (kg)
    sit_ups = Column(Integer, nullable=True)  # 윗몸일으키기 (회/분)
    standing_long_jump = Column(Float, nullable=True)  # 제자리멀리뛰기 (cm)
    shuttle_run_20m = Column(Integer, nullable=True)  # 왕복오래달리기 (회)
    sit_and_reach = Column(Float, nullable=True)  # 좌전굴 (cm)

    # 추가 측정 항목
    cardio_endurance = Column(Float, nullable=True)  # 심폐지구력
    flexibility = Column(Float, nullable=True)  # 유연성

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="talent_tests")
    scores = relationship("TalentScore", back_populates="talent_test", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_talent_tests_user_id", "user_id"),
        Index("idx_talent_tests_region", "region_sido", "region_sigungu"),
    )


class TalentScore(Base):
    """종목별 재능 점수"""
    __tablename__ = "talent_scores"

    id = Column(Integer, primary_key=True, index=True)
    talent_test_id = Column(Integer, ForeignKey("talent_tests.id"), nullable=False)

    sport = Column(String(50), nullable=False)  # 예: soccer, basketball, volleyball, sprint
    score = Column(Float, nullable=False)  # 0-100
    percentile = Column(Float, nullable=True)  # 0-100
    grade_level = Column(Enum(GradeLevel), nullable=True)
    comment = Column(Text, nullable=True)  # Gemini 생성 코멘트

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    talent_test = relationship("TalentTest", back_populates="scores")

    # Indexes
    __table_args__ = (
        Index("idx_talent_scores_test_id", "talent_test_id"),
        Index("idx_talent_scores_sport", "sport"),
    )
