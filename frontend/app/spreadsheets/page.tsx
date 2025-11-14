'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import Link from 'next/link';
import apiClient from '@/lib/api/client';
import PageTransition, { StaggerContainer, StaggerItem } from '@/components/animations/page-transition';
import AnimatedButton from '@/components/animations/animated-button';

interface Spreadsheet {
  id: number;
  title: string;
  slug: string;
  created_by: {
    id: number;
    email: string;
    full_name: string;
  };
  last_edited_by: {
    id: number;
    email: string;
    full_name: string;
  };
  is_archived: boolean;
  permission_level: string;
  view_count: number;
  sheet_count: number;
  updated_at: string;
  created_at: string;
}

export default function SpreadsheetsPage() {
  const [searchQuery, setSearchQuery] = useState('');

  const { data: spreadsheets, isLoading } = useQuery<Spreadsheet[]>({
    queryKey: ['spreadsheets'],
    queryFn: async () => {
      const response = await apiClient.get('/spreadsheets/');
      return response.data.results || response.data;
    },
  });

  const filteredSpreadsheets = spreadsheets?.filter((sheet) => {
    const matchesSearch = sheet.title.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSearch && !sheet.is_archived;
  });

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

    if (diffHours < 24) {
      if (diffHours === 0) {
        const diffMins = Math.floor(diffMs / (1000 * 60));
        return diffMins < 1 ? 'Just now' : `${diffMins}m ago`;
      }
      return `${diffHours}h ago`;
    } else if (diffHours < 48) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString();
    }
  };

  return (
    <PageTransition>
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Spreadsheets</h1>
                <p className="text-gray-600 mt-1">
                  {filteredSpreadsheets?.length || 0} spreadsheet{filteredSpreadsheets?.length !== 1 ? 's' : ''}
                </p>
              </div>
              <Link href="/spreadsheets/new">
                <AnimatedButton variant="primary" size="lg">
                  + New Spreadsheet
                </AnimatedButton>
              </Link>
            </div>
          </motion.div>

          {/* Search */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-lg border border-gray-200 p-4 mb-6"
          >
            <input
              type="text"
              placeholder="Search spreadsheets..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </motion.div>

          {/* Spreadsheets List */}
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600" />
            </div>
          ) : filteredSpreadsheets && filteredSpreadsheets.length > 0 ? (
            <StaggerContainer>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredSpreadsheets.map((sheet) => (
                  <StaggerItem key={sheet.id}>
                    <Link href={`/spreadsheets/${sheet.id}`}>
                      <motion.div
                        whileHover={{ y: -4, boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)' }}
                        className="bg-white rounded-lg border border-gray-200 p-6 cursor-pointer transition-all"
                      >
                        <div className="flex items-start gap-4">
                          <div className="text-4xl">📊</div>
                          <div className="flex-1 min-w-0">
                            <h3 className="font-semibold text-gray-900 truncate mb-1">
                              {sheet.title}
                            </h3>
                            <div className="text-sm text-gray-600 space-y-1">
                              <p className="truncate">
                                by {sheet.created_by.full_name}
                              </p>
                              <p>Updated {formatDate(sheet.updated_at)}</p>
                            </div>
                            <div className="flex items-center gap-3 mt-3 text-xs text-gray-500">
                              <span>{sheet.sheet_count || 0} sheets</span>
                              <span>•</span>
                              <span>{sheet.view_count} views</span>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    </Link>
                  </StaggerItem>
                ))}
              </div>
            </StaggerContainer>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-white rounded-lg border border-gray-200 p-12 text-center"
            >
              <div className="text-6xl mb-4">📊</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No spreadsheets found
              </h3>
              <p className="text-gray-600 mb-6">
                {searchQuery
                  ? 'Try adjusting your search'
                  : 'Get started by creating your first spreadsheet'}
              </p>
              <Link href="/spreadsheets/new">
                <AnimatedButton variant="primary">
                  Create Spreadsheet
                </AnimatedButton>
              </Link>
            </motion.div>
          )}
        </div>
      </div>
    </PageTransition>
  );
}
