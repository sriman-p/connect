'use client';

import { usePathname } from 'next/navigation';
import Sidebar from './sidebar';
import Header from './header';

interface AppLayoutProps {
  children: React.ReactNode;
}

const publicPaths = ['/login', '/register', '/'];

export default function AppLayout({ children }: AppLayoutProps) {
  const pathname = usePathname();
  const isPublicPath = publicPaths.includes(pathname || '');

  if (isPublicPath) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <div className="pl-64">
        <Header />
        <main className="pt-16">
          {children}
        </main>
      </div>
    </div>
  );
}
