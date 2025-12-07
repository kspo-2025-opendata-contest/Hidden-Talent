"""문의하기 스키마"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.inquiry import InquiryStatus


class InquiryCreate(BaseModel):
    """문의 생성 요청"""
    name: str
    email: EmailStr
    subject: str
    content: str


class InquiryReply(BaseModel):
    """관리자 답변 요청"""
    admin_reply: str


class InquiryResponse(BaseModel):
    """문의 응답"""
    id: int
    user_id: Optional[int] = None
    name: str
    email: str
    subject: str
    content: str
    status: InquiryStatus
    admin_reply: Optional[str] = None
    replied_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InquiryListResponse(BaseModel):
    """문의 목록 응답"""
    inquiries: list[InquiryResponse]
    total: int
    page: int
    page_size: int
