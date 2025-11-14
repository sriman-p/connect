'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import apiClient from '@/lib/api/client';
import PageTransition from '@/components/animations/page-transition';
import AnimatedButton, { AnimatedIconButton } from '@/components/animations/animated-button';

interface Project {
  id: number;
  identifier: string;
  name: string;
  description: string;
  status: string;
  progress: number;
  lead: {
    id: number;
    email: string;
    full_name: string;
  };
  created_by: {
    id: number;
    email: string;
    full_name: string;
  };
  color: string;
  icon: string;
  issue_count: number;
  completed_issue_count: number;
  start_date: string | null;
  target_date: string | null;
  created_at: string;
  updated_at: string;
}

interface Issue {
  id: number;
  identifier: string;
  title: string;
  status: string;
  priority: string;
  assignee: {
    id: number;
    full_name: string;
  } | null;
}

export default function ProjectDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('overview');

  const { data: project, isLoading } = useQuery<Project>({
    queryKey: ['project', params.id],
    queryFn: async () => {
      const response = await apiClient.get(`/projects/${params.id}/`);
      return response.data;
    },
  });

  const { data: issues } = useQuery<Issue[]>({
    queryKey: ['project-issues', params.id],
    queryFn: async () => {
      const response = await apiClient.get(`/issues/?project=${params.id}`);
      return response.data.results || response.data;
    },
    enabled: activeTab === 'issues',
  });

  if (isLoading || !project) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'planned':
        return 'bg-gray-100 text-gray-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'on_hold':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <PageTransition>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-8 py-6">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4">
                <AnimatedIconButton onClick={() => router.push('/projects')}>
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                  </svg>
                </AnimatedIconButton>

                <div
                  className="w-16 h-16 rounded-lg flex items-center justify-center text-3xl"
                  style={{ backgroundColor: project.color + '20', color: project.color }}
                >
                  {project.icon || '📁'}
                </div>

                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(project.status)}`}>
                      {project.status.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                  <p className="text-gray-600 mb-2">{project.identifier}</p>
                  <p className="text-gray-700 max-w-2xl">{project.description}</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <AnimatedButton variant="ghost" size="sm">
                  Settings
                </AnimatedButton>
                <Link href={`/issues/new?project=${project.id}`}>
                  <AnimatedButton variant="primary" size="sm">
                    + New Issue
                  </AnimatedButton>
                </Link>
              </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-6 mt-6">
              {['overview', 'issues', 'activity'].map((tab) => (
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
          {activeTab === 'overview' && (
            <div className="grid grid-cols-3 gap-6">
              {/* Main Content */}
              <div className="col-span-2 space-y-6">
                {/* Progress */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-white rounded-lg border border-gray-200 p-6"
                >
                  <h2 className="text-lg font-semibold mb-4">Progress</h2>
                  <div className="mb-4">
                    <div className="flex items-center justify-between text-sm mb-2">
                      <span className="text-gray-600">
                        {project.completed_issue_count} of {project.issue_count} issues completed
                      </span>
                      <span className="font-medium">{Math.round(project.progress)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className="bg-blue-600 h-3 rounded-full transition-all"
                        style={{ width: `${project.progress}%` }}
                      />
                    </div>
                  </div>
                </motion.div>

                {/* Timeline */}
                {(project.start_date || project.target_date) && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-white rounded-lg border border-gray-200 p-6"
                  >
                    <h2 className="text-lg font-semibold mb-4">Timeline</h2>
                    <div className="space-y-3">
                      {project.start_date && (
                        <div className="flex items-center gap-3">
                          <span className="text-gray-600 w-24">Start Date:</span>
                          <span className="font-medium">
                            {new Date(project.start_date).toLocaleDateString()}
                          </span>
                        </div>
                      )}
                      {project.target_date && (
                        <div className="flex items-center gap-3">
                          <span className="text-gray-600 w-24">Target Date:</span>
                          <span className="font-medium">
                            {new Date(project.target_date).toLocaleDateString()}
                          </span>
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </div>

              {/* Sidebar */}
              <div className="space-y-6">
                {/* Team */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="bg-white rounded-lg border border-gray-200 p-6"
                >
                  <h3 className="font-semibold mb-4">Team</h3>
                  <div className="space-y-3">
                    <div>
                      <div className="text-xs text-gray-500 mb-1">Project Lead</div>
                      <div className="text-sm font-medium">{project.lead.full_name}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 mb-1">Created By</div>
                      <div className="text-sm font-medium">{project.created_by.full_name}</div>
                    </div>
                  </div>
                </motion.div>

                {/* Details */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="bg-white rounded-lg border border-gray-200 p-6"
                >
                  <h3 className="font-semibold mb-4">Details</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Created</span>
                      <span>{new Date(project.created_at).toLocaleDateString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Updated</span>
                      <span>{new Date(project.updated_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </motion.div>
              </div>
            </div>
          )}

          {activeTab === 'issues' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-white rounded-lg border border-gray-200"
            >
              {issues && issues.length > 0 ? (
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Issue</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Priority</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Assignee</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {issues.map((issue) => (
                      <tr
                        key={issue.id}
                        className="hover:bg-gray-50 cursor-pointer"
                        onClick={() => router.push(`/issues/${issue.id}`)}
                      >
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium text-gray-900">{issue.identifier}</span>
                            <span className="text-sm text-gray-600">{issue.title}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-sm text-gray-600">{issue.status}</span>
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-sm text-gray-600">{issue.priority}</span>
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-sm text-gray-600">
                            {issue.assignee?.full_name || 'Unassigned'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="p-12 text-center text-gray-500">
                  No issues in this project yet
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
