from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass


from app.models.role import Role
from app.models.user import User
from app.models.transaction import Transaction
from app.models.exchange_rate_log import ExchangeRateLog

