'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import Link from 'next/link';
import apiClient from '@/lib/api/client';
import PageTransition, { StaggerContainer, StaggerItem } from '@/components/animations/page-transition';
import AnimatedButton from '@/components/animations/animated-button';

interface File {
  id: number;
  name: string;
  file_type: string;
  file_size: number;
  file_url: string;
  thumbnail_url: string;
  uploaded_by: {
    id: number;
    full_name: string;
  };
  folder_name: string | null;
  is_public: boolean;
  is_starred: boolean;
  uploaded_at: string;
}

export default function FilesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');

  const { data: files, isLoading } = useQuery<File[]>({
    queryKey: ['files'],
    queryFn: async () => {
      const response = await apiClient.get('/files/');
      return response.data.results || response.data;
    },
  });

  const filteredFiles = files?.filter((file) => {
    const matchesSearch = file.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === 'all' || file.file_type === filterType;
    return matchesSearch && matchesType;
  });

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
  };

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'image':
        return '🖼️';
      case 'video':
        return '🎬';
      case 'audio':
        return '🎵';
      case 'document':
        return '📄';
      case 'spreadsheet':
        return '📊';
      case 'presentation':
        return '📽️';
      case 'pdf':
        return '📕';
      case 'archive':
        return '📦';
      case 'code':
        return '💻';
      default:
        return '📎';
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
                <h1 className="text-3xl font-bold text-gray-900">Files</h1>
                <p className="text-gray-600 mt-1">
                  {filteredFiles?.length || 0} file{filteredFiles?.length !== 1 ? 's' : ''}
                </p>
              </div>
              <Link href="/files/upload">
                <AnimatedButton variant="primary" size="lg">
                  + Upload File
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
                  placeholder="Search files..."
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
                <option value="image">Images</option>
                <option value="document">Documents</option>
                <option value="spreadsheet">Spreadsheets</option>
                <option value="video">Videos</option>
                <option value="pdf">PDFs</option>
              </select>
            </div>
          </motion.div>

          {/* Files Grid */}
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
            </div>
          ) : filteredFiles && filteredFiles.length > 0 ? (
            <StaggerContainer>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {filteredFiles.map((file) => (
                  <StaggerItem key={file.id}>
                    <Link href={file.file_url} target="_blank">
                      <motion.div
                        whileHover={{ y: -4, boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)' }}
                        className="bg-white rounded-lg border border-gray-200 p-4 cursor-pointer transition-all"
                      >
                        <div className="aspect-square bg-gray-100 rounded-lg mb-3 flex items-center justify-center overflow-hidden">
                          {file.thumbnail_url ? (
                            <img
                              src={file.thumbnail_url}
                              alt={file.name}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <span className="text-6xl">{getFileIcon(file.file_type)}</span>
                          )}
                        </div>

                        <div className="space-y-1">
                          <h3 className="font-medium text-gray-900 truncate" title={file.name}>
                            {file.name}
                          </h3>
                          <div className="flex items-center justify-between text-xs text-gray-500">
                            <span>{formatFileSize(file.file_size)}</span>
                            {file.is_starred && <span>⭐</span>}
                          </div>
                          <p className="text-xs text-gray-500 truncate">
                            {file.uploaded_by.full_name}
                          </p>
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
              <div className="text-6xl mb-4">📁</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No files found
              </h3>
              <p className="text-gray-600 mb-6">
                {searchQuery
                  ? 'Try adjusting your search or filters'
                  : 'Get started by uploading your first file'}
              </p>
              <Link href="/files/upload">
                <AnimatedButton variant="primary">
                  Upload File
                </AnimatedButton>
              </Link>
            </motion.div>
          )}
        </div>
      </div>
    </PageTransition>
  );
}
