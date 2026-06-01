from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from ..services import StockService, NewsService
from ..utils.dependencies import get_current_active_user

router = APIRouter(prefix="/api/stocks", tags=["Stocks"])


@router.get("/quote/{symbol}")
def get_stock_quote(
    symbol: str,
    current_user = Depends(get_current_active_user)
):
    """Get stock quote"""
    return StockService.get_stock_quote(symbol)


@router.get("/history/{symbol}")
def get_stock_history(
    symbol: str,
    period: str = Query("1mo", regex="^(1d|5d|1mo|3mo|6mo|1y|5y)$"),
    current_user = Depends(get_current_active_user)
):
    """Get historical stock data"""
    return StockService.get_historical_data(symbol, period)


@router.get("/search")
def search_stocks(
    query: str = Query(..., min_length=1),
    current_user = Depends(get_current_active_user)
):
    """Search for stocks"""
    return StockService.search_stocks(query)


@router.get("/trending")
def get_trending_stocks(
    current_user = Depends(get_current_active_user)
):
    """Get trending stocks"""
    return StockService.get_trending_stocks()


@router.get("/movers")
def get_market_movers(
    current_user = Depends(get_current_active_user)
):
    """Get market gainers and losers"""
    return StockService.get_market_movers()


@router.get("/news/{symbol}")
def get_stock_news(
    symbol: str,
    limit: int = Query(10, ge=1, le=50),
    current_user = Depends(get_current_active_user)
):
    """Get news for a specific stock"""
    return NewsService.get_financial_news(symbol=symbol, limit=limit)


@router.get("/news")
def get_general_news(
    limit: int = Query(10, ge=1, le=50),
    current_user = Depends(get_current_active_user)
):
    """Get general financial news"""
    return NewsService.get_financial_news(limit=limit)