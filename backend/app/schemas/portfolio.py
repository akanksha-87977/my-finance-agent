from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class HoldingBase(BaseModel):
    symbol: str
    quantity: float
    average_price: float


class HoldingCreate(HoldingBase):
    pass


class HoldingResponse(HoldingBase):
    id: int
    current_price: float
    total_value: float
    gain_loss: float
    gain_loss_percent: float
    sector: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PortfolioCreate(BaseModel):
    name: str = "My Portfolio"


class PortfolioResponse(BaseModel):
    id: int
    name: str
    total_value: float
    total_cost: float
    total_gain_loss: float
    total_gain_loss_percent: float
    holdings: List[HoldingResponse] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


class WatchlistCreate(BaseModel):
    symbol: str
    name: Optional[str] = None


class WatchlistResponse(BaseModel):
    id: int
    symbol: str
    name: Optional[str]
    added_at: datetime
    
    class Config:
        from_attributes = True