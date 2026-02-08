from pydantic import BaseModel, ConfigDict
from fastapi_users import schemas
from typing import Optional
from enum import Enum
import uuid
import datetime


# ---------- TRANSACTIONS ----------


class TransactionType(str, Enum):
    inflow = "inflow"
    outflow = "outflow"


class TransactionCreate(BaseModel):
    description: Optional[str] = None
    amount: float
    trx_type: TransactionType


class TransactionResponse(BaseModel):
    id: str
    user_id: str
    email: str
    description: Optional[str]
    amount: float
    trx_type: TransactionType
    created_at: datetime.datetime
    is_owner: bool

    model_config = ConfigDict(from_attributes=True)


# ---------- USERS (FastAPI Users) ----------


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass
