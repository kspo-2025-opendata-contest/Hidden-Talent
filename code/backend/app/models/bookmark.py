from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, func, Index
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class TargetType(str, enum.Enum):
    """북마크 대상 유형"""
    program = "program"
    facility = "facility"
    coach = "coach"


class Bookmark(Base):
    """사용자 북마크"""
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_type = Column(Enum(TargetType), nullable=False)
    target_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="bookmarks")

    # Indexes
    __table_args__ = (
        Index("idx_bookmarks_user", "user_id"),
        Index("idx_bookmarks_target", "target_type", "target_id"),
    )


class Notification(Base):
    """사용자 알림"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(String(1000), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")

    # Indexes
    __table_args__ = (
        Index("idx_notifications_user", "user_id"),
    )
