# Multi-Agent AI Financial Research & Portfolio Intelligence Platform

A comprehensive, enterprise-grade financial intelligence platform powered by multiple AI agents that collaborate to analyze portfolios, assess risk, and provide investment recommendations.

![Platform Banner](https://img.shields.io/badge/AI-Powered-blue) ![Tech Stack](https://img.shields.io/badge/Tech-Full%20Stack-green) ![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

## 🌟 Features

### Core Capabilities

- **Multi-Agent AI System**: 5 specialized AI agents working collaboratively
  - Market Research Agent
  - News Sentiment Agent
  - Risk Analysis Agent
  - Portfolio Optimization Agent
  - Report Generation Agent

- **Real-time Portfolio Management**
  - Live stock price tracking
  - Portfolio performance analytics
  - Asset allocation visualization
  - Gain/loss tracking

- **AI-Powered Analysis**
  - Comprehensive portfolio analysis
  - Risk assessment and scoring
  - Sentiment analysis from news
  - Investment recommendations

- **Interactive AI Chat Assistant**
  - Natural language queries
  - Context-aware responses
  - Portfolio-specific insights

- **Professional Reporting**
  - AI-generated reports
  - PDF export capability
  - Institutional-grade analysis

- **Market Intelligence**
  - Real-time stock data
  - Market movers tracking
  - Trending stocks
  - Historical charts

## 🏗️ Architecture

### Tech Stack

**Frontend:**
- Next.js 14
- React 18
- Tailwind CSS
- Recharts
- Axios

**Backend:**
- FastAPI (Python)
- SQLAlchemy ORM
- PostgreSQL
- JWT Authentication

**AI & ML:**
- OpenAI GPT-4
- LangChain
- CrewAI
- Vector Database (ChromaDB/Pinecone)

**Infrastructure:**
- Docker
- Docker Compose
- RESTful APIs

## 📦 Installation

### Prerequisites

- Docker & Docker Compose
- OpenAI API Key
- (Optional) Stock API keys (Alpha Vantage, Finnhub, News API)

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/financial-ai-platform.git
cd financial-ai-platform

/////To run frontend + backend simultaneously://///

Backend (Terminal 1)
cd backend
.\..venv\Scripts\python -m uvicorn app.main_entry:app --host 0.0.0.0 --port 8000 --reload

cd backend && .\.venv\Scripts\python.exe -m uvicorn app.main_entry:app --host 0.0.0.0 --port 8000 --reload
Frontend (Terminal 2)
cd frontend
npm install
npm run dev

Then open the frontend URL printed by npm run dev (typically http://localhost:3000).

