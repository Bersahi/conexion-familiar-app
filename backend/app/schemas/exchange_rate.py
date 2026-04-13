from pydantic import BaseModel
from datetime import datetime

class ExchangeRateLogCreate(BaseModel):
    rate: float
    from_currency: str
    to_currency: str
    transaction_id: int

class ExchangeRateLogResponse(BaseModel):
    id: int
    rate: float
    from_currency: str
    to_currency: str
    fetched_at: datetime
    transaction_id: int

    model_config = {"from_attributes": True}