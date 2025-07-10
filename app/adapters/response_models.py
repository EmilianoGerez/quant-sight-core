from pydantic import BaseModel
from datetime import datetime

class RegimePoint(BaseModel):
    date: datetime
    close: float
    regime: int
    
class TrendPoint(BaseModel):
    date: datetime
    close: float
    trend_bias: str
