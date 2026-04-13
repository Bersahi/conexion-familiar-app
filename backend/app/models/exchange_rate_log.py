from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

class ExchangeRateLog(Base):
    __tablename__ = "exchange_rate_logs"

    id = Column(Integer, primary_key=True)
    rate = Column(Float, nullable=False)
    from_currency = Column(String, nullable=False)  # USD
    to_currency = Column(String, nullable=False)    # GTQ
    fetched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)

    transaction = relationship("Transaction", back_populates="exchange_rate_log")