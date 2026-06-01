'use client';

import { usePathname, useRouter } from 'next/navigation';
import {
  FaChartLine,
  FaBriefcase,
  FaComments,
  FaFileAlt,
  FaStar,
  FaHome,
  FaChartBar,
} from 'react-icons/fa';

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  const menuItems = [
    { icon: FaHome, label: 'Dashboard', path: '/dashboard' },
    { icon: FaBriefcase, label: 'Portfolio', path: '/portfolio' },
    { icon: FaComments, label: 'AI Assistant', path: '/chat' },
    { icon: FaFileAlt, label: 'Reports', path: '/reports' },
    { icon: FaStar, label: 'Watchlist', path: '/watchlist' },
    { icon: FaChartBar, label: 'Markets', path: '/markets' },
  ];

  return (
    <div className="w-64 bg-dark-800 border-r border-dark-700 min-h-screen p-4">
      <div className="space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.path;

          return (
            <button
              key={item.path}
              onClick={() => router.push(item.path)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                isActive
                  ? 'bg-primary-600 text-white'
                  : 'text-gray-400 hover:bg-dark-700 hover:text-white'
              }`}
            >
              <Icon className="text-xl" />
              <span className="font-medium">{item.label}</span>
            </button>
          );
        })}
      </div>

      <div className="mt-8 p-4 bg-dark-900 rounded-lg border border-dark-700">
        <h3 className="text-sm font-semibold mb-2">AI Analysis</h3>
        <p className="text-xs text-gray-400 mb-3">
          Get comprehensive AI-powered portfolio analysis
        </p>
        <button className="w-full py-2 bg-primary-600 hover:bg-primary-700 rounded-lg text-sm font-semibold transition">
          Run Analysis
        </button>
      </div>
    </div>
  );
}