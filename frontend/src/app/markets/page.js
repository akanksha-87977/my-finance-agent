'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { isTokenValid } from '@/lib/auth';
import AppShell from '@/components/layout/AppShell';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import MarketMovers from '@/components/dashboard/MarketMovers';

export default function MarketsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isTokenValid()) {
      router.push('/login');
      return;
    }
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner text="Loading markets..." />
      </div>
    );
  }

  return (
    <AppShell>
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Markets</h1>
        <p className="text-gray-400">Market movers and trending activity</p>
      </div>
      <MarketMovers />
    </AppShell>
  );
}

