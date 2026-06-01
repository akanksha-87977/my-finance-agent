from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import User, ChatHistory
from ..schemas import ChatMessage, ChatResponse
from ..services import PortfolioService

from ..utils.dependencies import get_current_active_user
from ..agents import AgentOrchestrator



router = APIRouter(prefix="/api/chat", tags=["Chat"])



@router.post("/", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send a message to AI financial assistant"""
    
    # Get portfolio context
    portfolio = PortfolioService.get_user_portfolio(db, current_user)
    portfolio_data = {
        "total_value": portfolio.total_value,
        "total_cost": portfolio.total_cost,
        "total_gain_loss": portfolio.total_gain_loss,
        "total_gain_loss_percent": portfolio.total_gain_loss_percent,
        "holdings": [
            {
                "symbol": h.symbol,
                "quantity": h.quantity,
                "average_price": h.average_price,
                "current_price": h.current_price,
                "total_value": h.total_value,
                "gain_loss": h.gain_loss,
                "gain_loss_percent": h.gain_loss_percent,
                "sector": h.sector
            }
            for h in portfolio.holdings
        ]
    }
    
    context = {
        "portfolio_data": portfolio_data,
        "user_id": current_user.id
    }
    
    # Get AI response
    try:
        orchestrator = AgentOrchestrator()
        response_text = await orchestrator.answer_financial_question(
            message.message,
            context
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {exc}")

    
    # Save to chat history
    chat_record = ChatHistory(
        user_id=current_user.id,
        message=message.message,
        response=response_text,
        context=message.context
    )
    
    db.add(chat_record)
    db.commit()
    db.refresh(chat_record)
    
    return chat_record


@router.get("/history", response_model=List[ChatResponse])
def get_chat_history(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get chat history"""
    history = db.query(ChatHistory).filter(
        ChatHistory.user_id == current_user.id
    ).order_by(ChatHistory.created_at.desc()).limit(limit).all()
    
    return history[::-1]  # Reverse to chronological order


@router.delete("/history")
def clear_chat_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Clear chat history"""
    db.query(ChatHistory).filter(
        ChatHistory.user_id == current_user.id
    ).delete()
    
    db.commit()
    
    return {"message": "Chat history cleared"}