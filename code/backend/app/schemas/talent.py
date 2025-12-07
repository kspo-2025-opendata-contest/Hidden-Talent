from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class GenderEnum(str, Enum):
    M = "M"
    F = "F"


class GradeLevelEnum(str, Enum):
    excellent = "excellent"  # 최우수
    high = "high"  # 우수
    above_average = "above_average"  # 평균 이상
    average = "average"  # 평균
    below_average = "below_average"  # 평균 이하


class DisabilityTypeEnum(str, Enum):
    physical = "physical"  # 지체장애
    visual = "visual"  # 시각장애
    hearing = "hearing"  # 청각장애
    intellectual = "intellectual"  # 지적장애


class TalentTestRequest(BaseModel):
    """재능 진단 요청"""
    age: int = Field(..., ge=5, le=100, description="나이")
    grade: Optional[str] = Field(None, max_length=20, description="학년")
    gender: GenderEnum = Field(..., description="성별 (M/F)")
    region_sido: Optional[str] = Field(None, max_length=50, description="시/도")
    region_sigungu: Optional[str] = Field(None, max_length=50, description="시/군/구")
    disability_type: Optional[DisabilityTypeEnum] = Field(None, description="장애 유형")

    # 체력 측정 항목
    height: Optional[float] = Field(None, ge=50, le=250, description="신장 (cm)")
    weight: Optional[float] = Field(None, ge=10, le=200, description="체중 (kg)")
    grip_strength: Optional[float] = Field(None, ge=0, le=100, description="악력 (kg)")
    sit_ups: Optional[int] = Field(None, ge=0, le=200, description="윗몸일으키기 (회/분)")
    standing_long_jump: Optional[float] = Field(None, ge=0, le=400, description="제자리멀리뛰기 (cm)")
    shuttle_run_20m: Optional[int] = Field(None, ge=0, le=200, description="왕복오래달리기 (회)")
    sit_and_reach: Optional[float] = Field(None, ge=-50, le=100, description="좌전굴 (cm)")

    class Config:
        json_schema_extra = {
            "example": {
                "age": 15,
                "grade": "중3",
                "gender": "M",
                "region_sido": "서울특별시",
                "region_sigungu": "강서구",
                "grip_strength": 32.5,
                "sit_ups": 45,
                "standing_long_jump": 210,
                "shuttle_run_20m": 12,
                "sit_and_reach": 15.2,
                "height": 170.3,
                "weight": 60.0
            }
        }


class TalentScoreItem(BaseModel):
    """종목별 재능 점수"""
    sport: str
    score: float
    percentile: float
    grade_level: GradeLevelEnum
    comment: Optional[str] = None


class TalentScoreResponse(BaseModel):
    """재능 진단 응답"""
    test_id: int
    scores: List[TalentScoreItem]
    comment: Optional[str] = None  # 전체 코멘트 (Gemini 생성)

    class Config:
        from_attributes = True


class TalentTestListItem(BaseModel):
    """테스트 목록 아이템"""
    id: int
    age: int
    grade: Optional[str]
    gender: str
    region_sido: Optional[str]
    region_sigungu: Optional[str]
    created_at: datetime
    top_scores: List[TalentScoreItem]

    class Config:
        from_attributes = True


class TalentTestListResponse(BaseModel):
    """테스트 목록 응답"""
    items: List[TalentTestListItem]
    total: int
