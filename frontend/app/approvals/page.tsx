'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import Link from 'next/link';
import apiClient from '@/lib/api/client';
import PageTransition, { StaggerContainer, StaggerItem } from '@/components/animations/page-transition';
import AnimatedButton from '@/components/animations/animated-button';

interface ApprovalRequest {
  id: number;
  title: string;
  workflow_name: string;
  status: string;
  priority: string;
  requester: {
    id: number;
    full_name: string;
  };
  due_date: string | null;
  created_at: string;
}

export default function ApprovalsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const { data: approvals, isLoading } = useQuery<ApprovalRequest[]>({
    queryKey: ['approvals'],
    queryFn: async () => {
      const response = await apiClient.get('/approvals/requests/');
      return response.data.results || response.data;
    },
  });

  const filteredApprovals = approvals?.filter((approval) => {
    const matchesSearch = approval.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = filterStatus === 'all' || approval.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'approved':
        return 'bg-green-100 text-green-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      case 'cancelled':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'text-red-600';
      case 'high':
        return 'text-orange-600';
      case 'normal':
        return 'text-gray-600';
      case 'low':
        return 'text-gray-400';
      default:
        return 'text-gray-600';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
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
                <h1 className="text-3xl font-bold text-gray-900">Approvals</h1>
                <p className="text-gray-600 mt-1">
                  {filteredApprovals?.length || 0} request{filteredApprovals?.length !== 1 ? 's' : ''}
                </p>
              </div>
              <Link href="/approvals/new">
                <AnimatedButton variant="primary" size="lg">
                  + New Request
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
                  placeholder="Search approval requests..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
          </motion.div>

          {/* Approvals List */}
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
            </div>
          ) : filteredApprovals && filteredApprovals.length > 0 ? (
            <StaggerContainer>
              <div className="space-y-4">
                {filteredApprovals.map((approval) => (
                  <StaggerItem key={approval.id}>
                    <Link href={`/approvals/${approval.id}`}>
                      <motion.div
                        whileHover={{ scale: 1.01, boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)' }}
                        className="bg-white rounded-lg border border-gray-200 p-6 cursor-pointer transition-all"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="text-lg font-semibold text-gray-900">
                                {approval.title}
                              </h3>
                              <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(approval.status)}`}>
                                {approval.status.toUpperCase()}
                              </span>
                              <span className={`text-sm font-medium ${getPriorityColor(approval.priority)}`}>
                                {approval.priority.charAt(0).toUpperCase() + approval.priority.slice(1)} Priority
                              </span>
                            </div>

                            <div className="flex items-center gap-6 text-sm text-gray-600">
                              <div className="flex items-center gap-2">
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                                <span>{approval.workflow_name}</span>
                              </div>

                              <div className="flex items-center gap-2">
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                </svg>
                                <span>{approval.requester.full_name}</span>
                              </div>

                              <div className="flex items-center gap-2">
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                                <span>Created {formatDate(approval.created_at)}</span>
                              </div>

                              {approval.due_date && (
                                <div className="flex items-center gap-2">
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                  </svg>
                                  <span>Due {formatDate(approval.due_date)}</span>
                                </div>
                              )}
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
              <div className="text-6xl mb-4">✅</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No approval requests found
              </h3>
              <p className="text-gray-600 mb-6">
                {searchQuery
                  ? 'Try adjusting your search or filters'
                  : 'Get started by creating your first approval request'}
              </p>
              <Link href="/approvals/new">
                <AnimatedButton variant="primary">
                  New Request
                </AnimatedButton>
              </Link>
            </motion.div>
          )}
        </div>
      </div>
    </PageTransition>
  );
}
