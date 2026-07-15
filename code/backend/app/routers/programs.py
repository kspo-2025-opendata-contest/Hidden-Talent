from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from app.database import get_db
from app.schemas.program import ProgramResponse, ProgramListResponse
from app.models.program import Program


router = APIRouter()

# 장애인 체육 프로그램 식별 키워드 (프로그램명/시설명/대상 그룹)
DISABILITY_KEYWORDS = ["장애", "파라", "휠체어", "보치아", "골볼"]


@router.get("", response_model=ProgramListResponse)
async def get_programs(
    db: Session = Depends(get_db),
    region_sido: Optional[str] = Query(None, description="시/도 필터"),
    region_sigungu: Optional[str] = Query(None, description="시/군/구 필터"),
    program_type: Optional[str] = Query(None, description="프로그램 유형 필터"),
    target_group: Optional[str] = Query(None, description="대상 그룹 필터 (청소년, 성인 등)"),
    industry_name: Optional[str] = Query(None, description="업종명 필터 (수영장, 체육관 등)"),
    keyword: Optional[str] = Query(None, description="프로그램명 또는 시설명 검색"),
    disability: Optional[bool] = Query(None, description="장애인 체육 프로그램만 조회 (True 시 장애인/파라 등 접근성 프로그램으로 한정)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 개수"),
):
    """
    프로그램 목록 조회

    다양한 필터와 검색 조건으로 청소년/유아동 이용가능 프로그램을 조회합니다.
    """
    query = db.query(Program)

    # 필터 적용
    if region_sido:
        query = query.filter(Program.region_sido == region_sido)
    if region_sigungu:
        query = query.filter(Program.region_sigungu == region_sigungu)
    if program_type:
        query = query.filter(Program.program_type.ilike(f"%{program_type}%"))
    if target_group:
        query = query.filter(Program.target_group.ilike(f"%{target_group}%"))
    if industry_name:
        query = query.filter(Program.industry_name.ilike(f"%{industry_name}%"))
    if keyword:
        query = query.filter(
            (Program.program_name.ilike(f"%{keyword}%")) |
            (Program.facility_name.ilike(f"%{keyword}%"))
        )
    # 장애인 체육 프로그램으로 한정 (장애 학생 맞춤 추천용)
    if disability:
        dis_conds = []
        for kw in DISABILITY_KEYWORDS:
            like = f"%{kw}%"
            dis_conds.append(Program.program_name.ilike(like))
            dis_conds.append(Program.facility_name.ilike(like))
            dis_conds.append(Program.target_group.ilike(like))
        query = query.filter(or_(*dis_conds))

    # 총 개수
    total = query.count()

    # 페이지네이션
    offset = (page - 1) * limit
    programs = query.order_by(Program.id.desc()).offset(offset).limit(limit).all()

    return ProgramListResponse(
        items=[ProgramResponse.model_validate(p) for p in programs],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/{program_id}", response_model=ProgramResponse)
async def get_program_detail(
    program_id: int,
    db: Session = Depends(get_db),
):
    """
    프로그램 상세 조회
    """
    program = db.query(Program).filter(Program.id == program_id).first()
    if not program:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="프로그램을 찾을 수 없습니다."
        )
    return ProgramResponse.model_validate(program)


@router.get("/regions/list")
async def get_program_regions(
    db: Session = Depends(get_db),
):
    """
    프로그램이 존재하는 지역 목록 조회
    """
    regions = db.query(
        Program.region_sido,
        Program.region_sigungu
    ).distinct().filter(
        Program.region_sido.isnot(None)
    ).order_by(Program.region_sido, Program.region_sigungu).limit(500).all()

    result = {}
    for sido, sigungu in regions:
        if sido not in result:
            result[sido] = []
        if sigungu and sigungu not in result[sido]:
            result[sido].append(sigungu)

    return result


@router.get("/types/list")
async def get_program_types(
    db: Session = Depends(get_db),
):
    """
    프로그램 유형 목록 조회
    """
    types = db.query(Program.program_type).distinct().filter(
        Program.program_type.isnot(None)
    ).limit(100).all()

    return [t[0] for t in types if t[0]]
