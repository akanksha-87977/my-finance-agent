from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from typing import Dict, List
import json
from ..services.stock_service import StockService
from ..config import settings


class MarketResearchAgent:
    """Agent responsible for market research and stock analysis"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        self.agent = Agent(
            role='Market Research Analyst',
            goal='Analyze stock market data, trends, and technical indicators to provide comprehensive market insights',
            backstory="""You are an expert market research analyst with 15+ years of experience 
            in equity research. You specialize in technical analysis, trend identification, 
            and comprehensive stock evaluation. You provide data-driven insights based on 
            market data, trading volumes, and price movements.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def analyze_stock(self, symbol: str) -> Dict:
        """Analyze a specific stock"""
        # Fetch stock data
        stock_data = StockService.get_stock_quote(symbol)
        historical_data = StockService.get_historical_data(symbol, period="3mo")
        
        # Create analysis prompt
        prompt = f"""
        Analyze the following stock data for {symbol}:
        
        Current Data:
        - Price: ${stock_data.get('price', 0):.2f}
        - Change: {stock_data.get('changePercent', 0):.2f}%
        - Volume: {stock_data.get('volume', 0):,}
        - Market Cap: ${stock_data.get('marketCap', 0):,}
        - 52-Week High: ${stock_data.get('fiftyTwoWeekHigh', 0):.2f}
        - 52-Week Low: ${stock_data.get('fiftyTwoWeekLow', 0):.2f}
        - Sector: {stock_data.get('sector', 'Unknown')}
        
        Historical Performance (3 months):
        Number of data points: {len(historical_data)}
        
        Provide a comprehensive analysis including:
        1. Current market position
        2. Trend analysis (bullish/bearish/neutral)
        3. Technical indicators assessment
        4. Price momentum
        5. Trading volume analysis
        6. Key observations
        
        Format your response as a structured analysis.
        """
        
        task = Task(
            description=prompt,
            agent=self.agent,
            expected_output="Detailed stock analysis with market insights"
        )
        
        # Execute analysis
        try:
            result = task.execute()
            
            return {
                "symbol": symbol,
                "analysis": result if isinstance(result, str) else str(result),
                "stock_data": stock_data,
                "trend": self._determine_trend(historical_data),
                "recommendation": self._generate_recommendation(stock_data, historical_data)
            }
        except Exception as e:
            return {
                "symbol": symbol,
                "analysis": f"Analysis in progress for {symbol}",
                "stock_data": stock_data,
                "error": str(e)
            }
    
    def analyze_multiple_stocks(self, symbols: List[str]) -> Dict:
        """Analyze multiple stocks and compare"""
        analyses = []
        
        for symbol in symbols:
            analysis = self.analyze_stock(symbol)
            analyses.append(analysis)
        
        # Generate comparative analysis
        comparison_prompt = f"""
        Compare the following stocks and provide insights:
        {', '.join(symbols)}
        
        Based on the individual analyses, provide:
        1. Comparative performance
        2. Relative strengths and weaknesses
        3. Best opportunities
        4. Risk comparison
        """
        
        task = Task(
            description=comparison_prompt,
            agent=self.agent,
            expected_output="Comparative analysis of multiple stocks"
        )
        
        try:
            comparison = task.execute()
        except:
            comparison = "Comparative analysis in progress"
        
        return {
            "individual_analyses": analyses,
            "comparison": comparison if isinstance(comparison, str) else str(comparison)
        }
    
    def _determine_trend(self, historical_data: List[Dict]) -> str:
        """Determine price trend from historical data"""
        if not historical_data or len(historical_data) < 2:
            return "neutral"
        
        first_price = historical_data[0]['close']
        last_price = historical_data[-1]['close']
        change_percent = ((last_price - first_price) / first_price) * 100
        
        if change_percent > 5:
            return "bullish"
        elif change_percent < -5:
            return "bearish"
        else:
            return "neutral"
    
    def _generate_recommendation(self, stock_data: Dict, historical_data: List[Dict]) -> str:
        """Generate simple recommendation"""
        trend = self._determine_trend(historical_data)
        
        if trend == "bullish":
            return "BUY"
        elif trend == "bearish":
            return "SELL"
        else:
            return "HOLD"