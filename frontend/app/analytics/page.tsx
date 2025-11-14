'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js'
import { Line, Bar, Doughnut } from 'react-chartjs-2'

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

interface DashboardStats {
  total_users: number
  active_users_today: number
  total_projects: number
  total_issues: number
  issues_closed_today: number
  documents_created_today: number
  meetings_today: number
}

interface ActivityData {
  created_at__date: string
  count: number
}

interface FeatureUsage {
  event_name: string
  count: number
}

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('7d')

  // Fetch dashboard stats
  const { data: stats, isLoading: statsLoading } = useQuery<DashboardStats>({
    queryKey: ['analytics-stats'],
    queryFn: async () => {
      const res = await fetch('/api/analytics/dashboard/stats/')
      if (!res.ok) throw new Error('Failed to fetch stats')
      return res.json()
    },
  })

  // Fetch activity data
  const { data: activity, isLoading: activityLoading } = useQuery<ActivityData[]>({
    queryKey: ['analytics-activity', timeRange],
    queryFn: async () => {
      const res = await fetch('/api/analytics/dashboard/activity/')
      if (!res.ok) throw new Error('Failed to fetch activity')
      return res.json()
    },
  })

  // Fetch feature usage
  const { data: features, isLoading: featuresLoading } = useQuery<FeatureUsage[]>({
    queryKey: ['analytics-features'],
    queryFn: async () => {
      const res = await fetch('/api/analytics/dashboard/features/')
      if (!res.ok) throw new Error('Failed to fetch features')
      return res.json()
    },
  })

  // Prepare activity chart data
  const activityChartData = {
    labels: activity?.map(a => new Date(a.created_at__date).toLocaleDateString()) || [],
    datasets: [
      {
        label: 'User Activity',
        data: activity?.map(a => a.count) || [],
        borderColor: 'rgb(99, 102, 241)',
        backgroundColor: 'rgba(99, 102, 241, 0.1)',
        tension: 0.4,
      },
    ],
  }

  // Prepare feature usage chart data
  const featureChartData = {
    labels: features?.map(f => f.event_name) || [],
    datasets: [
      {
        label: 'Usage Count',
        data: features?.map(f => f.count) || [],
        backgroundColor: [
          'rgba(99, 102, 241, 0.8)',
          'rgba(139, 92, 246, 0.8)',
          'rgba(168, 85, 247, 0.8)',
          'rgba(192, 132, 252, 0.8)',
          'rgba(216, 180, 254, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(34, 211, 238, 0.8)',
          'rgba(20, 184, 166, 0.8)',
          'rgba(34, 197, 94, 0.8)',
          'rgba(132, 204, 22, 0.8)',
        ],
      },
    ],
  }

  const statCards = [
    {
      title: 'Total Users',
      value: stats?.total_users || 0,
      change: '+12%',
      trend: 'up' as const,
      icon: '👥',
    },
    {
      title: 'Active Today',
      value: stats?.active_users_today || 0,
      change: '+8%',
      trend: 'up' as const,
      icon: '🟢',
    },
    {
      title: 'Total Projects',
      value: stats?.total_projects || 0,
      change: '+5%',
      trend: 'up' as const,
      icon: '📁',
    },
    {
      title: 'Total Issues',
      value: stats?.total_issues || 0,
      change: '+15%',
      trend: 'up' as const,
      icon: '🎯',
    },
    {
      title: 'Issues Closed Today',
      value: stats?.issues_closed_today || 0,
      change: '+10%',
      trend: 'up' as const,
      icon: '✅',
    },
    {
      title: 'Documents Created',
      value: stats?.documents_created_today || 0,
      change: '+7%',
      trend: 'up' as const,
      icon: '📄',
    },
    {
      title: 'Meetings Today',
      value: stats?.meetings_today || 0,
      change: '+3%',
      trend: 'up' as const,
      icon: '📹',
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Analytics Dashboard</h1>
          <p className="text-gray-600">Track your workspace activity and usage metrics</p>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {statCards.map((stat, index) => (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="text-3xl">{stat.icon}</div>
                <span
                  className={`text-sm font-medium ${
                    stat.trend === 'up' ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {stat.change}
                </span>
              </div>
              <h3 className="text-gray-600 text-sm font-medium mb-1">{stat.title}</h3>
              <p className="text-3xl font-bold text-gray-900">
                {statsLoading ? (
                  <span className="animate-pulse">...</span>
                ) : (
                  stat.value.toLocaleString()
                )}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Activity Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-lg shadow-md p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">User Activity</h2>
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value as '7d' | '30d' | '90d')}
                className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last 90 days</option>
              </select>
            </div>
            {activityLoading ? (
              <div className="h-64 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              </div>
            ) : (
              <div className="h-64">
                <Line
                  data={activityChartData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        display: false,
                      },
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                      },
                    },
                  }}
                />
              </div>
            )}
          </motion.div>

          {/* Feature Usage Chart */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white rounded-lg shadow-md p-6"
          >
            <h2 className="text-xl font-bold text-gray-900 mb-6">Top Features</h2>
            {featuresLoading ? (
              <div className="h-64 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              </div>
            ) : (
              <div className="h-64">
                <Bar
                  data={featureChartData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    plugins: {
                      legend: {
                        display: false,
                      },
                    },
                    scales: {
                      x: {
                        beginAtZero: true,
                      },
                    },
                  }}
                />
              </div>
            )}
          </motion.div>
        </div>

        {/* Feature Usage Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white rounded-lg shadow-md p-6"
        >
          <h2 className="text-xl font-bold text-gray-900 mb-6">Feature Usage Details</h2>
          {featuresLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Feature
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Usage Count
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Percentage
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {features?.map((feature, index) => {
                    const total = features.reduce((sum, f) => sum + f.count, 0)
                    const percentage = ((feature.count / total) * 100).toFixed(1)
                    return (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {feature.event_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {feature.count.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <div className="flex items-center">
                            <div className="w-32 bg-gray-200 rounded-full h-2 mr-2">
                              <div
                                className="bg-indigo-600 h-2 rounded-full"
                                style={{ width: `${percentage}%` }}
                              ></div>
                            </div>
                            <span>{percentage}%</span>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}
