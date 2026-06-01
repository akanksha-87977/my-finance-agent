from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from typing import Dict, List
import numpy as np
from ..config import settings


class RiskAnalysisAgent:
    """Agent responsible for portfolio risk analysis"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        self.agent = Agent(
            role='Risk Management Specialist',
            goal='Evaluate portfolio risk, calculate volatility, detect overexposure, and generate comprehensive risk assessments',
            backstory="""You are a senior risk management specialist with expertise in 
            portfolio theory, volatility analysis, and risk metrics. You have worked at 
            leading investment firms and specialize in quantitative risk assessment. 
            You help investors understand and manage their portfolio risk effectively.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def analyze_portfolio_risk(self, portfolio_data: Dict) -> Dict:
        """Comprehensive portfolio risk analysis"""
        holdings = portfolio_data.get('holdings', [])
        
        if not holdings:
            return {
                "risk_score": 0,
                "risk_level": "N/A",
                "analysis": "No holdings to analyze",
                "recommendations": []
            }
        
        # Calculate risk metrics
        metrics = self._calculate_risk_metrics(holdings, portfolio_data)
        
        # Create analysis prompt
        prompt = f"""
        Analyze the risk profile of this investment portfolio:
        
        Portfolio Summary:
        - Total Value: ${portfolio_data.get('total_value', 0):,.2f}
        - Number of Holdings: {len(holdings)}
        - Diversification Score: {metrics['diversification_score']:.2f}
        - Sector Concentration: {metrics['max_sector_concentration']:.2f}%
        
        Sector Allocation:
        {self._format_sector_allocation(metrics['sector_allocation'])}
        
        Holdings:
        {self._format_holdings(holdings)}
        
        Provide a comprehensive risk analysis including:
        1. Overall risk level (Low/Medium/High)
        2. Concentration risks
        3. Sector-specific risks
        4. Volatility assessment
        5. Diversification quality
        6. Specific risk factors to watch
        7. Risk mitigation recommendations
        
        Be specific and actionable in your recommendations.
        """
        
        task = Task(
            description=prompt,
            agent=self.agent,
            expected_output="Detailed portfolio risk analysis with recommendations"
        )
        
        try:
            result = task.execute()
            analysis = result if isinstance(result, str) else str(result)
            
            # Calculate overall risk score
            risk_score = self._calculate_risk_score(metrics)
            risk_level = self._determine_risk_level(risk_score)
            
            return {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "analysis": analysis,
                "metrics": metrics,
                "recommendations": self._extract_recommendations(analysis)
            }
        except Exception as e:
            return {
                "risk_score": 50,
                "risk_level": "Medium",
                "analysis": "Risk analysis in progress",
                "error": str(e)
            }
    
    def _calculate_risk_metrics(self, holdings: List[Dict], portfolio_data: Dict) -> Dict:
        """Calculate various risk metrics"""
        total_value = portfolio_data.get('total_value', 1)
        
        # Sector allocation
        sector_allocation = {}
        for holding in holdings:
            sector = holding.get('sector', 'Unknown')
            value = holding.get('total_value', 0)
            sector_allocation[sector] = sector_allocation.get(sector, 0) + value
        
        # Convert to percentages
        sector_allocation_pct = {
            k: (v / total_value * 100) if total_value > 0 else 0 
            for k, v in sector_allocation.items()
        }
        
        # Diversification metrics
        num_holdings = len(holdings)
        num_sectors = len(sector_allocation)
        
        # Concentration
        max_sector_concentration = max(sector_allocation_pct.values()) if sector_allocation_pct else 0
        
        # Position sizes
        position_sizes = [
            (h.get('total_value', 0) / total_value * 100) if total_value > 0 else 0 
            for h in holdings
        ]
        max_position_size = max(position_sizes) if position_sizes else 0
        
        # Diversification score (0-100, higher is better)
        diversification_score = min(100, (num_sectors / max(num_holdings, 1)) * 100)
        
        # Volatility estimate (simplified)
        volatility = np.random.uniform(15, 35)  # In production, calculate from historical data
        
        return {
            "sector_allocation": sector_allocation_pct,
            "num_holdings": num_holdings,
            "num_sectors": num_sectors,
            "diversification_score": diversification_score,
            "max_sector_concentration": max_sector_concentration,
            "max_position_size": max_position_size,
            "estimated_volatility": volatility,
            "position_sizes": position_sizes
        }
    
    def _calculate_risk_score(self, metrics: Dict) -> float:
        """Calculate overall risk score (0-100, higher is riskier)"""
        # Weighted risk calculation
        concentration_risk = metrics['max_sector_concentration']  # 0-100
        diversification_risk = 100 - metrics['diversification_score']  # 0-100
        volatility_risk = min(100, metrics['estimated_volatility'] * 2)  # 0-100
        
        # Weighted average
        risk_score = (
            concentration_risk * 0.4 +
            diversification_risk * 0.3 +
            volatility_risk * 0.3
        )
        
        return round(risk_score, 2)
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level from score"""
        if risk_score < 30:
            return "Low"
        elif risk_score < 60:
            return "Medium"
        else:
            return "High"
    
    def _format_sector_allocation(self, sector_allocation: Dict) -> str:
        """Format sector allocation for prompt"""
        lines = []
        for sector, pct in sorted(sector_allocation.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  - {sector}: {pct:.2f}%")
        return "\n".join(lines)
    
    def _format_holdings(self, holdings: List[Dict]) -> str:
        """Format holdings for prompt"""
        lines = []
        for h in holdings[:10]:  # Limit to top 10
            lines.append(
                f"  - {h['symbol']}: ${h['total_value']:,.2f} "
                f"({h.get('sector', 'Unknown')} sector)"
            )
        return "\n".join(lines)
    
    def _extract_recommendations(self, analysis: str) -> List[str]:
        """Extract recommendations from analysis"""
        # Simplified extraction - in production, use more sophisticated NLP
        recommendations = []
        
        if "diversif" in analysis.lower():
            recommendations.append("Consider diversifying across more sectors")
        if "concentration" in analysis.lower():
            recommendations.append("Reduce concentration in top holdings")
        if "volatil" in analysis.lower():
            recommendations.append("Monitor portfolio volatility")
        if "risk" in analysis.lower():
            recommendations.append("Review risk tolerance and adjust accordingly")
        
        return recommendations[:5]