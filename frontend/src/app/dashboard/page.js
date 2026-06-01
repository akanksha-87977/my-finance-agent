'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isTokenValid } from '@/lib/auth';
import { portfolioAPI, stockAPI } from '@/lib/api';
import AppShell from '@/components/layout/AppShell';

import PortfolioOverview from '@/components/dashboard/PortfolioOverview';
import AssetAllocation from '@/components/dashboard/AssetAllocation';
import MarketMovers from '@/components/dashboard/MarketMovers';
import Watchlist from '@/components/dashboard/Watchlist';
import LoadingSpinner from '@/components/common/LoadingSpinner';

export default function Dashboard() {
  const router = useRouter();
  const [portfolio, setPortfolio] = useState(null);
  const [trending, setTrending] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isTokenValid()) {
      router.push('/login');
      return;
    }
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [portfolioRes, trendingRes] = await Promise.all([
        portfolioAPI.getPortfolio(),
        stockAPI.getTrending(),
      ]);
      setPortfolio(portfolioRes.data);
      setTrending(trendingRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner text="Loading dashboard..." />
      </div>
    );
  }

  return (
    <AppShell>
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
        <p className="text-gray-400">Welcome to your Financial AI Platform</p>
      </div>

      <div className="space-y-6">
        <PortfolioOverview portfolio={portfolio} />

        <div className="grid md:grid-cols-2 gap-6">
          <AssetAllocation holdings={portfolio?.holdings || []} />
          <MarketMovers />
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <Watchlist />
          <TrendingStocks stocks={trending} />
        </div>
      </div>
    </AppShell>
  );
}

function TrendingStocks({ stocks }) {
  return (
    <div className="bg-dark-800 border border-dark-700 rounded-xl p-6">
      <h3 className="text-lg font-semibold mb-4">Trending Stocks</h3>
      <div className="space-y-2">
        {stocks.slice(0, 6).map((stock) => (
          <div
            key={stock.symbol}
            className="flex items-center justify-between p-3 bg-dark-900 rounded-lg"
          >
            <div>
              <p className="font-semibold">{stock.symbol}</p>
              <p className="text-xs text-gray-400">{stock.name}</p>
            </div>
            <div className="text-right">
              <p className="font-semibold">${stock.price?.toFixed(2)}</p>
              <p className={`text-xs ${stock.changePercent >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                {stock.changePercent >= 0 ? '+' : ''}
                {stock.changePercent?.toFixed(2)}%
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}