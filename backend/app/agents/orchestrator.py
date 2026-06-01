from typing import Dict, List
from .market_research_agent import MarketResearchAgent
from .news_sentiment_agent import NewsSentimentAgent
from .risk_analysis_agent import RiskAnalysisAgent
from .portfolio_optimization_agent import PortfolioOptimizationAgent
from .report_generation_agent import ReportGenerationAgent


class AgentOrchestrator:
    """Orchestrates multiple AI agents to work together"""
    
    def __init__(self):
        self.market_agent = MarketResearchAgent()
        self.sentiment_agent = NewsSentimentAgent()
        self.risk_agent = RiskAnalysisAgent()
        self.optimization_agent = PortfolioOptimizationAgent()
        self.report_agent = ReportGenerationAgent()
    
    async def analyze_portfolio_comprehensive(self, portfolio_data: Dict) -> Dict:
        """Comprehensive portfolio analysis using all agents"""
        
        # Extract symbols from portfolio
        holdings = portfolio_data.get('holdings', [])
        symbols = [h['symbol'] for h in holdings]
        
        # Step 1: Market Research
        print("🔍 Running Market Research Analysis...")
        if symbols:
            market_analysis = self.market_agent.analyze_multiple_stocks(symbols)
        else:
            market_analysis = {"analysis": "No holdings to analyze"}
        
        # Step 2: Sentiment Analysis
        print("📰 Running News Sentiment Analysis...")
        sentiment_analysis = self.sentiment_agent.analyze_news_sentiment()
        
        # Step 3: Risk Analysis
        print("⚠️ Running Risk Analysis...")
        risk_analysis = self.risk_agent.analyze_portfolio_risk(portfolio_data)
        
        # Step 4: Portfolio Optimization
        print("📊 Running Portfolio Optimization...")
        optimization = self.optimization_agent.optimize_portfolio(
            portfolio_data,
            risk_analysis,
            market_analysis
        )
        
        # Step 5: Generate Report
        print("📄 Generating Comprehensive Report...")
        report = self.report_agent.generate_portfolio_report(
            portfolio_data,
            market_analysis,
            sentiment_analysis,
            risk_analysis,
            optimization
        )
        
        return {
            "market_analysis": market_analysis,
            "sentiment_analysis": sentiment_analysis,
            "risk_analysis": risk_analysis,
            "optimization": optimization,
            "report": report,
            "status": "completed"
        }
    
    async def analyze_stock(self, symbol: str) -> Dict:
        """Comprehensive stock analysis"""
        
        print(f"🔍 Analyzing {symbol}...")
        
        # Market research
        market_analysis = self.market_agent.analyze_stock(symbol)
        
        # Sentiment analysis
        sentiment_analysis = self.sentiment_agent.analyze_news_sentiment(symbol)
        
        # Generate report
        report = self.report_agent.generate_stock_research_report(
            symbol,
            {**market_analysis, **sentiment_analysis}
        )
        
        return {
            "symbol": symbol,
            "market_analysis": market_analysis,
            "sentiment_analysis": sentiment_analysis,
            "report": report,
            "status": "completed"
        }
    
    async def answer_financial_question(self, question: str, context: Dict = None) -> str:
        """Answer financial questions using appropriate agents"""
        
        question_lower = question.lower()
        
        # Determine which agents to use
        if "risk" in question_lower or "volatile" in question_lower:
            # Use risk agent
            if context and context.get('portfolio_data'):
                analysis = self.risk_agent.analyze_portfolio_risk(context['portfolio_data'])
                return analysis.get('analysis', 'Analysis in progress')
        
        elif "news" in question_lower or "sentiment" in question_lower:
            # Use sentiment agent
            symbol = context.get('symbol') if context else None
            analysis = self.sentiment_agent.analyze_news_sentiment(symbol)
            return analysis.get('analysis', 'Analysis in progress')
        
        elif "optimize" in question_lower or "rebalance" in question_lower:
            # Use optimization agent
            if context and context.get('portfolio_data'):
                portfolio_data = context['portfolio_data']
                risk_data = context.get('risk_data', {})
                market_data = context.get('market_data', {})
                
                analysis = self.optimization_agent.optimize_portfolio(
                    portfolio_data,
                    risk_data,
                    market_data
                )
                return analysis.get('analysis', 'Analysis in progress')
        
        else:
            # Default to market research
            return "I can help you analyze stocks, assess portfolio risk, check market sentiment, or optimize your portfolio. What would you like to know more about?"