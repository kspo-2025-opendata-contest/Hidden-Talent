from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from app.database import get_db
from app.schemas.program import FacilityStatsResponse, FacilityStatsListResponse
from app.models.facility import FacilityStats


router = APIRouter()


@router.get("", response_model=FacilityStatsListResponse)
async def get_facility_stats(
    db: Session = Depends(get_db),
    region_sido: Optional[str] = Query(None, description="시/도 필터"),
    region_sigungu: Optional[str] = Query(None, description="시/군/구 필터"),
    base_ym: Optional[str] = Query(None, description="기준년월 필터 (예: 202507)"),
    limit: int = Query(100, ge=1, le=500, description="조회 개수"),
):
    """
    지역별 공공체육시설 보급현황 통계 조회

    지역별 시설 수, 인구 수, 1인당 시설 수 등의 통계 데이터를 조회합니다.
    """
    query = db.query(FacilityStats)

    # 필터 적용
    if region_sido:
        query = query.filter(FacilityStats.region_sido == region_sido)
    if region_sigungu:
        query = query.filter(FacilityStats.region_sigungu == region_sigungu)
    if base_ym:
        query = query.filter(FacilityStats.base_ym == base_ym)

    # 총 개수
    total = query.count()

    # 최신 데이터 우선
    stats = query.order_by(FacilityStats.base_ym.desc()).limit(limit).all()

    return FacilityStatsListResponse(
        items=[FacilityStatsResponse.model_validate(s) for s in stats],
        total=total,
    )


@router.get("/regions")
async def get_facility_regions(
    db: Session = Depends(get_db),
):
    """
    시설 통계가 존재하는 지역 목록 조회
    """
    regions = db.query(
        FacilityStats.region_sido,
        FacilityStats.region_sigungu
    ).distinct().filter(
        FacilityStats.region_sido.isnot(None)
    ).order_by(FacilityStats.region_sido, FacilityStats.region_sigungu).limit(500).all()

    result = {}
    for sido, sigungu in regions:
        if sido not in result:
            result[sido] = []
        if sigungu and sigungu not in result[sido]:
            result[sido].append(sigungu)

    return result


@router.get("/summary")
async def get_facility_summary(
    db: Session = Depends(get_db),
    base_ym: Optional[str] = Query(None, description="기준년월 (미입력시 최신)"),
):
    """
    시설 현황 요약 통계

    전국 시설 수, 평균 1인당 시설 수 등의 요약 정보를 반환합니다.
    """
    # 최신 기준년월 조회
    if not base_ym:
        latest = db.query(func.max(FacilityStats.base_ym)).scalar()
        base_ym = latest if latest else "202507"

    # 해당 기준년월의 통계 집계
    stats = db.query(FacilityStats).filter(FacilityStats.base_ym == base_ym).all()

    if not stats:
        return {
            "base_ym": base_ym,
            "total_regions": 0,
            "total_facilities": 0,
            "total_population": 0,
            "avg_facility_per_person": 0,
        }

    total_facilities = sum(s.facility_count or 0 for s in stats)
    total_population = sum(s.population or 0 for s in stats)
    avg_facility_per_person = total_facilities / total_population if total_population > 0 else 0

    # 시도별 집계
    sido_summary = {}
    for s in stats:
        sido = s.region_sido
        if sido not in sido_summary:
            sido_summary[sido] = {"facility_count": 0, "population": 0, "region_count": 0}
        sido_summary[sido]["facility_count"] += s.facility_count or 0
        sido_summary[sido]["population"] += s.population or 0
        sido_summary[sido]["region_count"] += 1

    return {
        "base_ym": base_ym,
        "total_regions": len(stats),
        "total_facilities": total_facilities,
        "total_population": total_population,
        "avg_facility_per_person": round(avg_facility_per_person, 6),
        "by_sido": sido_summary,
    }
