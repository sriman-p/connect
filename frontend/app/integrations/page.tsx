'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'

interface Integration {
  id: number
  name: string
  integration_type: string
  is_active: boolean
  sync_status: string
  last_synced_at: string | null
  installed_at: string
}

const INTEGRATION_TYPES = [
  { value: 'github', label: 'GitHub', icon: '🔧', description: 'Connect to GitHub repositories' },
  { value: 'gitlab', label: 'GitLab', icon: '🦊', description: 'Connect to GitLab projects' },
  { value: 'jira', label: 'Jira', icon: '📋', description: 'Sync with Jira issues' },
  { value: 'slack', label: 'Slack', icon: '💬', description: 'Send notifications to Slack' },
  { value: 'teams', label: 'Microsoft Teams', icon: '👥', description: 'Integrate with Teams' },
  { value: 'google', label: 'Google Workspace', icon: '📧', description: 'Connect Google services' },
  { value: 'zoom', label: 'Zoom', icon: '📹', description: 'Schedule Zoom meetings' },
]

export default function IntegrationsPage() {
  const [showAddDialog, setShowAddDialog] = useState(false)
  const [selectedType, setSelectedType] = useState('')
  const queryClient = useQueryClient()

  // Fetch integrations
  const { data: integrations, isLoading } = useQuery<Integration[]>({
    queryKey: ['integrations'],
    queryFn: async () => {
      const res = await fetch('/api/integrations/integrations/')
      if (!res.ok) throw new Error('Failed to fetch integrations')
      return res.json()
    },
  })

  // Delete integration mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      const res = await fetch(`/api/integrations/integrations/${id}/`, {
        method: 'DELETE',
      })
      if (!res.ok) throw new Error('Failed to delete integration')
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] })
    },
  })

  // Sync integration mutation
  const syncMutation = useMutation({
    mutationFn: async (id: number) => {
      const res = await fetch(`/api/integrations/integrations/${id}/sync/`, {
        method: 'POST',
      })
      if (!res.ok) throw new Error('Failed to sync integration')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] })
    },
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'text-green-600 bg-green-100'
      case 'syncing':
        return 'text-blue-600 bg-blue-100'
      case 'failed':
        return 'text-red-600 bg-red-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">Integrations</h1>
              <p className="text-gray-600">Connect external services to your workspace</p>
            </div>
            <button
              onClick={() => setShowAddDialog(true)}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              + Add Integration
            </button>
          </div>
        </motion.div>

        {/* Available Integrations */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-lg shadow-md p-6 mb-8"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Available Integrations</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {INTEGRATION_TYPES.map((type) => (
              <div
                key={type.value}
                className="border border-gray-200 rounded-lg p-4 hover:border-indigo-500 hover:shadow-md transition-all cursor-pointer"
                onClick={() => {
                  setSelectedType(type.value)
                  setShowAddDialog(true)
                }}
              >
                <div className="text-3xl mb-2">{type.icon}</div>
                <h3 className="font-semibold text-gray-900 mb-1">{type.label}</h3>
                <p className="text-sm text-gray-600">{type.description}</p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Active Integrations */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-lg shadow-md p-6"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Active Integrations</h2>

          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
          ) : integrations && integrations.length > 0 ? (
            <div className="space-y-4">
              {integrations.map((integration) => (
                <div
                  key={integration.id}
                  className="border border-gray-200 rounded-lg p-4 flex items-center justify-between"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-gray-900">{integration.name}</h3>
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${getStatusColor(
                          integration.sync_status
                        )}`}
                      >
                        {integration.sync_status}
                      </span>
                      {!integration.is_active && (
                        <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-600">
                          Inactive
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600">
                      Type: {integration.integration_type} • Installed:{' '}
                      {new Date(integration.installed_at).toLocaleDateString()}
                      {integration.last_synced_at && (
                        <> • Last synced: {new Date(integration.last_synced_at).toLocaleString()}</>
                      )}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => syncMutation.mutate(integration.id)}
                      disabled={syncMutation.isPending}
                      className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
                    >
                      {syncMutation.isPending ? 'Syncing...' : 'Sync'}
                    </button>
                    <button
                      onClick={() => {
                        if (confirm('Are you sure you want to delete this integration?')) {
                          deleteMutation.mutate(integration.id)
                        }
                      }}
                      className="px-4 py-2 bg-red-600 text-white text-sm rounded-md hover:bg-red-700 transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-600 mb-4">No integrations configured yet</p>
              <button
                onClick={() => setShowAddDialog(true)}
                className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Add Your First Integration
              </button>
            </div>
          )}
        </motion.div>

        {/* Add Integration Dialog (Simplified) */}
        {showAddDialog && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white rounded-lg p-6 max-w-md w-full mx-4"
            >
              <h3 className="text-xl font-bold text-gray-900 mb-4">Add Integration</h3>
              <p className="text-gray-600 mb-6">
                Integration configuration requires API keys and credentials. Please configure
                integrations through the backend admin interface.
              </p>
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => {
                    setShowAddDialog(false)
                    setSelectedType('')
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                >
                  Close
                </button>
                <a
                  href="/admin/integrations/integration/add/"
                  target="_blank"
                  className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
                >
                  Go to Admin
                </a>
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  )
}
