from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings


# SQLite와 PostgreSQL 모두 지원
db_url = settings.database_url_sync
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        db_url,
        echo=settings.DEBUG,
        connect_args=connect_args
    )
else:
    engine = create_engine(
        db_url,
        echo=settings.DEBUG,
        pool_pre_ping=True
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """SQLAlchemy 모델 기반 클래스"""
    pass


def get_db():
    """Dependency: DB 세션 주입"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
