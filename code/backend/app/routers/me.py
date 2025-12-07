from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.bookmark import Bookmark, Notification, TargetType
from app.models.talent import TalentTest
from app.models.program import Program
from app.schemas.bookmark import (
    BookmarkCreate,
    BookmarkResponse,
    BookmarkListResponse,
    NotificationResponse,
    NotificationListResponse,
    MyOverviewResponse,
    TargetTypeEnum,
)
from app.schemas.auth import UserResponse


class ProfileUpdateRequest(BaseModel):
    """프로필 수정 요청"""
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="이름")
    school_or_org: Optional[str] = Field(None, max_length=200, description="학교/소속")
    region_sido: Optional[str] = Field(None, max_length=50, description="시/도")
    region_sigungu: Optional[str] = Field(None, max_length=50, description="시/군/구")


router = APIRouter()


@router.get("/overview", response_model=MyOverviewResponse)
async def get_my_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    마이페이지 개요

    사용자의 전체 활동 요약 정보를 반환합니다.
    """
    # 재능 진단 통계
    talent_test_count = db.query(TalentTest).filter(
        TalentTest.user_id == current_user.id
    ).count()

    latest_test = db.query(TalentTest).filter(
        TalentTest.user_id == current_user.id
    ).order_by(TalentTest.created_at.desc()).first()

    # 북마크 통계
    bookmark_count = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id
    ).count()

    bookmark_by_type = db.query(
        Bookmark.target_type,
        func.count(Bookmark.id).label("count")
    ).filter(
        Bookmark.user_id == current_user.id
    ).group_by(Bookmark.target_type).all()

    bookmark_type_counts = {t.value: c for t, c in bookmark_by_type}

    # 알림 통계
    notification_count = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).count()

    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()

    return MyOverviewResponse(
        user={
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role.value if current_user.role else None,
            "region_sido": current_user.region_sido,
            "region_sigungu": current_user.region_sigungu,
            "school_or_org": current_user.school_or_org,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        },
        talent_tests={
            "total": talent_test_count,
            "latest_at": latest_test.created_at.isoformat() if latest_test else None,
        },
        bookmarks={
            "total": bookmark_count,
            "by_type": bookmark_type_counts,
        },
        notifications={
            "total": notification_count,
            "unread": unread_count,
        },
    )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    data: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    프로필 수정

    사용자 프로필 정보를 수정합니다.
    """
    if data.name is not None:
        current_user.name = data.name
    if data.school_or_org is not None:
        current_user.school_or_org = data.school_or_org
    if data.region_sido is not None:
        current_user.region_sido = data.region_sido
    if data.region_sigungu is not None:
        current_user.region_sigungu = data.region_sigungu

    db.commit()
    db.refresh(current_user)

    return UserResponse.model_validate(current_user)


@router.get("/bookmarks", response_model=BookmarkListResponse)
async def get_my_bookmarks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    target_type: Optional[TargetTypeEnum] = Query(None, description="대상 유형 필터"),
    limit: int = Query(50, ge=1, le=200, description="조회 개수"),
    offset: int = Query(0, ge=0, description="시작 위치"),
):
    """
    북마크 목록 조회

    사용자가 저장한 북마크 목록을 반환합니다.
    """
    query = db.query(Bookmark).filter(Bookmark.user_id == current_user.id)

    if target_type:
        query = query.filter(Bookmark.target_type == target_type.value)

    total = query.count()
    bookmarks = query.order_by(Bookmark.created_at.desc()).offset(offset).limit(limit).all()

    # 북마크된 대상의 상세 정보 조회
    items = []
    for b in bookmarks:
        target_name = None
        target_detail = None

        if b.target_type == TargetType.program:
            program = db.query(Program).filter(Program.id == b.target_id).first()
            if program:
                target_name = program.program_name
                target_detail = f"{program.region_sido} {program.region_sigungu or ''}"

        items.append(BookmarkResponse(
            id=b.id,
            target_type=TargetTypeEnum(b.target_type.value),
            target_id=b.target_id,
            created_at=b.created_at,
            target_name=target_name,
            target_detail=target_detail,
        ))

    return BookmarkListResponse(items=items, total=total)


@router.post("/bookmarks", response_model=BookmarkResponse)
async def create_bookmark(
    data: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    북마크 추가

    프로그램, 시설 등을 북마크에 추가합니다.
    """
    # 중복 체크
    existing = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id,
        Bookmark.target_type == data.target_type.value,
        Bookmark.target_id == data.target_id,
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="이미 북마크된 항목입니다")

    # 대상 존재 확인 (프로그램만)
    target_name = None
    target_detail = None

    if data.target_type == TargetTypeEnum.program:
        program = db.query(Program).filter(Program.id == data.target_id).first()
        if not program:
            raise HTTPException(status_code=404, detail="프로그램을 찾을 수 없습니다")
        target_name = program.program_name
        target_detail = f"{program.region_sido} {program.region_sigungu or ''}"

    bookmark = Bookmark(
        user_id=current_user.id,
        target_type=data.target_type.value,
        target_id=data.target_id,
    )
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)

    return BookmarkResponse(
        id=bookmark.id,
        target_type=TargetTypeEnum(bookmark.target_type.value),
        target_id=bookmark.target_id,
        created_at=bookmark.created_at,
        target_name=target_name,
        target_detail=target_detail,
    )


@router.delete("/bookmarks/{bookmark_id}")
async def delete_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    북마크 삭제
    """
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == current_user.id,
    ).first()

    if not bookmark:
        raise HTTPException(status_code=404, detail="북마크를 찾을 수 없습니다")

    db.delete(bookmark)
    db.commit()

    return {"message": "북마크가 삭제되었습니다", "id": bookmark_id}


@router.get("/notifications", response_model=NotificationListResponse)
async def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    unread_only: bool = Query(False, description="읽지 않은 알림만"),
    limit: int = Query(50, ge=1, le=200, description="조회 개수"),
    offset: int = Query(0, ge=0, description="시작 위치"),
):
    """
    알림 목록 조회
    """
    query = db.query(Notification).filter(Notification.user_id == current_user.id)

    if unread_only:
        query = query.filter(Notification.is_read == False)

    total = query.count()
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()

    notifications = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()

    return NotificationListResponse(
        items=[NotificationResponse.model_validate(n) for n in notifications],
        total=total,
        unread_count=unread_count,
    )


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    알림 읽음 처리
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="알림을 찾을 수 없습니다")

    notification.is_read = True
    db.commit()

    return {"message": "알림이 읽음 처리되었습니다", "id": notification_id}


@router.post("/notifications/read-all")
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    모든 알림 읽음 처리
    """
    updated = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).update({"is_read": True})

    db.commit()

    return {"message": f"{updated}개의 알림이 읽음 처리되었습니다", "count": updated}
