"""문의하기 모델"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, func, Index
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class InquiryStatus(str, enum.Enum):
    """문의 상태"""
    pending = "pending"      # 대기중
    answered = "answered"    # 답변완료
    closed = "closed"        # 종료


class Inquiry(Base):
    """문의 모델"""
    __tablename__ = "inquiries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 비회원도 문의 가능
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    subject = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Enum(InquiryStatus), default=InquiryStatus.pending, nullable=False)
    admin_reply = Column(Text, nullable=True)
    replied_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", backref="inquiries")

    # Indexes
    __table_args__ = (
        Index("idx_inquiries_status", "status"),
        Index("idx_inquiries_created_at", "created_at"),
    )
