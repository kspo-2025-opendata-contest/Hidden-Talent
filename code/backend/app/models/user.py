from sqlalchemy import Column, Integer, String, Enum, DateTime, func, Index
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    """사용자 역할"""
    student = "student"      # 학생
    parent = "parent"        # 학부모
    coach = "coach"          # 지도자
    official = "official"    # 기관 담당자
    admin = "admin"          # 관리자


class User(Base):
    """사용자 모델"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.student, nullable=False)
    school_or_org = Column(String(200), nullable=True)
    region_sido = Column(String(50), nullable=True)
    region_sigungu = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    talent_tests = relationship("TalentTest", back_populates="user")
    bookmarks = relationship("Bookmark", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

    # Indexes
    __table_args__ = (
        Index("idx_users_role", "role"),
    )
