from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TargetTypeEnum(str, Enum):
    """북마크 대상 유형"""
    program = "program"
    facility = "facility"
    coach = "coach"


class BookmarkCreate(BaseModel):
    """북마크 생성 요청"""
    target_type: TargetTypeEnum = Field(..., description="대상 유형")
    target_id: int = Field(..., description="대상 ID")


class BookmarkResponse(BaseModel):
    """북마크 응답"""
    id: int
    target_type: TargetTypeEnum
    target_id: int
    created_at: datetime
    # 연결된 데이터 정보 (프로그램명 등)
    target_name: Optional[str] = None
    target_detail: Optional[str] = None

    model_config = {"from_attributes": True}


class BookmarkListResponse(BaseModel):
    """북마크 목록 응답"""
    items: List[BookmarkResponse]
    total: int


class NotificationResponse(BaseModel):
    """알림 응답"""
    id: int
    title: str
    message: Optional[str] = None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    """알림 목록 응답"""
    items: List[NotificationResponse]
    total: int
    unread_count: int


class MyOverviewResponse(BaseModel):
    """마이페이지 개요 응답"""
    user: dict
    talent_tests: dict
    bookmarks: dict
    notifications: dict
