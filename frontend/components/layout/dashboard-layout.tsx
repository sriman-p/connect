'use client';

/**
 * Dashboard Layout Component
 * Main layout wrapper for authenticated pages
 */

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Sidebar } from './sidebar';
import { useAuthStore } from '@/lib/stores/auth-store';
import { isAuthenticated } from '@/lib/utils/token';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const router = useRouter();
  const { checkAuth, fetchProfile, user } = useAuthStore();

  useEffect(() => {
    // Check authentication on mount
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    checkAuth();

    // Fetch profile if not already loaded
    if (!user) {
      fetchProfile();
    }
  }, [checkAuth, fetchProfile, router, user]);

  // Show loading state while checking auth
  if (!isAuthenticated()) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50 dark:bg-gray-950">
      {/* Sidebar */}
      <div className="hidden md:flex md:w-64 md:flex-col">
        <Sidebar />
      </div>

      {/* Main content */}
      <div className="flex flex-col flex-1 overflow-hidden">
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
