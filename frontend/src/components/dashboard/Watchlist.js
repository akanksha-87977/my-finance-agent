'use client';

import { useState, useEffect } from 'react';
import { portfolioAPI, stockAPI } from '@/lib/api';
import { formatCurrency, formatPercent, getChangeColor } from '@/lib/utils';
import toast from 'react-hot-toast';
import { FaPlus, FaTimes } from 'react-icons/fa';

export default function Watchlist() {
  const [watchlist, setWatchlist] = useState([]);
  const [quotes, setQuotes] = useState({});
  const [showAdd, setShowAdd] = useState(false);
  const [symbol, setSymbol] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWatchlist();
  }, []);

  const fetchWatchlist = async () => {
    try {
      const response = await portfolioAPI.getWatchlist();
      setWatchlist(response.data);

      // Fetch quotes for each symbol
      const quotesData = {};
      for (const item of response.data) {
        try {
          const quoteResponse = await stockAPI.getQuote(item.symbol);
          quotesData[item.symbol] = quoteResponse.data;
        } catch (error) {
          console.error(`Failed to fetch quote for ${item.symbol}`);
        }
      }
      setQuotes(quotesData);
    } catch (error) {
      console.error('Failed to fetch watchlist:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    try {
      await portfolioAPI.addToWatchlist({ symbol: symbol.toUpperCase() });
      toast.success('Added to watchlist');
      setSymbol('');
      setShowAdd(false);
      fetchWatchlist();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add to watchlist');
    }
  };

  const handleRemove = async (id) => {
    try {
      await portfolioAPI.removeFromWatchlist(id);
      toast.success('Removed from watchlist');
      fetchWatchlist();
    } catch (error) {
      toast.error('Failed to remove from watchlist');
    }
  };

  return (
    <div className="bg-dark-800 border border-dark-700 rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Watchlist</h3>
        <button
          onClick={() => setShowAdd(!showAdd)}
          className="p-2 bg-primary-600 hover:bg-primary-700 rounded-lg transition"
        >
          <FaPlus />
        </button>
      </div>

      {showAdd && (
        <form onSubmit={handleAdd} className="mb-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              placeholder="Enter symbol (e.g., AAPL)"
              className="flex-1 px-3 py-2 bg-dark-900 border border-dark-600 rounded-lg focus:outline-none focus:border-primary-500"
              required
            />
            <button
              type="submit"
              className="px-4 py-2 bg-primary-600 hover:bg-primary-700 rounded-lg font-semibold transition"
            >
              Add
            </button>
          </div>
        </form>
      )}

      <div className="space-y-2">
        {watchlist.map((item) => {
          const quote = quotes[item.symbol];
          return (
            <div
              key={item.id}
              className="flex items-center justify-between p-3 bg-dark-900 rounded-lg"
            >
              <div>
                <p className="font-semibold">{item.symbol}</p>
                <p className="text-xs text-gray-400">{quote?.name || item.name}</p>
              </div>
              <div className="flex items-center gap-3">
                {quote && (
                  <div className="text-right">
                    <p className="font-semibold">{formatCurrency(quote.price)}</p>
                    <p className={`text-xs ${getChangeColor(quote.changePercent)}`}>
                      {formatPercent(quote.changePercent)}
                    </p>
                  </div>
                )}
                <button
                  onClick={() => handleRemove(item.id)}
                  className="p-2 text-red-400 hover:bg-red-500/10 rounded-lg transition"
                >
                  <FaTimes />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}