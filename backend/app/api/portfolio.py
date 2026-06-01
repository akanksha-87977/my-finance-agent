from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import User, Portfolio, Holding, Watchlist
from ..schemas import (
    PortfolioCreate, PortfolioResponse,
    HoldingCreate, HoldingResponse,
    WatchlistCreate, WatchlistResponse
)
from ..services import PortfolioService
from ..utils.dependencies import get_current_active_user

router = APIRouter(prefix="/api/portfolio", tags=["Portfolio"])


@router.post("/", response_model=PortfolioResponse)
def create_portfolio(
    portfolio: PortfolioCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new portfolio"""
    return PortfolioService.create_portfolio(db, current_user, portfolio)


@router.get("/", response_model=PortfolioResponse)
def get_portfolio(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's portfolio"""
    return PortfolioService.get_user_portfolio(db, current_user)


@router.post("/holdings", response_model=HoldingResponse)
def add_holding(
    holding: HoldingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a holding to portfolio"""
    portfolio = PortfolioService.get_user_portfolio(db, current_user)
    return PortfolioService.add_holding(db, portfolio, holding)


@router.delete("/holdings/{holding_id}")
def delete_holding(
    holding_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a holding"""
    holding = db.query(Holding).filter(Holding.id == holding_id).first()
    
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    
    # Verify ownership
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == holding.portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()
    
    if not portfolio:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(holding)
    db.commit()
    
    return {"message": "Holding deleted successfully"}


@router.get("/metrics")
def get_portfolio_metrics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get portfolio metrics and analytics"""
    portfolio = PortfolioService.get_user_portfolio(db, current_user)
    metrics = PortfolioService.calculate_portfolio_metrics(portfolio)
    return metrics


@router.post("/watchlist", response_model=WatchlistResponse)
def add_to_watchlist(
    watchlist_item: WatchlistCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add stock to watchlist"""
    # Check if already in watchlist
    existing = db.query(Watchlist).filter(
        Watchlist.user_id == current_user.id,
        Watchlist.symbol == watchlist_item.symbol
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already in watchlist")
    
    watchlist = Watchlist(
        user_id=current_user.id,
        symbol=watchlist_item.symbol,
        name=watchlist_item.name
    )
    
    db.add(watchlist)
    db.commit()
    db.refresh(watchlist)
    
    return watchlist


@router.get("/watchlist", response_model=List[WatchlistResponse])
def get_watchlist(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's watchlist"""
    watchlist = db.query(Watchlist).filter(
        Watchlist.user_id == current_user.id
    ).all()
    
    return watchlist


@router.delete("/watchlist/{watchlist_id}")
def remove_from_watchlist(
    watchlist_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove from watchlist"""
    watchlist = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == current_user.id
    ).first()
    
    if not watchlist:
        raise HTTPException(status_code=404, detail="Not found")
    
    db.delete(watchlist)
    db.commit()
    
    return {"message": "Removed from watchlist"}