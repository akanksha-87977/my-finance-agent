'use client';

import { useState, useEffect } from 'react';
import { stockAPI } from '@/lib/api';
import { formatCurrency, formatPercent, getChangeColor } from '@/lib/utils';
import LoadingSpinner from '../common/LoadingSpinner';

export default function MarketMovers() {
  const [movers, setMovers] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMovers();
  }, []);

  const fetchMovers = async () => {
    try {
      const response = await stockAPI.getMovers();
      setMovers(response.data);
    } catch (error) {
      console.error('Failed to fetch movers:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner size="small" />;

  return (
    <div className="bg-dark-800 border border-dark-700 rounded-xl p-6">
      <h3 className="text-lg font-semibold mb-4">Market Movers</h3>

      <div className="space-y-4">
        <div>
          <h4 className="text-sm font-semibold text-green-500 mb-2">Top Gainers</h4>
          <div className="space-y-2">
            {movers?.gainers?.slice(0, 3).map((stock) => (
              <StockItem key={stock.symbol} stock={stock} />
            ))}
          </div>
        </div>

        <div>
          <h4 className="text-sm font-semibold text-red-500 mb-2">Top Losers</h4>
          <div className="space-y-2">
            {movers?.losers?.slice(0, 3).map((stock) => (
              <StockItem key={stock.symbol} stock={stock} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function StockItem({ stock }) {
  return (
    <div className="flex items-center justify-between p-2 bg-dark-900 rounded-lg">
      <div>
        <p className="font-semibold">{stock.symbol}</p>
        <p className="text-xs text-gray-400">{formatCurrency(stock.price)}</p>
      </div>
      <span className={`text-sm font-semibold ${getChangeColor(stock.changePercent)}`}>
        {formatPercent(stock.changePercent)}
      </span>
    </div>
  );
}