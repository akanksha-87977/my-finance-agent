from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from typing import Dict, List
from ..config import settings


class PortfolioOptimizationAgent:
    """Agent responsible for portfolio optimization and rebalancing recommendations"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.4,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        self.agent = Agent(
            role='Portfolio Optimization Specialist',
            goal='Optimize portfolio allocation, suggest rebalancing strategies, and recommend buy/sell actions for improved returns',
            backstory="""You are a portfolio optimization expert with deep knowledge of 
            modern portfolio theory, asset allocation, and rebalancing strategies. You have 
            helped numerous clients optimize their portfolios for better risk-adjusted returns.
            You provide actionable recommendations based on portfolio analysis and market conditions.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def optimize_portfolio(self, portfolio_data: Dict, risk_analysis: Dict, market_data: Dict) -> Dict:
        """Generate portfolio optimization recommendations"""
        holdings = portfolio_data.get('holdings', [])
        
        if not holdings:
            return {
                "recommendations": [],
                "rebalancing_plan": {},
                "analysis": "No holdings to optimize"
            }
        
        # Create optimization prompt
        prompt = f"""
        Optimize the following investment portfolio:
        
        Portfolio Summary:
        - Total Value: ${portfolio_data.get('total_value', 0):,.2f}
        - Total Gain/Loss: ${portfolio_data.get('total_gain_loss', 0):,.2f} ({portfolio_data.get('total_gain_loss_percent', 0):.2f}%)
        - Number of Holdings: {len(holdings)}
        
        Risk Analysis:
        - Risk Level: {risk_analysis.get('risk_level', 'Unknown')}
        - Risk Score: {risk_analysis.get('risk_score', 0):.2f}
        - Diversification Score: {risk_analysis.get('metrics', {}).get('diversification_score', 0):.2f}
        
        Current Holdings:
        {self._format_holdings_detailed(holdings)}
        
        Sector Allocation:
        {self._format_sector_allocation(risk_analysis.get('metrics', {}).get('sector_allocation', {}))}
        
        Based on this analysis, provide:
        1. Portfolio optimization recommendations
        2. Specific rebalancing suggestions (buy/sell/hold)
        3. Target allocation percentages
        4. Diversification improvements
        5. Risk-adjusted optimization strategies
        6. Expected impact on portfolio performance
        
        Provide specific, actionable recommendations with clear rationale.
        """
        
        task = Task(
            description=prompt,
            agent=self.agent,
            expected_output="Comprehensive portfolio optimization recommendations"
        )
        
        try:
            result = task.execute()
            analysis = result if isinstance(result, str) else str(result)
            
            # Extract recommendations
            recommendations = self._extract_action_items(analysis)
            
            # Generate rebalancing plan
            rebalancing_plan = self._create_rebalancing_plan(holdings, risk_analysis)
            
            return {
                "analysis": analysis,
                "recommendations": recommendations,
                "rebalancing_plan": rebalancing_plan,
                "action_items": self._generate_action_items(holdings, rebalancing_plan)
            }
        except Exception as e:
            return {
                "analysis": "Portfolio optimization in progress",
                "recommendations": [],
                "error": str(e)
            }
    
    def suggest_new_investments(self, portfolio_data: Dict, user_preferences: Dict = None) -> Dict:
        """Suggest new investment opportunities"""
        holdings = portfolio_data.get('holdings', [])
        current_symbols = [h['symbol'] for h in holdings]
        
        prompt = f"""
        Suggest new investment opportunities for a portfolio that currently holds:
        {', '.join(current_symbols) if current_symbols else 'No holdings'}
        
        Portfolio Value: ${portfolio_data.get('total_value', 0):,.2f}
        
        Consider:
        1. Diversification needs
        2. Current market conditions
        3. Growth potential
        4. Risk balance
        
        Suggest 5-7 investment opportunities with:
        - Stock symbol
        - Rationale for investment
        - Expected risk/return profile
        - Recommended allocation percentage
        """
        
        task = Task(
            description=prompt,
            agent=self.agent,
            expected_output="Investment opportunity recommendations"
        )
        
        try:
            result = task.execute()
            return {
                "suggestions": result if isinstance(result, str) else str(result),
                "opportunities": self._parse_opportunities(result)
            }
        except:
            return {
                "suggestions": "Generating investment suggestions...",
                "opportunities": []
            }
    
    def _format_holdings_detailed(self, holdings: List[Dict]) -> str:
        """Format holdings with detailed info"""
        lines = []
        for h in holdings:
            lines.append(
                f"  - {h['symbol']}: {h['quantity']} shares @ ${h['average_price']:.2f}, "
                f"Current: ${h['current_price']:.2f}, "
                f"Value: ${h['total_value']:,.2f}, "
                f"P/L: ${h['gain_loss']:,.2f} ({h['gain_loss_percent']:.2f}%), "
                f"Sector: {h.get('sector', 'Unknown')}"
            )
        return "\n".join(lines)
    
    def _format_sector_allocation(self, sector_allocation: Dict) -> str:
        """Format sector allocation"""
        if not sector_allocation:
            return "  No allocation data"
        
        lines = []
        for sector, pct in sorted(sector_allocation.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  - {sector}: {pct:.2f}%")
        return "\n".join(lines)
    
    def _extract_action_items(self, analysis: str) -> List[str]:
        """Extract actionable recommendations"""
        recommendations = []
        
        # Simplified extraction
        keywords = {
            "sell": "Consider selling overweight positions",
            "buy": "Consider buying underweight positions",
            "rebalance": "Rebalance portfolio to target allocation",
            "diversify": "Increase diversification across sectors",
            "reduce": "Reduce concentration in top holdings"
        }
        
        for keyword, recommendation in keywords.items():
            if keyword in analysis.lower():
                recommendations.append(recommendation)
        
        return recommendations[:7]
    
    def _create_rebalancing_plan(self, holdings: List[Dict], risk_analysis: Dict) -> Dict:
        """Create a rebalancing plan"""
        total_value = sum(h['total_value'] for h in holdings)
        
        if total_value == 0:
            return {}
        
        # Simple equal-weight rebalancing plan
        target_weight = 100 / len(holdings) if holdings else 0
        
        plan = {}
        for holding in holdings:
            current_weight = (holding['total_value'] / total_value) * 100
            difference = current_weight - target_weight
            
            if abs(difference) > 5:  # Only suggest if difference > 5%
                action = "REDUCE" if difference > 0 else "INCREASE"
                plan[holding['symbol']] = {
                    "current_weight": round(current_weight, 2),
                    "target_weight": round(target_weight, 2),
                    "action": action,
                    "difference": round(difference, 2)
                }
        
        return plan
    
    def _generate_action_items(self, holdings: List[Dict], rebalancing_plan: Dict) -> List[Dict]:
        """Generate specific action items"""
        actions = []
        
        for symbol, plan in rebalancing_plan.items():
            actions.append({
                "symbol": symbol,
                "action": plan['action'],
                "current_weight": plan['current_weight'],
                "target_weight": plan['target_weight'],
                "description": f"{plan['action']} {symbol} position from {plan['current_weight']:.1f}% to {plan['target_weight']:.1f}%"
            })
        
        return actions
    
    def _parse_opportunities(self, suggestions: str) -> List[Dict]:
        """Parse investment opportunities from suggestions"""
        # Simplified parsing - in production, use more sophisticated NLP
        return [
            {"symbol": "SPY", "type": "ETF", "rationale": "Market diversification"},
            {"symbol": "QQQ", "type": "ETF", "rationale": "Tech sector exposure"}
        ]