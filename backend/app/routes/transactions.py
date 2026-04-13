from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.transaccion import Transaction
from app.models.exchange_rate_log import ExchangeRateLog
from app.schemas.transaccion import TransactionCreate, TransactionResponse

from app.services.exchange_rate import get_exchange_rate
from app.models.user import User
from app.routes.dependencias import get_current_user, get_emisor, get_receptor

router = APIRouter(prefix="/transactions", tags=["transactions"])

# Emisor registra envío en USD
@router.post("/send", response_model=TransactionResponse)
async def send_money(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_emisor)
):
    rate = await get_exchange_rate()
    amount_gtq = round(data.amount_usd * rate, 2)

    transaction = Transaction(
        amount_usd=data.amount_usd,
        amount_gtq=amount_gtq,
        exchange_rate=rate,
        note=data.note,
        status="pendiente",
        user_id=current_user.id
    )
    db.add(transaction)
    db.flush()

    log = ExchangeRateLog(
        rate=rate,
        from_currency="USD",
        to_currency="GTQ",
        transaction_id=transaction.id
    )
    db.add(log)
    db.commit()
    db.refresh(transaction)
    return transaction

# Receptor solicita monto en GTQ
@router.post("/request", response_model=TransactionResponse)
async def request_money(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_receptor)
):
    rate = await get_exchange_rate()
    amount_usd = round(data.amount_gtq / rate, 2)

    transaction = Transaction(
        amount_usd=amount_usd,
        amount_gtq=data.amount_gtq,
        exchange_rate=rate,
        note=data.note,
        status="pendiente",
        user_id=current_user.id
    )
    db.add(transaction)
    db.flush()

    log = ExchangeRateLog(
        rate=rate,
        from_currency="GTQ",
        to_currency="USD",
        transaction_id=transaction.id
    )
    db.add(log)
    db.commit()
    db.refresh(transaction)
    return transaction

# Historial con paginación
@router.get("/history", response_model=list[TransactionResponse])
def get_history(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    offset = (page - 1) * limit
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return transactions

# Receptor confirma recepción
@router.patch("/{transaction_id}/confirm", response_model=TransactionResponse)
def confirm_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_receptor)
):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    if transaction.status == "confirmado":
        raise HTTPException(status_code=400, detail="La transacción ya fue confirmada")
    
    transaction.status = "confirmado"
    db.commit()
    db.refresh(transaction)
    return transaction