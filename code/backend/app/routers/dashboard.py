from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from app.database import get_db
from app.models.facility import FacilityStats
from app.models.support import SupportStats
from app.models.coach import CoachStats
from app.models.program import Program
from app.models.talent import TalentTest, TalentScore


router = APIRouter()


@router.get("/summary")
async def get_dashboard_summary(
    db: Session = Depends(get_db),
):
    """
    대시보드 요약 통계

    전체 서비스 현황을 한눈에 볼 수 있는 요약 정보를 반환합니다.
    """
    # 프로그램 수
    program_count = db.query(Program).count()

    # 시설 통계 (최신 데이터)
    latest_facility_ym = db.query(func.max(FacilityStats.base_ym)).scalar()
    facility_stats = db.query(FacilityStats).filter(
        FacilityStats.base_ym == latest_facility_ym
    ).all() if latest_facility_ym else []

    total_facilities = sum(s.facility_count or 0 for s in facility_stats)

    # 스포츠강좌이용권 수혜자 수 (최신)
    latest_support_year = db.query(func.max(SupportStats.base_year)).scalar()
    support_stats = db.query(SupportStats).filter(
        SupportStats.base_year == latest_support_year
    ).all() if latest_support_year else []

    total_recipients = sum(s.recipient_count or 0 for s in support_stats)

    # 체육지도자 수 (최신 연도)
    latest_coach_year = db.query(func.max(CoachStats.qualification_year)).scalar()
    coach_stats = db.query(CoachStats).filter(
        CoachStats.qualification_year == latest_coach_year
    ).first() if latest_coach_year else None

    total_coaches = 0
    if coach_stats:
        total_coaches = (
            (coach_stats.health_exercise_manager or 0) +
            (coach_stats.professional_sports_1 or 0) +
            (coach_stats.professional_sports_2 or 0) +
            (coach_stats.living_sports_1 or 0) +
            (coach_stats.living_sports_2 or 0) +
            (coach_stats.youth_sports or 0) +
            (coach_stats.senior_sports or 0) +
            (coach_stats.disabled_sports_1 or 0) +
            (coach_stats.disabled_sports_2 or 0)
        )

    # 재능 진단 수
    talent_test_count = db.query(TalentTest).count()

    return {
        "programs": {
            "total": program_count,
        },
        "facilities": {
            "total": total_facilities,
            "base_ym": latest_facility_ym,
            "region_count": len(facility_stats),
        },
        "support": {
            "total_recipients": total_recipients,
            "base_year": latest_support_year,
        },
        "coaches": {
            "total": total_coaches,
            "latest_year": latest_coach_year,
        },
        "talent_tests": {
            "total": talent_test_count,
        },
    }


@router.get("/regions")
async def get_dashboard_regions(
    db: Session = Depends(get_db),
    base_ym: Optional[str] = Query(None, description="시설 통계 기준년월"),
):
    """
    지역별 통계

    각 시도별 시설, 프로그램, 스포츠강좌이용권 현황을 반환합니다.
    """
    # 최신 기준년월
    if not base_ym:
        base_ym = db.query(func.max(FacilityStats.base_ym)).scalar()

    # 시설 통계
    facility_stats = db.query(FacilityStats).filter(
        FacilityStats.base_ym == base_ym
    ).all() if base_ym else []

    # 시도별 집계
    regions = {}

    for s in facility_stats:
        sido = s.region_sido
        if not sido:
            continue
        if sido not in regions:
            regions[sido] = {
                "region_sido": sido,
                "facility_count": 0,
                "population": 0,
                "sigungu_count": 0,
            }
        regions[sido]["facility_count"] += s.facility_count or 0
        regions[sido]["population"] += s.population or 0
        regions[sido]["sigungu_count"] += 1

    # 프로그램 수 추가
    program_counts = db.query(
        Program.region_sido,
        func.count(Program.id).label("count")
    ).group_by(Program.region_sido).all()

    for sido, count in program_counts:
        if sido in regions:
            regions[sido]["program_count"] = count

    # 스포츠강좌이용권 수혜자 수 추가
    latest_support_year = db.query(func.max(SupportStats.base_year)).scalar()
    support_by_sido = db.query(
        SupportStats.region_sido,
        func.sum(SupportStats.recipient_count).label("total")
    ).filter(
        SupportStats.base_year == latest_support_year
    ).group_by(SupportStats.region_sido).all() if latest_support_year else []

    for sido, total in support_by_sido:
        if sido in regions:
            regions[sido]["support_recipients"] = int(total) if total else 0

    return {
        "base_ym": base_ym,
        "regions": list(regions.values()),
    }


@router.get("/coaches")
async def get_coach_stats(
    db: Session = Depends(get_db),
):
    """
    체육지도자 통계

    연도별 자격 유형별 체육지도자 취득 현황을 반환합니다.
    """
    stats = db.query(CoachStats).order_by(CoachStats.qualification_year.desc()).limit(20).all()

    return {
        "items": [
            {
                "year": s.qualification_year,
                "health_exercise_manager": s.health_exercise_manager,
                "professional_sports_1": s.professional_sports_1,
                "professional_sports_2": s.professional_sports_2,
                "living_sports_1": s.living_sports_1,
                "living_sports_2": s.living_sports_2,
                "youth_sports": s.youth_sports,
                "senior_sports": s.senior_sports,
                "disabled_sports_1": s.disabled_sports_1,
                "disabled_sports_2": s.disabled_sports_2,
            }
            for s in stats
        ],
        "total": len(stats),
    }
