"""
테스트 계정 생성 스크립트

일반 사용자와 관리자 계정을 생성합니다.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.services.auth_service import hash_password


def create_accounts():
    """테스트 계정 생성"""
    db = SessionLocal()

    try:
        # 일반 사용자 계정
        user_email = "user@suminjae.com"
        existing_user = db.query(User).filter(User.email == user_email).first()
        if not existing_user:
            user = User(
                name="테스트 사용자",
                email=user_email,
                password_hash=hash_password("User1234!"),
                role=UserRole.student,
                school_or_org="숨인재 중학교",
                region_sido="서울특별시",
                region_sigungu="강남구",
            )
            db.add(user)
            print(f"Created user account: {user_email}")
        else:
            existing_user.password_hash = hash_password("User1234!")
            print(f"Updated user account password: {user_email}")

        # 관리자 계정
        admin_email = "admin@suminjae.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if not existing_admin:
            admin = User(
                name="관리자",
                email=admin_email,
                password_hash=hash_password("Admin1234!"),
                role=UserRole.admin,
                school_or_org="숨인재 관리자",
                region_sido="서울특별시",
                region_sigungu="중구",
            )
            db.add(admin)
            print(f"Created admin account: {admin_email}")
        else:
            existing_admin.password_hash = hash_password("Admin1234!")
            print(f"Updated admin account password: {admin_email}")

        db.commit()
        print("\n=== Account Information ===")
        print("일반 사용자: user@suminjae.com / User1234!")
        print("관리자: admin@suminjae.com / Admin1234!")
        print("===========================")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_accounts()
