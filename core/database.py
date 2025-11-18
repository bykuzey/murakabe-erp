"""
MinimalERP - Database Module

SQLAlchemy async database configuration and session management.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, DateTime, Boolean, String
from datetime import datetime
from typing import AsyncGenerator
import pytz

from core.config import settings

# Create async engine
# Handle different database types
db_url = settings.DATABASE_URL
if "postgresql" in db_url:
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(
        db_url,
        echo=settings.SHOW_SQL_QUERIES,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_pre_ping=True,
    )
else:
    # SQLite doesn't support pool_size and max_overflow
    engine = create_async_engine(
        db_url,
        echo=settings.SHOW_SQL_QUERIES,
    )

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


def get_istanbul_time():
    """Get current time in Istanbul timezone"""
    return datetime.now(pytz.timezone('Europe/Istanbul'))


class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), default=get_istanbul_time, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_istanbul_time, onupdate=get_istanbul_time, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Audit fields
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    deleted_by = Column(Integer, nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    def soft_delete(self, user_id: int = None):
        """Soft delete the record"""
        self.is_deleted = True
        self.is_active = False
        self.deleted_at = get_istanbul_time()
        self.deleted_by = user_id

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


# Dependency for getting database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Database session dependency.

    Usage in FastAPI endpoints:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """Drop all database tables (use with caution!)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
