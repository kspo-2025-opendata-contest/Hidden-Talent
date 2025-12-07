"""문의하기 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.dependencies import get_current_user, get_current_user_optional
from app.models.user import User, UserRole
from app.models.inquiry import Inquiry, InquiryStatus
from app.schemas.inquiry import (
    InquiryCreate,
    InquiryReply,
    InquiryResponse,
    InquiryListResponse,
)

router = APIRouter(prefix="/api/inquiry", tags=["inquiry"])


@router.post("", response_model=InquiryResponse)
def create_inquiry(
    data: InquiryCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """문의 생성 (비회원도 가능)"""
    inquiry = Inquiry(
        user_id=current_user.id if current_user else None,
        name=data.name,
        email=data.email,
        subject=data.subject,
        content=data.content,
        status=InquiryStatus.pending,
    )
    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)
    return inquiry


@router.get("", response_model=InquiryListResponse)
def list_inquiries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[InquiryStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """문의 목록 조회 (관리자 전용)"""
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="관리자만 접근할 수 있습니다")

    query = db.query(Inquiry)

    if status:
        query = query.filter(Inquiry.status == status)

    total = query.count()
    inquiries = (
        query.order_by(desc(Inquiry.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return InquiryListResponse(
        inquiries=inquiries,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{inquiry_id}", response_model=InquiryResponse)
def get_inquiry(
    inquiry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """문의 상세 조회 (관리자 전용)"""
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="관리자만 접근할 수 있습니다")

    inquiry = db.query(Inquiry).filter(Inquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="문의를 찾을 수 없습니다")

    return inquiry


@router.post("/{inquiry_id}/reply", response_model=InquiryResponse)
def reply_inquiry(
    inquiry_id: int,
    data: InquiryReply,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """문의에 답변 (관리자 전용)"""
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="관리자만 접근할 수 있습니다")

    inquiry = db.query(Inquiry).filter(Inquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="문의를 찾을 수 없습니다")

    inquiry.admin_reply = data.admin_reply
    inquiry.status = InquiryStatus.answered
    inquiry.replied_at = datetime.utcnow()
    db.commit()
    db.refresh(inquiry)

    return inquiry


@router.patch("/{inquiry_id}/close", response_model=InquiryResponse)
def close_inquiry(
    inquiry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """문의 종료 (관리자 전용)"""
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="관리자만 접근할 수 있습니다")

    inquiry = db.query(Inquiry).filter(Inquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="문의를 찾을 수 없습니다")

    inquiry.status = InquiryStatus.closed
    db.commit()
    db.refresh(inquiry)

    return inquiry


@router.get("/stats/summary")
def get_inquiry_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """문의 통계 (관리자 전용)"""
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="관리자만 접근할 수 있습니다")

    total = db.query(Inquiry).count()
    pending = db.query(Inquiry).filter(Inquiry.status == InquiryStatus.pending).count()
    answered = db.query(Inquiry).filter(Inquiry.status == InquiryStatus.answered).count()
    closed = db.query(Inquiry).filter(Inquiry.status == InquiryStatus.closed).count()

    return {
        "total": total,
        "pending": pending,
        "answered": answered,
        "closed": closed,
    }
