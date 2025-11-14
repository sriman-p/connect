'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import apiClient from '@/lib/api/client';
import PageTransition from '@/components/animations/page-transition';
import AnimatedButton, { AnimatedIconButton } from '@/components/animations/animated-button';

interface Meeting {
  id: number;
  title: string;
  description: string;
  meeting_type: string;
  status: string;
  start_time: string;
  end_time: string;
  timezone: string;
  organizer: {
    id: number;
    full_name: string;
  };
  participant_count: number;
  duration_minutes: number;
  meeting_url: string;
  meeting_password: string;
  is_recorded: boolean;
  recording_url: string;
  created_at: string;
}

interface Participant {
  id: number;
  user: {
    full_name: string;
  };
  role: string;
  status: string;
  joined_at: string | null;
}

interface Note {
  id: number;
  title: string;
  content: string;
  created_by: {
    full_name: string;
  };
  is_shared: boolean;
  created_at: string;
}

export default function MeetingDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('overview');

  const { data: meeting, isLoading } = useQuery<Meeting>({
    queryKey: ['meeting', params.id],
    queryFn: async () => {
      const response = await apiClient.get(`/meetings/${params.id}/`);
      return response.data;
    },
  });

  const { data: participants } = useQuery<Participant[]>({
    queryKey: ['meeting-participants', params.id],
    queryFn: async () => {
      const response = await apiClient.get(`/meetings/${params.id}/participants/`);
      return response.data;
    },
    enabled: activeTab === 'participants',
  });

  const { data: notes } = useQuery<Note[]>({
    queryKey: ['meeting-notes', params.id],
    queryFn: async () => {
      const response = await apiClient.get(`/meeting-notes/?meeting=${params.id}`);
      return response.data.results || response.data;
    },
    enabled: activeTab === 'notes',
  });

  if (isLoading || !meeting) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled':
        return 'bg-blue-100 text-blue-800';
      case 'in_progress':
        return 'bg-green-100 text-green-800';
      case 'completed':
        return 'bg-gray-100 text-gray-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return {
      date: date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
      time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    };
  };

  const startTime = formatDateTime(meeting.start_time);
  const endTime = formatDateTime(meeting.end_time);
  const isUpcoming = new Date(meeting.start_time) > new Date();

  return (
    <PageTransition>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-8 py-6">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4 flex-1">
                <AnimatedIconButton onClick={() => router.push('/meetings')}>
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                  </svg>
                </AnimatedIconButton>

                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <h1 className="text-3xl font-bold text-gray-900">{meeting.title}</h1>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(meeting.status)}`}>
                      {meeting.status.replace('_', ' ').toUpperCase()}
                    </span>
                    {meeting.is_recorded && (
                      <span className="px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
                        🔴 Recording
                      </span>
                    )}
                  </div>
                  <p className="text-gray-700 mb-3">{meeting.description}</p>
                  <div className="flex items-center gap-6 text-sm text-gray-600">
                    <div className="flex items-center gap-2">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <span>{startTime.date}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>{startTime.time} - {endTime.time} ({meeting.duration_minutes} min)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                      <span>{meeting.participant_count} participants</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {isUpcoming && meeting.meeting_url && (
                  <AnimatedButton
                    variant="primary"
                    size="lg"
                    onClick={() => window.open(meeting.meeting_url, '_blank')}
                  >
                    Join Meeting
                  </AnimatedButton>
                )}
                <AnimatedButton variant="ghost" size="sm">
                  Edit
                </AnimatedButton>
              </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-6 mt-6">
              {['overview', 'participants', 'notes'].map((tab) => (
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
                {/* Meeting Details */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-white rounded-lg border border-gray-200 p-6"
                >
                  <h2 className="text-lg font-semibold mb-4">Meeting Details</h2>
                  <div className="space-y-3">
                    <div>
                      <div className="text-sm text-gray-600 mb-1">Meeting Type</div>
                      <div className="font-medium">{meeting.meeting_type.replace('_', ' ').toUpperCase()}</div>
                    </div>
                    {meeting.meeting_url && (
                      <div>
                        <div className="text-sm text-gray-600 mb-1">Meeting Link</div>
                        <a
                          href={meeting.meeting_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline font-medium"
                        >
                          {meeting.meeting_url}
                        </a>
                      </div>
                    )}
                    {meeting.meeting_password && (
                      <div>
                        <div className="text-sm text-gray-600 mb-1">Meeting Password</div>
                        <div className="font-mono">{meeting.meeting_password}</div>
                      </div>
                    )}
                    {meeting.recording_url && (
                      <div>
                        <div className="text-sm text-gray-600 mb-1">Recording</div>
                        <a
                          href={meeting.recording_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline font-medium"
                        >
                          View Recording
                        </a>
                      </div>
                    )}
                  </div>
                </motion.div>
              </div>

              {/* Sidebar */}
              <div className="space-y-6">
                {/* Organizer */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-white rounded-lg border border-gray-200 p-6"
                >
                  <h3 className="font-semibold mb-4">Organizer</h3>
                  <div className="font-medium">{meeting.organizer.full_name}</div>
                </motion.div>

                {/* Info */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="bg-white rounded-lg border border-gray-200 p-6"
                >
                  <h3 className="font-semibold mb-4">Information</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Timezone</span>
                      <span>{meeting.timezone}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Created</span>
                      <span>{new Date(meeting.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </motion.div>
              </div>
            </div>
          )}

          {activeTab === 'participants' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-white rounded-lg border border-gray-200"
            >
              {participants && participants.length > 0 ? (
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Joined At</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {participants.map((participant) => (
                      <tr key={participant.id}>
                        <td className="px-6 py-4 text-sm font-medium text-gray-900">
                          {participant.user.full_name}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">{participant.role}</td>
                        <td className="px-6 py-4 text-sm text-gray-600">{participant.status}</td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {participant.joined_at ? new Date(participant.joined_at).toLocaleString() : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="p-12 text-center text-gray-500">
                  No participants yet
                </div>
              )}
            </motion.div>
          )}

          {activeTab === 'notes' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-4"
            >
              {notes && notes.length > 0 ? (
                notes.map((note) => (
                  <div key={note.id} className="bg-white rounded-lg border border-gray-200 p-6">
                    <div className="flex items-start justify-between mb-3">
                      <h3 className="text-lg font-semibold">{note.title}</h3>
                      {note.is_shared && (
                        <span className="px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                          Shared
                        </span>
                      )}
                    </div>
                    <div className="prose max-w-none text-gray-700 mb-3">{note.content}</div>
                    <div className="text-xs text-gray-500">
                      By {note.created_by.full_name} • {new Date(note.created_at).toLocaleString()}
                    </div>
                  </div>
                ))
              ) : (
                <div className="bg-white rounded-lg border border-gray-200 p-12 text-center text-gray-500">
                  No notes yet
                </div>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </PageTransition>
  );
}
