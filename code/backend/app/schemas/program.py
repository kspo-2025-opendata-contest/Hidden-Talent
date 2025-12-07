from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class ProgramResponse(BaseModel):
    """프로그램 응답"""
    id: int
    facility_name: Optional[str] = None
    facility_type_name: Optional[str] = None
    industry_name: Optional[str] = None
    region_sido: Optional[str] = None
    region_sigungu: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    program_type: Optional[str] = None
    program_name: Optional[str] = None
    target_group: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    schedule_weekdays: Optional[str] = None
    schedule_time: Optional[str] = None
    capacity: Optional[int] = None
    price: Optional[float] = None
    homepage_url: Optional[str] = None

    class Config:
        from_attributes = True


class ProgramListResponse(BaseModel):
    """프로그램 목록 응답"""
    items: List[ProgramResponse]
    total: int
    page: int
    limit: int


class FacilityStatsResponse(BaseModel):
    """시설 통계 응답"""
    id: int
    base_ym: str
    region_sido: Optional[str] = None
    region_sigungu: Optional[str] = None
    facility_count: Optional[int] = None
    population: Optional[int] = None
    facility_per_person: Optional[float] = None
    rank: Optional[int] = None

    class Config:
        from_attributes = True


class FacilityStatsListResponse(BaseModel):
    """시설 통계 목록 응답"""
    items: List[FacilityStatsResponse]
    total: int
