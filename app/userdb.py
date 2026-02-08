import os
import uuid
import datetime
from dotenv import load_dotenv
from enum import Enum
from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy import Column, Text, DateTime, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID

load_dotenv()

DATABASE_URL = os.getenv("USER_DATABASE_URL")
if DATABASE_URL is None:
    raise RuntimeError("USER_DATABASE_URL is not set in environment")


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    transactions = relationship("Transaction", back_populates="user")


class TransactionType(str, Enum):
    inflow = "inflow"
    outflow = "outflow"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    description = Column(Text, nullable=True)  # can be None
    amount = Column(Float, nullable=False)
    trx_type = Column(SQLEnum(TransactionType, native_enum=False), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="transactions")


# ---------- ENGINE & SESSION ----------

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# ---------- DATABASE HELPERS ----------


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
