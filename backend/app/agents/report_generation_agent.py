from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from typing import Dict
from datetime import datetime
from ..config import settings


class ReportGenerationAgent:
    """Agent responsible for generating comprehensive financial reports"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.6,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        self.agent = Agent(
            role='Financial Report Writer',
            goal='Create comprehensive, professional financial reports and investment summaries',
            backstory="""You are an expert financial report writer with experience in 
            creating institutional-grade investment reports. You synthesize complex financial
            data and AI analyses into clear, actionable reports for investors. Your reports
            are known for being thorough, well-structured, and professional.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def generate_portfolio_report(
        self,
        portfolio_data: Dict,
        market_analysis: Dict,
        sentiment_analysis: Dict,
        risk_analysis: Dict,
        optimization: Dict
    ) -> Dict:
        """Generate comprehensive portfolio report"""
        
        prompt = f"""
        Create a comprehensive Portfolio Analysis Report based on the following information:
        
        PORTFOLIO OVERVIEW:
        - Total Value: ${portfolio_data.get('total_value', 0):,.2f}
        - Total Investment: ${portfolio_data.get('total_cost', 0):,.2f}
        - Total Return: ${portfolio_data.get('total_gain_loss', 0):,.2f} ({portfolio_data.get('total_gain_loss_percent', 0):.2f}%)
        - Number of Holdings: {len(portfolio_data.get('holdings', []))}
        
        MARKET RESEARCH INSIGHTS:
        {market_analysis.get('analysis', 'No market analysis available')}
        
        SENTIMENT ANALYSIS:
        - Overall Sentiment: {sentiment_analysis.get('sentiment', 'Neutral')}
        - Sentiment Score: {sentiment_analysis.get('score', 0.5)}
        {sentiment_analysis.get('analysis', '')}
        
        RISK ASSESSMENT:
        - Risk Level: {risk_analysis.get('risk_level', 'Unknown')}
        - Risk Score: {risk_analysis.get('risk_score', 0):.2f}/100
        {risk_analysis.get('analysis', '')}
        
        OPTIMIZATION RECOMMENDATIONS:
        {optimization.get('analysis', '')}
        
        Create a professional report with the following sections:
        1. Executive Summary
        2. Portfolio Performance Analysis
        3. Market Conditions & Sentiment
        4. Risk Assessment
        5. Investment Recommendations
        6. Action Items
        7. Conclusion
        
        Write in a professional, institutional tone suitable for presentation to investors or management.
        Be specific, data-driven, and actionable.
        """
        
        task = Task(
            description=prompt,
            agent=self.agent,
            expected_output="Professional portfolio analysis report"
        )
        
        try:
            result = task.execute()
            report_content = result if isinstance(result, str) else str(result)
            
            # Create structured report
            report = {
                "title": f"Portfolio Analysis Report - {datetime.now().strftime('%B %d, %Y')}",
                "generated_at": datetime.now().isoformat(),
                "summary": self._extract_summary(report_content),
                "content": report_content,
                "sections": self._parse_sections(report_content),
                "key_metrics": {
                    "portfolio_value": portfolio_data.get('total_value', 0),
                    "total_return": portfolio_data.get('total_gain_loss', 0),
                    "return_percentage": portfolio_data.get('total_gain_loss_percent', 0),
                    "risk_level": risk_analysis.get('risk_level', 'Unknown'),
                    "risk_score": risk_analysis.get('risk_score', 0),
                    "sentiment": sentiment_analysis.get('sentiment', 'Neutral')
                },
                "recommendations": optimization.get('recommendations', [])
            }
            
            return report
            
        except Exception as e:
            return {
                "title": "Portfolio Analysis Report",
                "generated_at": datetime.now().isoformat(),
                "summary": "Report generation in progress",
                "content": "Generating comprehensive analysis...",
                "error": str(e)
            }
    
    def generate_stock_research_report(self, symbol: str, analysis_data: Dict) -> Dict:
        """Generate stock research report"""
        
        prompt = f"""
        Create a detailed Stock Research Report for {symbol}:
        
        {analysis_data.get('analysis', '')}
        
        Include:
        1. Company Overview
        2. Current Valuation & Price Analysis
        3. Technical Analysis
        4. Market Sentiment
        5. Investment Thesis
        6. Risk Factors
        7. Price Target & Recommendation
        
        Make it comprehensive and professional.
        """
        
        task = Task(
            description=prompt,
            agent=self.agent,
            expected_output="Stock research report"
        )
        
        try:
            result = task.execute()
            return {
                "symbol": symbol,
                "title": f"{symbol} Research Report",
                "generated_at": datetime.now().isoformat(),
                "content": result if isinstance(result, str) else str(result),
                "recommendation": analysis_data.get('recommendation', 'HOLD')
            }
        except:
            return {
                "symbol": symbol,
                "title": f"{symbol} Research Report",
                "content": "Report generation in progress"
            }
    
    def _extract_summary(self, content: str) -> str:
        """Extract executive summary from report"""
        # Look for executive summary section
        if "executive summary" in content.lower():
            parts = content.lower().split("executive summary")
            if len(parts) > 1:
                summary_part = parts[1].split("\n\n")[0:3]
                return "\n".join(summary_part)
        
        # Otherwise return first paragraph
        paragraphs = content.split("\n\n")
        return paragraphs[0] if paragraphs else content[:500]
    
    def _parse_sections(self, content: str) -> Dict:
        """Parse report into sections"""
        # Simplified section parsing
        sections = {}
        
        section_headers = [
            "Executive Summary",
            "Portfolio Performance",
            "Market Conditions",
            "Risk Assessment",
            "Recommendations",
            "Conclusion"
        ]
        
        for header in section_headers:
            if header.lower() in content.lower():
                sections[header] = f"See full report for {header}"
        
        return sections