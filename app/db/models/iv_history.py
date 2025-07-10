
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class IvHistory(Base):
    __tablename__ = "ivhistory"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    contract_id = Column(String, nullable=False)
    expiration = Column(String, nullable=False)
    iv = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)

    watchlist_id = Column(Integer, ForeignKey("watchlist.id"))
    watchlist = relationship("Watchlist", back_populates="iv_history")
