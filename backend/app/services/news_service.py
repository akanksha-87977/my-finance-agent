import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from ..config import settings



class NewsService:
    
    @staticmethod
    def get_financial_news(symbol: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get financial news"""
        try:
            if settings.NEWS_API_KEY:
                # Using News API
                base_url = "https://newsapi.org/v2/everything"
                
                query = f"{symbol} stock" if symbol else "stock market finance"
                params = {
                    "q": query,
                    "apiKey": settings.NEWS_API_KEY,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": limit
                }
                
                response = requests.get(base_url, params=params)
                data = response.json()
                
                news = []
                for article in data.get("articles", [])[:limit]:
                    news.append({
                        "title": article.get("title"),
                        "description": article.get("description"),
                        "url": article.get("url"),
                        "source": article.get("source", {}).get("name"),
                        "publishedAt": article.get("publishedAt"),
                        "image": article.get("urlToImage")
                    })
                
                return news
            else:
                # Return mock news if no API key
                return NewsService._get_mock_news(symbol)
                
        except Exception as e:
            print(f"Error fetching news: {e}")
            return NewsService._get_mock_news(symbol)
    
    @staticmethod
    def _get_mock_news(symbol: Optional[str] = None) -> List[Dict]:
        """Get mock news data"""
        base_news = [
            {
                "title": f"{'Stock Market' if not symbol else symbol} Shows Strong Performance in Q4",
                "description": "Market analysis shows positive trends continuing...",
                "url": "#",
                "source": "Financial Times",
                "publishedAt": datetime.utcnow().isoformat(),
                "sentiment": "positive"
            },
            {
                "title": f"Analysts Upgrade {'Tech Sector' if not symbol else symbol} Outlook",
                "description": "Leading analysts provide positive outlook...",
                "url": "#",
                "source": "Bloomberg",
                "publishedAt": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "sentiment": "positive"
            },
            {
                "title": "Market Volatility Expected Due to Economic Data",
                "description": "Upcoming economic reports may impact markets...",
                "url": "#",
                "source": "Reuters",
                "publishedAt": (datetime.utcnow() - timedelta(hours=5)).isoformat(),
                "sentiment": "neutral"
            }
        ]
        return base_news
    
    @staticmethod
    def analyze_sentiment(text: str) -> Dict:
        """Analyze sentiment of text using AI"""
        # This would integrate with OpenAI or other sentiment analysis
        # Simplified version here
        positive_words = ["growth", "profit", "surge", "upgrade", "bullish", "positive"]
        negative_words = ["loss", "decline", "downgrade", "bearish", "negative", "fall"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return {"sentiment": "positive", "score": 0.7}
        elif negative_count > positive_count:
            return {"sentiment": "negative", "score": 0.3}
        else:
            return {"sentiment": "neutral", "score": 0.5}