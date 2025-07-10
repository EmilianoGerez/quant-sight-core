from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean
)
from sqlalchemy.orm import relationship
from app.db.base import Base

class Watchlist(Base):
    __tablename__ = "watchlist"

    id            = Column(Integer, primary_key=True, index=True)
    symbol        = Column(String, unique=True, index=True, nullable=False)
    name          = Column(String, nullable=True)
    exchange      = Column(String, nullable=True)
    provider      = Column(String, default="yahoo", nullable=False)

    # ── new fields ────────────────────────────────────────────
    category      = Column(String,      nullable=False, index=True)
    sector        = Column(String,      nullable=True,  index=True)
    industry      = Column(String,      nullable=True,  index=True)
    asset_class   = Column(String,      nullable=True,  index=True)
    region        = Column(String,      nullable=True,  index=True)

    track_iv      = Column(Boolean,     default=False,   nullable=False)
    is_active     = Column(Boolean,     default=True,    nullable=False)
    added_by      = Column(String,      nullable=True)

    added_at      = Column(DateTime,    default=datetime.utcnow, nullable=False)

    iv_history    = relationship("IvHistory", back_populates="watchlist")
