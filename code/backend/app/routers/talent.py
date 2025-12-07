from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.schemas.talent import (
    TalentTestRequest,
    TalentScoreResponse,
    TalentScoreItem,
    TalentTestListItem,
    TalentTestListResponse,
)
from app.models.talent import TalentTest, TalentScore, GradeLevel, Gender, DisabilityType
from app.models.user import User
from app.dependencies import get_current_user, get_current_user_optional
from app.services.scoring_service import calculate_all_sport_scores
from app.services.gemini_client import generate_talent_comment


router = APIRouter()


@router.post("/score", response_model=TalentScoreResponse, status_code=status.HTTP_201_CREATED)
async def create_talent_score(
    request: TalentTestRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    재능 진단 API

    체력 측정 데이터를 입력받아 종목별 재능 점수를 계산합니다.
    로그인하지 않아도 사용 가능하며, 로그인 시 기록이 저장됩니다.
    """
    # BMI 계산
    bmi = None
    if request.height and request.weight:
        height_m = request.height / 100
        bmi = round(request.weight / (height_m ** 2), 2)

    # TalentTest 레코드 생성
    talent_test = TalentTest(
        user_id=current_user.id if current_user else None,
        age=request.age,
        grade=request.grade,
        gender=Gender(request.gender.value),
        region_sido=request.region_sido,
        region_sigungu=request.region_sigungu,
        disability_type=DisabilityType(request.disability_type.value) if request.disability_type else None,
        height=request.height,
        weight=request.weight,
        bmi=bmi,
        grip_strength=request.grip_strength,
        sit_ups=request.sit_ups,
        standing_long_jump=request.standing_long_jump,
        shuttle_run_20m=request.shuttle_run_20m,
        sit_and_reach=request.sit_and_reach,
    )
    db.add(talent_test)
    db.commit()
    db.refresh(talent_test)

    # 종목별 점수 계산 (장애 유형 포함)
    sport_scores = calculate_all_sport_scores(
        grip_strength=request.grip_strength,
        sit_ups=request.sit_ups,
        standing_long_jump=request.standing_long_jump,
        shuttle_run_20m=request.shuttle_run_20m,
        sit_and_reach=request.sit_and_reach,
        disability_type=request.disability_type.value if request.disability_type else None,
    )

    # TalentScore 레코드들 생성
    score_items = []
    for score_data in sport_scores:
        talent_score = TalentScore(
            talent_test_id=talent_test.id,
            sport=score_data["sport"],
            score=score_data["score"],
            percentile=score_data["percentile"],
            grade_level=GradeLevel(score_data["grade_level"]),
        )
        db.add(talent_score)
        score_items.append(TalentScoreItem(
            sport=score_data["sport"],
            score=score_data["score"],
            percentile=score_data["percentile"],
            grade_level=score_data["grade_level"],
        ))

    db.commit()

    # Gemini로 코멘트 생성 (비동기, 실패해도 무시)
    overall_comment = None
    try:
        overall_comment = await generate_talent_comment(
            scores=sport_scores,
            user_profile={
                "age": request.age,
                "gender": request.gender.value,
                "region_sido": request.region_sido,
            }
        )
    except Exception:
        pass

    return TalentScoreResponse(
        test_id=talent_test.id,
        scores=score_items,
        comment=overall_comment,
    )


@router.get("/tests", response_model=TalentTestListResponse)
async def get_talent_tests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0,
):
    """
    과거 테스트 목록 조회

    로그인한 사용자의 체력 측정 기록과 상위 3개 종목 점수를 반환합니다.
    """
    # 총 개수 조회
    total = db.query(TalentTest).filter(
        TalentTest.user_id == current_user.id
    ).count()

    # 테스트 목록 조회
    tests = db.query(TalentTest).filter(
        TalentTest.user_id == current_user.id
    ).order_by(TalentTest.created_at.desc()).offset(offset).limit(limit).all()

    items = []
    for test in tests:
        # 상위 3개 점수 조회
        top_scores = db.query(TalentScore).filter(
            TalentScore.talent_test_id == test.id
        ).order_by(TalentScore.score.desc()).limit(3).all()

        items.append(TalentTestListItem(
            id=test.id,
            age=test.age,
            grade=test.grade,
            gender=test.gender.value,
            region_sido=test.region_sido,
            region_sigungu=test.region_sigungu,
            created_at=test.created_at,
            top_scores=[
                TalentScoreItem(
                    sport=s.sport,
                    score=s.score,
                    percentile=s.percentile or 0,
                    grade_level=s.grade_level.value if s.grade_level else "medium",
                )
                for s in top_scores
            ]
        ))

    return TalentTestListResponse(
        items=items,
        total=total,
    )


@router.get("/tests/{test_id}", response_model=TalentScoreResponse)
async def get_talent_test_detail(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    특정 테스트 상세 조회

    테스트 ID로 상세 결과를 조회합니다.
    """
    test = db.query(TalentTest).filter(TalentTest.id == test_id).first()

    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="테스트를 찾을 수 없습니다."
        )

    # 로그인한 사용자의 테스트인지 확인 (비로그인 테스트도 조회 가능)
    if test.user_id and current_user and test.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="접근 권한이 없습니다."
        )

    scores = db.query(TalentScore).filter(
        TalentScore.talent_test_id == test_id
    ).order_by(TalentScore.score.desc()).all()

    return TalentScoreResponse(
        test_id=test.id,
        scores=[
            TalentScoreItem(
                sport=s.sport,
                score=s.score,
                percentile=s.percentile or 0,
                grade_level=s.grade_level.value if s.grade_level else "medium",
                comment=s.comment,
            )
            for s in scores
        ],
    )
