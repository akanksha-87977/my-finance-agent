'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isTokenValid } from '@/lib/auth';
import { portfolioAPI, stockAPI } from '@/lib/api';
import { formatCurrency, formatPercent, getChangeColor } from '@/lib/utils';
import AppShell from '@/components/layout/AppShell';

import StockChart from '@/components/common/StockChart';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import toast from 'react-hot-toast';
import { FaPlus, FaTrash, FaChartLine } from 'react-icons/fa';

export default function Portfolio() {
  const router = useRouter();
  const [portfolio, setPortfolio] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedStock, setSelectedStock] = useState(null);
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
      const [portfolioRes, metricsRes] = await Promise.all([
        portfolioAPI.getPortfolio(),
        portfolioAPI.getMetrics(),
      ]);
      setPortfolio(portfolioRes.data);
      setMetrics(metricsRes.data);
    } catch (error) {
      console.error('Failed to fetch portfolio:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this holding?')) return;

    try {
      await portfolioAPI.deleteHolding(id);
      toast.success('Holding deleted');
      fetchData();
    } catch (error) {
      toast.error('Failed to delete holding');
    }
  };

  const handleViewChart = async (symbol) => {
    try {
      const response = await stockAPI.getHistory(symbol, '3mo');
      setSelectedStock({ symbol, data: response.data });
    } catch (error) {
      toast.error('Failed to load chart');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner text="Loading portfolio..." />
      </div>
    );
  }

  return (
    <AppShell>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Portfolio</h1>
          <p className="text-gray-400">Manage your investments</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 rounded-lg font-semibold transition"
        >
          <FaPlus /> Add Holding
        </button>
      </div>

      {/* Metrics Cards */}
      <div className="grid md:grid-cols-4 gap-4 mb-6">
        <MetricCard
          title="Diversification Score"
          value={`${metrics?.diversification_score || 0}%`}
          color="text-blue-500"
        />
        <MetricCard
          title="Risk Score"
          value={`${metrics?.risk_score || 0}%`}
          color="text-yellow-500"
        />
        <MetricCard
          title="Holdings"
          value={metrics?.num_holdings || 0}
          color="text-green-500"
        />
        <MetricCard
          title="Sectors"
          value={metrics?.num_sectors || 0}
          color="text-purple-500"
        />
      </div>

      {/* Holdings Table */}
      <div className="bg-dark-800 border border-dark-700 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-dark-900">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-semibold">Symbol</th>
                <th className="px-6 py-4 text-right text-sm font-semibold">Quantity</th>
                <th className="px-6 py-4 text-right text-sm font-semibold">Avg Price</th>
                <th className="px-6 py-4 text-right text-sm font-semibold">Current Price</th>
                <th className="px-6 py-4 text-right text-sm font-semibold">Total Value</th>
                <th className="px-6 py-4 text-right text-sm font-semibold">Gain/Loss</th>
                <th className="px-6 py-4 text-right text-sm font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {portfolio?.holdings?.map((holding) => (
                <tr key={holding.id} className="border-t border-dark-700">
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-semibold">{holding.symbol}</p>
                      <p className="text-xs text-gray-400">{holding.sector}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right">{holding.quantity}</td>
                  <td className="px-6 py-4 text-right">{formatCurrency(holding.average_price)}</td>
                  <td className="px-6 py-4 text-right">{formatCurrency(holding.current_price)}</td>
                  <td className="px-6 py-4 text-right font-semibold">
                    {formatCurrency(holding.total_value)}
                  </td>
                  <td className={`px-6 py-4 text-right font-semibold ${getChangeColor(holding.gain_loss)}`}>
                    <div>
                      <div>{formatCurrency(holding.gain_loss)}</div>
                      <div className="text-xs">{formatPercent(holding.gain_loss_percent)}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => handleViewChart(holding.symbol)}
                        className="p-2 text-primary-500 hover:bg-primary-500/10 rounded-lg transition"
                      >
                        <FaChartLine />
                      </button>
                      <button
                        onClick={() => handleDelete(holding.id)}
                        className="p-2 text-red-500 hover:bg-red-500/10 rounded-lg transition"
                      >
                        <FaTrash />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Sector Allocation */}
      {metrics?.sector_allocation && (
        <div className="mt-6 bg-dark-800 border border-dark-700 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Sector Allocation</h3>
          <div className="space-y-3">
            {Object.entries(metrics.sector_allocation).map(([sector, percentage]) => (
              <div key={sector}>
                <div className="flex justify-between text-sm mb-1">
                  <span>{sector}</span>
                  <span>{percentage.toFixed(2)}%</span>
                </div>
                <div className="h-2 bg-dark-900 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary-600"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Add Holding Modal */}
      {showAddModal && (
        <AddHoldingModal
          onClose={() => setShowAddModal(false)}
          onSuccess={() => {
            setShowAddModal(false);
            fetchData();
          }}
        />
      )}

      {/* Chart Modal */}
      {selectedStock && (
        <ChartModal
          stock={selectedStock}
          onClose={() => setSelectedStock(null)}
        />
      )}
    </AppShell>
  );
}

function MetricCard({ title, value, color }) {
  return (
    <div className="bg-dark-800 border border-dark-700 rounded-xl p-4">
      <p className="text-sm text-gray-400 mb-1">{title}</p>
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
    </div>
  );
}

function AddHoldingModal({ onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    symbol: '',
    quantity: '',
    average_price: '',
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await portfolioAPI.addHolding({
        symbol: formData.symbol.toUpperCase(),
        quantity: parseFloat(formData.quantity),
        average_price: parseFloat(formData.average_price),
      });
      toast.success('Holding added successfully');
      onSuccess();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add holding');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-dark-800 border border-dark-700 rounded-xl p-6 max-w-md w-full">
        <h2 className="text-xl font-bold mb-4">Add Holding</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Symbol</label>
            <input
              type="text"
              value={formData.symbol}
              onChange={(e) => setFormData({ ...formData, symbol: e.target.value })}
              className="w-full px-4 py-2 bg-dark-900 border border-dark-600 rounded-lg focus:outline-none focus:border-primary-500"
              placeholder="AAPL"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Quantity</label>
            <input
              type="number"
              step="0.01"
              value={formData.quantity}
              onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
              className="w-full px-4 py-2 bg-dark-900 border border-dark-600 rounded-lg focus:outline-none focus:border-primary-500"
              placeholder="10"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Average Price</label>
            <input
              type="number"
              step="0.01"
              value={formData.average_price}
              onChange={(e) => setFormData({ ...formData, average_price: e.target.value })}
              className="w-full px-4 py-2 bg-dark-900 border border-dark-600 rounded-lg focus:outline-none focus:border-primary-500"
              placeholder="150.00"
              required
            />
          </div>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2 bg-dark-700 hover:bg-dark-600 rounded-lg font-semibold transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-dark-600 rounded-lg font-semibold transition"
            >
              {loading ? 'Adding...' : 'Add'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function ChartModal({ stock, onClose }) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-dark-800 border border-dark-700 rounded-xl p-6 max-w-4xl w-full">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">{stock.symbol} - Price Chart</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-dark-700 rounded-lg transition"
          >
            ✕
          </button>
        </div>
        <StockChart data={stock.data} />
      </div>
    </div>
  );
}