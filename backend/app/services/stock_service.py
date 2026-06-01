import yfinance as yf
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import threading

from ..config import settings


class StockService:
    """Stock quote utilities.

    Note: Yahoo Finance (yfinance) is rate-limited. To keep analysis endpoints reliable,
    we add a small in-process cache + throttle per symbol.
    """

    _cache_lock = threading.Lock()
    _quote_cache: Dict[str, Tuple[datetime, Dict]] = {}
    _quote_inflight: Dict[str, datetime] = {}

    # Cache TTL for quotes (seconds). Default 10 minutes.
    _CACHE_TTL_SECONDS = int(getattr(settings, "STOCK_QUOTE_CACHE_TTL_SECONDS", 600))
    # Minimum time between upstream quote calls per symbol (seconds). Default 30 seconds.
    _THROTTLE_SECONDS = int(getattr(settings, "STOCK_QUOTE_THROTTLE_SECONDS", 30))

    @staticmethod
    def _get_cached(symbol: str) -> Optional[Dict]:
        now = datetime.utcnow()
        with StockService._cache_lock:
            cached = StockService._quote_cache.get(symbol)
            if not cached:
                return None
            ts, value = cached
            if (now - ts).total_seconds() <= StockService._CACHE_TTL_SECONDS:
                return value
            # stale; return None (call upstream)
            return None

    @staticmethod
    def _set_cached(symbol: str, value: Dict) -> None:
        now = datetime.utcnow()
        with StockService._cache_lock:
            StockService._quote_cache[symbol] = (now, value)

    @staticmethod
    def _throttle_wait_if_needed(symbol: str) -> bool:
        """Return True if we should short-circuit (i.e., too soon), else False."""
        now = datetime.utcnow()
        with StockService._cache_lock:
            last = StockService._quote_inflight.get(symbol)
            if last and (now - last).total_seconds() < StockService._THROTTLE_SECONDS:
                return True
            StockService._quote_inflight[symbol] = now
            return False

    @staticmethod
    def get_stock_quote(symbol: str) -> Dict:
        """Get current stock quote (cached/throttled)."""
        symbol = (symbol or "").upper().strip()
        if not symbol:
            return {"symbol": symbol, "name": symbol, "price": 0}

        # 1) Serve from cache if fresh
        cached = StockService._get_cached(symbol)
        if cached is not None:
            return cached

        # 2) Throttle upstream calls
        if StockService._throttle_wait_if_needed(symbol):
            # If throttled, fall back to stale cache if any exists
            with StockService._cache_lock:
                stale = StockService._quote_cache.get(symbol)
                if stale:
                    return stale[1]
            return {
                "symbol": symbol,
                "name": symbol,
                "price": 0,
                "error": "Throttled; no cached value available"
            }

        try:
            stock = yf.Ticker(symbol)
            info = stock.info

            quote = {
                "symbol": symbol,
                "name": info.get("longName", symbol),
                "price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
                "change": info.get("regularMarketChange", 0),
                "changePercent": info.get("regularMarketChangePercent", 0),
                "volume": info.get("volume", 0),
                "marketCap": info.get("marketCap", 0),
                "dayHigh": info.get("dayHigh", 0),
                "dayLow": info.get("dayLow", 0),
                "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh", 0),
                "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow", 0),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
            }

            # Save fresh value
            StockService._set_cached(symbol, quote)
            return quote
        except Exception as e:
            # 3) If upstream fails (incl. 429), return stale cache if present
            with StockService._cache_lock:
                stale = StockService._quote_cache.get(symbol)
                if stale:
                    stale_val = stale[1].copy()
                    stale_val["error"] = str(e)
                    return stale_val

            print(f"Error fetching stock quote for {symbol}: {e}")
            return {"symbol": symbol, "name": symbol, "price": 0, "error": str(e)}

    
    @staticmethod
    def get_historical_data(symbol: str, period: str = "1mo") -> List[Dict]:
        """Get historical stock data"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)
            
            data = []
            for date, row in hist.iterrows():
                data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"])
                })
            
            return data
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return []
    
    @staticmethod
    def get_trending_stocks() -> List[Dict]:
        """Get trending stocks"""
        try:
            # Using Yahoo Finance trending tickers
            trending_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "AMD"]
            
            stocks = []
            for symbol in trending_symbols[:6]:
                quote = StockService.get_stock_quote(symbol)
                if not quote.get("error"):
                    stocks.append(quote)
            
            return stocks
        except Exception as e:
            print(f"Error fetching trending stocks: {e}")
            return []
    
    @staticmethod
    def search_stocks(query: str) -> List[Dict]:
        """Search for stocks"""
        try:
            # Simple implementation - you can enhance this
            stock = yf.Ticker(query.upper())
            info = stock.info
            
            return [{
                "symbol": query.upper(),
                "name": info.get("longName", query),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown")
            }]
        except:
            return []
    
    @staticmethod
    def get_market_movers() -> Dict:
        """Get market gainers and losers"""
        # Simplified version - you can integrate with real API
        gainers_symbols = ["NVDA", "AMD", "AVGO"]
        losers_symbols = ["INTC", "CSCO", "QCOM"]
        
        gainers = [StockService.get_stock_quote(s) for s in gainers_symbols]
        losers = [StockService.get_stock_quote(s) for s in losers_symbols]
        
        return {
            "gainers": [g for g in gainers if not g.get("error")],
            "losers": [l for l in losers if not l.get("error")]
        }