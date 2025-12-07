from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import re
from app.database import get_db
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, UserResponse
from app.services import auth_service
from app.dependencies import get_current_user
from app.models.user import User


router = APIRouter()


class EmailCheckRequest(BaseModel):
    email: EmailStr


class EmailCheckResponse(BaseModel):
    available: bool
    message: str


def validate_password(password: str) -> tuple[bool, str]:
    """
    비밀번호 요건 검증

    요건:
    - 최소 8자 이상
    - 영문 대문자 1개 이상
    - 영문 소문자 1개 이상
    - 숫자 1개 이상
    - 특수문자 1개 이상

    Returns:
        (valid: bool, message: str)
    """
    if len(password) < 8:
        return False, "비밀번호는 8자 이상이어야 합니다."

    if not re.search(r'[A-Z]', password):
        return False, "비밀번호에 영문 대문자를 포함해야 합니다."

    if not re.search(r'[a-z]', password):
        return False, "비밀번호에 영문 소문자를 포함해야 합니다."

    if not re.search(r'\d', password):
        return False, "비밀번호에 숫자를 포함해야 합니다."

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "비밀번호에 특수문자(!@#$%^&*() 등)를 포함해야 합니다."

    return True, "사용 가능한 비밀번호입니다."


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    회원가입 API

    - name: 이름 (2-100자)
    - email: 이메일 (고유)
    - password: 비밀번호 (8자 이상, 대/소문자, 숫자, 특수문자 조합)
    - role: 회원 유형 (student/parent/coach/official)
    - school_or_org: 학교/소속 (선택)
    - region_sido: 시/도 (선택)
    - region_sigungu: 시/군/구 (선택)
    """
    # 비밀번호 요건 검증
    is_valid, message = validate_password(request.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    # 이메일 중복 확인
    existing_user = auth_service.get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다."
        )

    # 사용자 생성
    user = auth_service.create_user(
        db=db,
        name=request.name,
        email=request.email,
        password=request.password,
        role=request.role,
        school_or_org=request.school_or_org,
        region_sido=request.region_sido,
        region_sigungu=request.region_sigungu
    )

    # JWT 토큰 생성
    access_token = auth_service.create_access_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    로그인 API

    - email: 이메일
    - password: 비밀번호
    """
    user = auth_service.authenticate_user(db, request.email, request.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_access_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    현재 로그인한 사용자 정보 조회

    Authorization 헤더에 Bearer 토큰 필요
    """
    return UserResponse.model_validate(current_user)


@router.post("/check-email", response_model=EmailCheckResponse)
async def check_email(request: EmailCheckRequest, db: Session = Depends(get_db)):
    """
    이메일 중복 확인 API

    - email: 확인할 이메일 주소
    - 반환: available (사용 가능 여부), message (메시지)
    """
    existing_user = auth_service.get_user_by_email(db, request.email)
    if existing_user:
        return EmailCheckResponse(
            available=False,
            message="이미 사용 중인 이메일입니다."
        )
    return EmailCheckResponse(
        available=True,
        message="사용 가능한 이메일입니다."
    )
