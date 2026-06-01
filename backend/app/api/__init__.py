from fastapi import APIRouter
from .auth import router as auth_router
from .portfolio import router as portfolio_router
from .stocks import router as stocks_router
from .chat import router as chat_router
from .reports import router as reports_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(portfolio_router)
api_router.include_router(stocks_router)
api_router.include_router(chat_router)
api_router.include_router(reports_router)

__all__ = ["api_router"]