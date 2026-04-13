from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    amount_usd = Column(Float, nullable=False)
    amount_gtq = Column(Float, nullable=False)
    exchange_rate = Column(Float, nullable=False)  # tasa fija al momento
    status = Column(String, default="pendiente")   # pendiente | confirmado
    note = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="transactions")

    exchange_rate_log = relationship("ExchangeRateLog", back_populates="transaction", uselist=False)