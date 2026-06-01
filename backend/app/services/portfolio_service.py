from sqlalchemy.orm import Session
from typing import List, Dict
from ..models import Portfolio, Holding, User
from ..schemas import PortfolioCreate, HoldingCreate
from .stock_service import StockService
import numpy as np


class PortfolioService:
    
    @staticmethod
    def create_portfolio(db: Session, user: User, portfolio: PortfolioCreate) -> Portfolio:
        """Create a new portfolio"""
        db_portfolio = Portfolio(
            user_id=user.id,
            name=portfolio.name
        )
        db.add(db_portfolio)
        db.commit()
        db.refresh(db_portfolio)
        return db_portfolio
    
    @staticmethod
    def get_user_portfolio(db: Session, user: User) -> Portfolio:
        """Get user's portfolio, create if doesn't exist"""
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
        
        if not portfolio:
            portfolio = PortfolioService.create_portfolio(
                db, user, PortfolioCreate(name="My Portfolio")
            )
        
        # Update portfolio values
        PortfolioService.update_portfolio_values(db, portfolio)
        
        return portfolio
    
    @staticmethod
    def add_holding(db: Session, portfolio: Portfolio, holding: HoldingCreate) -> Holding:
        """Add a holding to portfolio"""
        # Check if holding already exists
        existing = db.query(Holding).filter(
            Holding.portfolio_id == portfolio.id,
            Holding.symbol == holding.symbol
        ).first()
        
        if existing:
            # Update quantity and average price
            total_cost = (existing.quantity * existing.average_price) + \
                        (holding.quantity * holding.average_price)
            total_quantity = existing.quantity + holding.quantity
            existing.average_price = total_cost / total_quantity
            existing.quantity = total_quantity
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Get stock info
            stock_info = StockService.get_stock_quote(holding.symbol)
            
            # Create new holding
            db_holding = Holding(
                portfolio_id=portfolio.id,
                symbol=holding.symbol,
                quantity=holding.quantity,
                average_price=holding.average_price,
                current_price=stock_info.get("price", 0),
                sector=stock_info.get("sector", "Unknown")
            )
            
            db.add(db_holding)
            db.commit()
            db.refresh(db_holding)
            return db_holding
    
    @staticmethod
    def update_portfolio_values(db: Session, portfolio: Portfolio):
        """Update all portfolio values with current prices"""
        total_value = 0
        total_cost = 0
        
        for holding in portfolio.holdings:
            # Get current price
            stock_info = StockService.get_stock_quote(holding.symbol)
            holding.current_price = stock_info.get("price", holding.current_price)
            
            # Calculate values
            holding.total_value = holding.quantity * holding.current_price
            cost = holding.quantity * holding.average_price
            holding.gain_loss = holding.total_value - cost
            
            if cost > 0:
                holding.gain_loss_percent = (holding.gain_loss / cost) * 100
            
            total_value += holding.total_value
            total_cost += cost
        
        # Update portfolio totals
        portfolio.total_value = total_value
        portfolio.total_cost = total_cost
        portfolio.total_gain_loss = total_value - total_cost
        
        if total_cost > 0:
            portfolio.total_gain_loss_percent = (portfolio.total_gain_loss / total_cost) * 100
        
        db.commit()
    
    @staticmethod
    def calculate_portfolio_metrics(portfolio: Portfolio) -> Dict:
        """Calculate advanced portfolio metrics"""
        holdings = portfolio.holdings
        
        if not holdings:
            return {
                "diversification_score": 0,
                "risk_score": 0,
                "sector_allocation": {},
                "volatility": 0
            }
        
        # Sector allocation
        sector_allocation = {}
        for holding in holdings:
            sector = holding.sector or "Unknown"
            if sector not in sector_allocation:
                sector_allocation[sector] = 0
            sector_allocation[sector] += holding.total_value
        
        # Normalize to percentages
        total = sum(sector_allocation.values())
        if total > 0:
            sector_allocation = {k: (v/total)*100 for k, v in sector_allocation.items()}
        
        # Diversification score (higher is better)
        num_holdings = len(holdings)
        num_sectors = len(sector_allocation)
        diversification_score = min(100, (num_sectors / max(num_holdings, 1)) * 100)
        
        # Simple risk score based on sector concentration
        max_sector_allocation = max(sector_allocation.values()) if sector_allocation else 100
        risk_score = max_sector_allocation  # Higher concentration = higher risk
        
        # Mock volatility calculation (would use actual historical data)
        volatility = np.random.uniform(15, 35)
        
        return {
            "diversification_score": round(diversification_score, 2),
            "risk_score": round(risk_score, 2),
            "sector_allocation": sector_allocation,
            "volatility": round(volatility, 2),
            "num_holdings": num_holdings,
            "num_sectors": num_sectors
        }