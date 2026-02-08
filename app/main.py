import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.userdb import (
    Transaction,
    create_db_and_tables,
    get_async_session,
    User,
)

from app.schemas import (
    UserRead,
    UserCreate,
    UserUpdate,
    TransactionCreate,
    TransactionResponse,
)

from app.routes.users import auth_backend, current_active_user, fastapi_users


# ---------- APP LIFESPAN ----------


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


# ---------- CORS (Frontend-ready) ----------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- AUTH ROUTES ----------

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


# ---------- HELPERS ----------


def to_transaction_response(
    trx: Transaction,
    user: User,
) -> TransactionResponse:
    return TransactionResponse(
        id=str(trx.id),
        user_id=str(trx.user_id),
        email=user.email,
        description=trx.description,
        amount=trx.amount,
        trx_type=trx.trx_type,
        created_at=trx.created_at,
        is_owner=True,
    )


# ---------- TRANSACTIONS ----------


@app.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=201,
)
async def add_transaction(
    transaction_in: TransactionCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    trx = Transaction(
        user_id=user.id,
        description=transaction_in.description,
        amount=transaction_in.amount,
        trx_type=transaction_in.trx_type,
    )

    session.add(trx)
    await session.commit()
    await session.refresh(trx)

    return to_transaction_response(trx, user)


@app.get(
    "/transactions",
    response_model=list[TransactionResponse],
)
async def get_transactions(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(
        select(Transaction)
        .where(Transaction.user_id == user.id)
        .order_by(Transaction.created_at.desc())
    )

    transactions = result.scalars().all()
    return [to_transaction_response(trx, user) for trx in transactions]


@app.delete(
    "/transactions/{transaction_id}",
    status_code=204,
)
async def delete_transaction(
    transaction_id: str,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        trx_id = uuid.UUID(transaction_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid transaction ID")

    result = await session.execute(select(Transaction).where(Transaction.id == trx_id))
    trx = result.scalars().first()

    if not trx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if trx.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    await session.delete(trx)
    await session.commit()
