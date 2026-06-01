'use client';

import { formatCurrency, formatPercent, getChangeColor } from '@/lib/utils';
import { FaArrowUp, FaArrowDown } from 'react-icons/fa';

export default function PortfolioOverview({ portfolio }) {
  const isPositive = portfolio?.total_gain_loss >= 0;

  return (
    <div className="grid md:grid-cols-3 gap-6">
      <StatCard
        title="Total Value"
        value={formatCurrency(portfolio?.total_value || 0)}
        subtitle="Portfolio value"
        color="text-primary-500"
      />
      <StatCard
        title="Total Return"
        value={formatCurrency(portfolio?.total_gain_loss || 0)}
        subtitle={formatPercent(portfolio?.total_gain_loss_percent || 0)}
        color={getChangeColor(portfolio?.total_gain_loss || 0)}
        icon={isPositive ? <FaArrowUp /> : <FaArrowDown />}
      />
      <StatCard
        title="Total Invested"
        value={formatCurrency(portfolio?.total_cost || 0)}
        subtitle={`${portfolio?.holdings?.length || 0} holdings`}
        color="text-gray-400"
      />
    </div>
  );
}

function StatCard({ title, value, subtitle, color, icon }) {
  return (
    <div className="bg-dark-800 border border-dark-700 rounded-xl p-6 card-hover">
      <p className="text-sm text-gray-400 mb-2">{title}</p>
      <div className="flex items-end gap-2">
        <h3 className={`text-3xl font-bold ${color}`}>{value}</h3>
        {icon && <span className={color}>{icon}</span>}
      </div>
      <p className="text-sm text-gray-500 mt-2">{subtitle}</p>
    </div>
  );
}