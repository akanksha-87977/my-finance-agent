'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { isTokenValid } from '@/lib/auth';
import AppShell from '@/components/layout/AppShell';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import Watchlist from '@/components/dashboard/Watchlist';

export default function WatchlistPage() {
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
        <LoadingSpinner text="Loading watchlist..." />
      </div>
    );
  }

  return (
    <AppShell>
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Watchlist</h1>
        <p className="text-gray-400">Track the stocks you care about</p>
      </div>
      <Watchlist />
    </AppShell>
  );
}

