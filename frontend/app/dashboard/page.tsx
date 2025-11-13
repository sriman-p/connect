/**
 * Dashboard Home Page
 * Main dashboard overview
 */

import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Dashboard | Connect',
  description: 'Your Connect dashboard',
};

export default function DashboardPage() {
  return (
    <div className="p-6 md:p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Welcome back! Here's what's happening with your projects.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Active Projects"
          value="12"
          change="+2 this week"
          changeType="positive"
        />
        <StatCard
          title="Open Issues"
          value="48"
          change="-5 from yesterday"
          changeType="positive"
        />
        <StatCard
          title="Team Members"
          value="24"
          change="+3 this month"
          changeType="positive"
        />
        <StatCard
          title="Completion Rate"
          value="87%"
          change="+12% this month"
          changeType="positive"
        />
      </div>

      {/* Recent Activity */}
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Recent Activity
        </h2>
        <div className="space-y-4">
          <ActivityItem
            user="Sarah Johnson"
            action="completed issue"
            target="AUTH-234: Fix login redirect"
            time="2 minutes ago"
          />
          <ActivityItem
            user="Mike Chen"
            action="commented on"
            target="PROJ-123: Update user profile UI"
            time="15 minutes ago"
          />
          <ActivityItem
            user="Emily Rodriguez"
            action="created project"
            target="Mobile App Redesign"
            time="1 hour ago"
          />
          <ActivityItem
            user="Alex Thompson"
            action="assigned you to"
            target="API-456: Implement webhooks"
            time="2 hours ago"
          />
        </div>
      </div>
    </div>
  );
}

interface StatCardProps {
  title: string;
  value: string;
  change: string;
  changeType: 'positive' | 'negative';
}

function StatCard({ title, value, change, changeType }: StatCardProps) {
  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
      <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
        {title}
      </p>
      <p className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
        {value}
      </p>
      <p
        className={`text-sm ${
          changeType === 'positive'
            ? 'text-green-600 dark:text-green-400'
            : 'text-red-600 dark:text-red-400'
        }`}
      >
        {change}
      </p>
    </div>
  );
}

interface ActivityItemProps {
  user: string;
  action: string;
  target: string;
  time: string;
}

function ActivityItem({ user, action, target, time }: ActivityItemProps) {
  return (
    <div className="flex items-start space-x-3 pb-4 border-b border-gray-100 dark:border-gray-800 last:border-0 last:pb-0">
      <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex-shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-900 dark:text-white">
          <span className="font-medium">{user}</span>{' '}
          <span className="text-gray-600 dark:text-gray-400">{action}</span>{' '}
          <span className="font-medium">{target}</span>
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{time}</p>
      </div>
    </div>
  );
}
