from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ChatMessage(BaseModel):
    message: str
    context: Optional[str] = None


class ChatResponse(BaseModel):
    id: int
    message: str
    response: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AgentAnalysisRequest(BaseModel):
    query: str
    portfolio_id: Optional[int] = None
    symbols: Optional[list] = None