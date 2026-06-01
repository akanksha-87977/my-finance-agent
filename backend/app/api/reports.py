from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
from datetime import datetime

from ..database import get_db
from ..models import User, AIReport
from ..schemas import AgentAnalysisRequest
from ..services import PortfolioService, PDFService

from ..utils.dependencies import get_current_active_user
from ..agents import AgentOrchestrator


router = APIRouter(prefix="/api/reports", tags=["Reports"])



@router.post("/analyze-portfolio")
async def analyze_portfolio(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Run comprehensive portfolio analysis using all AI agents"""
    
    # Get portfolio data
    portfolio = PortfolioService.get_user_portfolio(db, current_user)
    
    portfolio_data = {
        "total_value": portfolio.total_value,
        "total_cost": portfolio.total_cost,
        "total_gain_loss": portfolio.total_gain_loss,
        "total_gain_loss_percent": portfolio.total_gain_loss_percent,
        "holdings": [
            {
                "symbol": h.symbol,
                "quantity": h.quantity,
                "average_price": h.average_price,
                "current_price": h.current_price,
                "total_value": h.total_value,
                "gain_loss": h.gain_loss,
                "gain_loss_percent": h.gain_loss_percent,
                "sector": h.sector
            }
            for h in portfolio.holdings
        ]
    }
    
    # Run comprehensive analysis
    try:
        orchestrator = AgentOrchestrator()
        analysis = await orchestrator.analyze_portfolio_comprehensive(portfolio_data)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {exc}")

    
    # Save report to database
    report = AIReport(
        user_id=current_user.id,
        report_type="portfolio_analysis",
        title=f"Portfolio Analysis - {datetime.now().strftime('%Y-%m-%d')}",
        content=analysis,
        summary=analysis.get('report', {}).get('summary', '')
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return {
        "report_id": report.id,
        "analysis": analysis,
        "status": "completed"
    }


@router.post("/analyze-stock/{symbol}")
async def analyze_stock(
    symbol: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Analyze a specific stock"""
    
    try:
        orchestrator = AgentOrchestrator()
        analysis = await orchestrator.analyze_stock(symbol)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {exc}")
    
    # Save report
    report = AIReport(
        user_id=current_user.id,
        report_type="stock_research",
        title=f"{symbol} Research Report - {datetime.now().strftime('%Y-%m-%d')}",
        content=analysis,
        summary=f"Analysis for {symbol}"
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return {
        "report_id": report.id,
        "analysis": analysis,
        "status": "completed"
    }


@router.get("/")
def get_reports(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all user reports"""
    reports = db.query(AIReport).filter(
        AIReport.user_id == current_user.id
    ).order_by(AIReport.created_at.desc()).all()
    
    return reports


@router.get("/{report_id}")
def get_report(
    report_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific report"""
    report = db.query(AIReport).filter(
        AIReport.id == report_id,
        AIReport.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report


@router.post("/{report_id}/generate-pdf")
async def generate_pdf_report(
    report_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate PDF version of report"""
    
    report = db.query(AIReport).filter(
        AIReport.id == report_id,
        AIReport.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Create reports directory if not exists
    os.makedirs("reports", exist_ok=True)
    
    # Generate PDF
    filename = f"report_{report_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join("reports", filename)
    
    # Get portfolio data for PDF
    portfolio = PortfolioService.get_user_portfolio(db, current_user)
    portfolio_data = {
        "total_value": portfolio.total_value,
        "total_cost": portfolio.total_cost,
        "total_gain_loss": portfolio.total_gain_loss,
        "total_gain_loss_percent": portfolio.total_gain_loss_percent,
        "holdings": [
            {
                "symbol": h.symbol,
                "quantity": h.quantity,
                "average_price": h.average_price,
                "current_price": h.current_price,
                "total_value": h.total_value,
                "gain_loss": h.gain_loss,
                "gain_loss_percent": h.gain_loss_percent
            }
            for h in portfolio.holdings
        ]
    }
    
    analysis = report.content
    
    PDFService.generate_portfolio_report(portfolio_data, analysis, filepath)
    
    # Update report with file path
    report.file_path = filepath
    db.commit()
    
    return {
        "message": "PDF generated successfully",
        "filename": filename,
        "filepath": filepath
    }


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Download PDF report"""
    
    report = db.query(AIReport).filter(
        AIReport.id == report_id,
        AIReport.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if not report.file_path or not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    return FileResponse(
        report.file_path,
        media_type="application/pdf",
        filename=os.path.basename(report.file_path)
    )