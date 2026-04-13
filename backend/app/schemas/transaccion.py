from pydantic import BaseModel, field_validator
from .exchange_rate import ExchangeRateLogResponse
from datetime import datetime

class TransactionCreate(BaseModel):
    amount_usd: float | None = None
    amount_gtq: float | None = None
    note: str | None = None

    @field_validator("amount_usd", "amount_gtq")
    def amount_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        return v

class TransactionResponse(BaseModel):
    id: int
    amount_usd: float
    amount_gtq: float
    exchange_rate: float
    status: str
    note: str | None
    created_at: datetime

    exchange_rate_log: ExchangeRateLogResponse | None

    model_config = {"from_attributes": True}