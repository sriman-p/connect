'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import Link from 'next/link';
import apiClient from '@/lib/api/client';
import PageTransition, { StaggerContainer, StaggerItem } from '@/components/animations/page-transition';
import AnimatedButton from '@/components/animations/animated-button';

interface Meeting {
  id: number;
  title: string;
  description: string;
  meeting_type: string;
  status: string;
  start_time: string;
  end_time: string;
  organizer: {
    id: number;
    email: string;
    full_name: string;
  };
  participant_count: number;
  is_recorded: boolean;
  meeting_url: string;
  created_at: string;
}

export default function MeetingsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const { data: meetings, isLoading } = useQuery<Meeting[]>({
    queryKey: ['meetings'],
    queryFn: async () => {
      const response = await apiClient.get('/meetings/');
      return response.data.results || response.data;
    },
  });

  const filteredMeetings = meetings?.filter((meeting) => {
    const matchesSearch = meeting.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = filterStatus === 'all' || meeting.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

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
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      day: date.toLocaleDateString('en-US', { weekday: 'short' }),
    };
  };

  const getDuration = (start: string, end: string) => {
    const startDate = new Date(start);
    const endDate = new Date(end);
    const minutes = Math.floor((endDate.getTime() - startDate.getTime()) / (1000 * 60));
    if (minutes < 60) {
      return `${minutes}m`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMins = minutes % 60;
    return `${hours}h ${remainingMins}m`;
  };

  const isUpcoming = (startTime: string) => {
    return new Date(startTime) > new Date();
  };

  const formatStatus = (status: string) => {
    return status.split('_').map(word =>
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
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
                <h1 className="text-3xl font-bold text-gray-900">Meetings</h1>
                <p className="text-gray-600 mt-1">
                  {filteredMeetings?.length || 0} meeting{filteredMeetings?.length !== 1 ? 's' : ''}
                </p>
              </div>
              <Link href="/meetings/new">
                <AnimatedButton variant="primary" size="lg">
                  + Schedule Meeting
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
                  placeholder="Search meetings..."
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
                <option value="scheduled">Scheduled</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
          </motion.div>

          {/* Meetings List */}
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
            </div>
          ) : filteredMeetings && filteredMeetings.length > 0 ? (
            <StaggerContainer>
              <div className="space-y-4">
                {filteredMeetings.map((meeting) => {
                  const datetime = formatDateTime(meeting.start_time);
                  const upcoming = isUpcoming(meeting.start_time);

                  return (
                    <StaggerItem key={meeting.id}>
                      <Link href={`/meetings/${meeting.id}`}>
                        <motion.div
                          whileHover={{ scale: 1.01, boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)' }}
                          className="bg-white rounded-lg border border-gray-200 p-6 cursor-pointer transition-all"
                        >
                          <div className="flex items-start gap-6">
                            {/* Date Badge */}
                            <div className="flex-shrink-0 text-center">
                              <div className="w-16 h-16 rounded-lg bg-blue-50 border-2 border-blue-200 flex flex-col items-center justify-center">
                                <div className="text-xs text-blue-600 font-medium">{datetime.day}</div>
                                <div className="text-lg font-bold text-blue-900">{datetime.date.split(' ')[1]}</div>
                                <div className="text-xs text-blue-600">{datetime.date.split(' ')[0]}</div>
                              </div>
                            </div>

                            {/* Meeting Details */}
                            <div className="flex-1 min-w-0">
                              <div className="flex items-start justify-between mb-2">
                                <div>
                                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                                    {meeting.title}
                                  </h3>
                                  <p className="text-sm text-gray-600 line-clamp-2">
                                    {meeting.description}
                                  </p>
                                </div>
                                <span className={`px-3 py-1 rounded-full text-xs font-medium ml-4 whitespace-nowrap ${getStatusColor(meeting.status)}`}>
                                  {formatStatus(meeting.status)}
                                </span>
                              </div>

                              <div className="flex items-center gap-6 text-sm text-gray-600 mt-3">
                                <div className="flex items-center gap-2">
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                  </svg>
                                  <span>{datetime.time} • {getDuration(meeting.start_time, meeting.end_time)}</span>
                                </div>

                                <div className="flex items-center gap-2">
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                  </svg>
                                  <span>{meeting.organizer.full_name}</span>
                                </div>

                                <div className="flex items-center gap-2">
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                                  </svg>
                                  <span>{meeting.participant_count} participants</span>
                                </div>

                                {meeting.is_recorded && (
                                  <div className="flex items-center gap-2 text-red-600">
                                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                                      <circle cx="12" cy="12" r="8" />
                                    </svg>
                                    <span>Recording</span>
                                  </div>
                                )}
                              </div>

                              {upcoming && meeting.meeting_url && (
                                <div className="mt-4">
                                  <AnimatedButton
                                    variant="primary"
                                    size="sm"
                                    onClick={(e) => {
                                      e.preventDefault();
                                      window.open(meeting.meeting_url, '_blank');
                                    }}
                                  >
                                    Join Meeting
                                  </AnimatedButton>
                                </div>
                              )}
                            </div>
                          </div>
                        </motion.div>
                      </Link>
                    </StaggerItem>
                  );
                })}
              </div>
            </StaggerContainer>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-white rounded-lg border border-gray-200 p-12 text-center"
            >
              <div className="text-6xl mb-4">📅</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No meetings found
              </h3>
              <p className="text-gray-600 mb-6">
                {searchQuery
                  ? 'Try adjusting your search or filters'
                  : 'Get started by scheduling your first meeting'}
              </p>
              <Link href="/meetings/new">
                <AnimatedButton variant="primary">
                  Schedule Meeting
                </AnimatedButton>
              </Link>
            </motion.div>
          )}
        </div>
      </div>
    </PageTransition>
  );
}
