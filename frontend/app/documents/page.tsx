'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { apiClient } from '@/lib/api/client';
import PageTransition, { StaggerContainer, StaggerItem } from '@/components/animations/page-transition';
import AnimatedButton from '@/components/animations/animated-button';

interface Document {
  id: number;
  title: string;
  slug: string;
  doc_type: string;
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
  word_count: number;
  view_count: number;
  updated_at: string;
  created_at: string;
}

export default function DocumentsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');

  const { data: documents, isLoading } = useQuery<Document[]>({
    queryKey: ['documents'],
    queryFn: async () => {
      const response = await apiClient.get('/documents/');
      return response.data.results || response.data;
    },
  });

  const filteredDocuments = documents?.filter((doc) => {
    const matchesSearch = doc.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === 'all' || doc.doc_type === filterType;
    return matchesSearch && matchesType && !doc.is_archived;
  });

  const getDocIcon = (type: string) => {
    switch (type) {
      case 'doc':
        return '📄';
      case 'sheet':
        return '📊';
      case 'slide':
        return '📽️';
      case 'form':
        return '📋';
      default:
        return '📄';
    }
  };

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
                <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
                <p className="text-gray-600 mt-1">
                  {filteredDocuments?.length || 0} document{filteredDocuments?.length !== 1 ? 's' : ''}
                </p>
              </div>
              <Link href="/documents/new">
                <AnimatedButton variant="primary" size="lg">
                  + New Document
                </AnimatedButton>
              </Link>
            </div>
          </motion.div>

          {/* Filters */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-lg border border-gray-200 p-4 mb-6"
          >
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="Search documents..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Types</option>
                <option value="doc">Documents</option>
                <option value="sheet">Spreadsheets</option>
                <option value="slide">Presentations</option>
                <option value="form">Forms</option>
              </select>
            </div>
          </motion.div>

          {/* Documents List */}
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
            </div>
          ) : filteredDocuments && filteredDocuments.length > 0 ? (
            <StaggerContainer>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredDocuments.map((doc) => (
                  <StaggerItem key={doc.id}>
                    <Link href={`/documents/${doc.id}`}>
                      <motion.div
                        whileHover={{ y: -4, boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)' }}
                        className="bg-white rounded-lg border border-gray-200 p-6 cursor-pointer transition-all"
                      >
                        <div className="flex items-start gap-4">
                          <div className="text-4xl">{getDocIcon(doc.doc_type)}</div>
                          <div className="flex-1 min-w-0">
                            <h3 className="font-semibold text-gray-900 truncate mb-1">
                              {doc.title}
                            </h3>
                            <div className="text-sm text-gray-600 space-y-1">
                              <p className="truncate">
                                by {doc.created_by.full_name}
                              </p>
                              <p>Updated {formatDate(doc.updated_at)}</p>
                            </div>
                            <div className="flex items-center gap-3 mt-3 text-xs text-gray-500">
                              <span>{doc.word_count} words</span>
                              <span>•</span>
                              <span>{doc.view_count} views</span>
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
              <div className="text-6xl mb-4">📄</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No documents found
              </h3>
              <p className="text-gray-600 mb-6">
                {searchQuery
                  ? 'Try adjusting your search or filters'
                  : 'Get started by creating your first document'}
              </p>
              <Link href="/documents/new">
                <AnimatedButton variant="primary">
                  Create Document
                </AnimatedButton>
              </Link>
            </motion.div>
          )}
        </div>
      </div>
    </PageTransition>
  );
}
