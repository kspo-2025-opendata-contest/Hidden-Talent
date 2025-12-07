from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    """사용자 기본 스키마"""
    name: str
    email: EmailStr
    role: UserRole
    school_or_org: Optional[str] = None
    region_sido: Optional[str] = None
    region_sigungu: Optional[str] = None


class UserCreate(UserBase):
    """사용자 생성 스키마"""
    password: str


class UserUpdate(BaseModel):
    """사용자 수정 스키마"""
    name: Optional[str] = None
    school_or_org: Optional[str] = None
    region_sido: Optional[str] = None
    region_sigungu: Optional[str] = None


class UserInDB(UserBase):
    """DB 사용자 스키마"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
