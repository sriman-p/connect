'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import apiClient from '@/lib/api/client';
import PageTransition from '@/components/animations/page-transition';
import AnimatedButton, { AnimatedIconButton } from '@/components/animations/animated-button';

interface Issue {
  id: number;
  identifier: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  issue_type: string;
  assignee: {
    id: number;
    email: string;
    full_name: string;
  } | null;
  reporter: {
    id: number;
    email: string;
    full_name: string;
  };
  project: {
    id: number;
    name: string;
    identifier: string;
  };
  labels: Array<{
    id: number;
    name: string;
    color: string;
  }>;
  parent: number | null;
  estimate: number | null;
  due_date: string | null;
  created_at: string;
  updated_at: string;
}

interface Comment {
  id: number;
  author: {
    full_name: string;
  };
  content: string;
  created_at: string;
}

export default function IssueDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('details');

  const { data: issue, isLoading } = useQuery<Issue>({
    queryKey: ['issue', params.id],
    queryFn: async () => {
      const response = await apiClient.get(`/issues/${params.id}/`);
      return response.data;
    },
  });

  const { data: comments } = useQuery<Comment[]>({
    queryKey: ['issue-comments', params.id],
    queryFn: async () => {
      const response = await apiClient.get(`/issues/${params.id}/comments/`);
      return response.data.results || response.data;
    },
    enabled: activeTab === 'comments',
  });

  if (isLoading || !issue) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'todo':
        return 'bg-gray-100 text-gray-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'in_review':
        return 'bg-purple-100 text-purple-800';
      case 'done':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return '🔴';
      case 'high':
        return '🟠';
      case 'medium':
        return '🟡';
      case 'low':
        return '⚪';
      default:
        return '⚪';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'bug':
        return '🐛';
      case 'feature':
        return '✨';
      case 'improvement':
        return '📈';
      case 'task':
        return '✅';
      default:
        return '📝';
    }
  };

  return (
    <PageTransition>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-8 py-6">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4 flex-1">
                <AnimatedIconButton onClick={() => router.push('/issues')}>
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                  </svg>
                </AnimatedIconButton>

                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-2xl">{getTypeIcon(issue.issue_type)}</span>
                    <span className="text-sm font-medium text-gray-600">{issue.identifier}</span>
                    <span className="text-sm font-medium text-gray-400">•</span>
                    <span className="text-sm text-gray-600">{issue.project.identifier}</span>
                  </div>
                  <h1 className="text-3xl font-bold text-gray-900 mb-3">{issue.title}</h1>
                  <div className="flex items-center gap-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(issue.status)}`}>
                      {issue.status.replace('_', ' ').toUpperCase()}
                    </span>
                    <div className="flex items-center gap-2">
                      <span>{getPriorityIcon(issue.priority)}</span>
                      <span className="text-sm font-medium text-gray-700">
                        {issue.priority.charAt(0).toUpperCase() + issue.priority.slice(1)} Priority
                      </span>
                    </div>
                    {issue.labels.map((label) => (
                      <span
                        key={label.id}
                        className="px-2 py-1 rounded text-xs font-medium"
                        style={{ backgroundColor: label.color + '20', color: label.color }}
                      >
                        {label.name}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <AnimatedButton variant="ghost" size="sm">
                  Edit
                </AnimatedButton>
                <AnimatedButton variant="ghost" size="sm">
                  Close
                </AnimatedButton>
              </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-6 mt-6">
              {['details', 'comments', 'activity'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`pb-3 border-b-2 transition-colors ${
                    activeTab === tab
                      ? 'border-blue-600 text-blue-600 font-medium'
                      : 'border-transparent text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="max-w-7xl mx-auto px-8 py-8">
          {activeTab === 'details' && (
            <div className="grid grid-cols-3 gap-6">
              {/* Main Content */}
              <div className="col-span-2 space-y-6">
                {/* Description */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-white rounded-lg border border-gray-200 p-6"
                >
                  <h2 className="text-lg font-semibold mb-4">Description</h2>
                  <div className="prose max-w-none text-gray-700">
                    {issue.description || 'No description provided.'}
                  </div>
                </motion.div>
              </div>

              {/* Sidebar */}
              <div className="space-y-6">
                {/* Details */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-white rounded-lg border border-gray-200 p-6"
                >
                  <h3 className="font-semibold mb-4">Details</h3>
                  <div className="space-y-3">
                    <div>
                      <div className="text-xs text-gray-500 mb-1">Assignee</div>
                      <div className="text-sm font-medium">
                        {issue.assignee?.full_name || 'Unassigned'}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 mb-1">Reporter</div>
                      <div className="text-sm font-medium">{issue.reporter.full_name}</div>
                    </div>
                    {issue.estimate && (
                      <div>
                        <div className="text-xs text-gray-500 mb-1">Estimate</div>
                        <div className="text-sm font-medium">{issue.estimate}h</div>
                      </div>
                    )}
                    {issue.due_date && (
                      <div>
                        <div className="text-xs text-gray-500 mb-1">Due Date</div>
                        <div className="text-sm font-medium">
                          {new Date(issue.due_date).toLocaleDateString()}
                        </div>
                      </div>
                    )}
                  </div>
                </motion.div>

                {/* Timestamps */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="bg-white rounded-lg border border-gray-200 p-6"
                >
                  <h3 className="font-semibold mb-4">Timestamps</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Created</span>
                      <span>{new Date(issue.created_at).toLocaleDateString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Updated</span>
                      <span>{new Date(issue.updated_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </motion.div>
              </div>
            </div>
          )}

          {activeTab === 'comments' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-white rounded-lg border border-gray-200 p-6"
            >
              {comments && comments.length > 0 ? (
                <div className="space-y-4">
                  {comments.map((comment) => (
                    <div key={comment.id} className="border-b border-gray-200 pb-4 last:border-0">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-bold">
                          {comment.author.full_name.charAt(0)}
                        </div>
                        <div>
                          <div className="font-medium text-sm">{comment.author.full_name}</div>
                          <div className="text-xs text-gray-500">
                            {new Date(comment.created_at).toLocaleString()}
                          </div>
                        </div>
                      </div>
                      <div className="ml-11 text-gray-700">{comment.content}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-gray-500 py-8">
                  No comments yet
                </div>
              )}
            </motion.div>
          )}

          {activeTab === 'activity' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-white rounded-lg border border-gray-200 p-12 text-center"
            >
              <div className="text-gray-500">Activity feed coming soon...</div>
            </motion.div>
          )}
        </div>
      </div>
    </PageTransition>
  );
}
