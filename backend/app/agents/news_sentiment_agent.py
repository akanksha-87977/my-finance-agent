from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from typing import Dict, List
from ..services.news_service import NewsService
from ..config import settings


class NewsSentimentAgent:
    """Agent responsible for news analysis and sentiment detection"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.5,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        self.agent = Agent(
            role='News Sentiment Analyst',
            goal='Analyze financial news and detect market sentiment to identify potential market-moving events',
            backstory="""You are an expert in financial news analysis and sentiment detection.
            You have a deep understanding of how news impacts market movements and can quickly
            identify bullish or bearish signals from news articles. You specialize in NLP-based
            sentiment analysis and market psychology.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def analyze_news_sentiment(self, symbol: str = None) -> Dict:
        """Analyze news sentiment for a stock or general market"""
        # Fetch news
        news_articles = NewsService.get_financial_news(symbol=symbol, limit=10)
        
        if not news_articles:
            return {
                "symbol": symbol,
                "sentiment": "neutral",
                "score": 0.5,
                "summary": "No recent news available",
                "articles": []
            }
        
        # Create analysis prompt
        news_text = "\n\n".join([
            f"Title: {article['title']}\nDescription: {article['description']}"
            for article in news_articles[:5]
        ])
        
        prompt = f"""
        Analyze the sentiment of the following financial news articles for {symbol or 'the market'}:
        
        {news_text}
        
        Provide:
        1. Overall sentiment (Bullish/Bearish/Neutral)
        2. Sentiment score (0-1, where 0 is very bearish, 0.5 is neutral, 1 is very bullish)
        3. Key themes identified
        4. Potential market impact
        5. Notable events or announcements
        
        Be specific and data-driven in your analysis.
        """
        
        task = Task(
            description=prompt,
            agent=self.agent,
            expected_output="Comprehensive news sentiment analysis"
        )
        
        try:
            result = task.execute()
            sentiment_analysis = result if isinstance(result, str) else str(result)
            
            # Extract sentiment and score (simplified)
            sentiment, score = self._extract_sentiment(sentiment_analysis)
            
            return {
                "symbol": symbol or "MARKET",
                "sentiment": sentiment,
                "score": score,
                "analysis": sentiment_analysis,
                "articles": news_articles[:5],
                "key_themes": self._extract_themes(sentiment_analysis)
            }
        except Exception as e:
            return {
                "symbol": symbol,
                "sentiment": "neutral",
                "score": 0.5,
                "analysis": "Sentiment analysis in progress",
                "error": str(e)
            }
    
    def detect_market_moving_news(self) -> Dict:
        """Detect significant market-moving news"""
        general_news = NewsService.get_financial_news(limit=15)
        
        prompt = f"""
        From the following news articles, identify the most market-moving news:
        
        {chr(10).join([f"- {article['title']}" for article in general_news[:10]])}
        
        Identify:
        1. Most significant news items
        2. Potential market impact
        3. Affected sectors
        4. Recommended actions for investors
        """
        
        task = Task(
            description=prompt,
            agent=self.agent,
            expected_output="Market-moving news analysis"
        )
        
        try:
            result = task.execute()
            return {
                "analysis": result if isinstance(result, str) else str(result),
                "top_news": general_news[:5]
            }
        except:
            return {
                "analysis": "Analysis in progress",
                "top_news": general_news[:5]
            }
    
    def _extract_sentiment(self, analysis: str) -> tuple:
        """Extract sentiment and score from analysis"""
        analysis_lower = analysis.lower()
        
        if "bullish" in analysis_lower or "positive" in analysis_lower:
            return "bullish", 0.7
        elif "bearish" in analysis_lower or "negative" in analysis_lower:
            return "bearish", 0.3
        else:
            return "neutral", 0.5
    
    def _extract_themes(self, analysis: str) -> List[str]:
        """Extract key themes from analysis"""
        # Simplified theme extraction
        themes = []
        keywords = ["growth", "earnings", "revenue", "profit", "expansion", 
                   "decline", "loss", "risk", "opportunity", "innovation"]
        
        for keyword in keywords:
            if keyword in analysis.lower():
                themes.append(keyword.capitalize())
        
        return themes[:5]