from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.user import UserRole


class SignupRequest(BaseModel):
    """회원가입 요청"""
    name: str = Field(..., min_length=2, max_length=100, description="이름")
    email: EmailStr = Field(..., description="이메일")
    password: str = Field(..., min_length=6, max_length=100, description="비밀번호")
    role: UserRole = Field(default=UserRole.student, description="회원 유형")
    school_or_org: Optional[str] = Field(None, max_length=200, description="학교/소속")
    region_sido: Optional[str] = Field(None, max_length=50, description="시/도")
    region_sigungu: Optional[str] = Field(None, max_length=50, description="시/군/구")


class LoginRequest(BaseModel):
    """로그인 요청"""
    email: EmailStr = Field(..., description="이메일")
    password: str = Field(..., description="비밀번호")


class UserResponse(BaseModel):
    """사용자 정보 응답"""
    id: int
    name: str
    email: str
    role: UserRole
    school_or_org: Optional[str] = None
    region_sido: Optional[str] = None
    region_sigungu: Optional[str] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """토큰 응답"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
