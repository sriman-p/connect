'use client';

/**
 * Channel List Component
 * Displays list of channels
 */

import { useEffect, useState } from 'react';
import { Hash, Lock, Plus } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { getChannels } from '@/lib/api/messaging';
import type { Channel } from '@/lib/types/api';

interface ChannelListProps {
  selectedChannelId?: number;
  onSelectChannel: (channel: Channel) => void;
}

export function ChannelList({ selectedChannelId, onSelectChannel }: ChannelListProps) {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadChannels();
  }, []);

  const loadChannels = async () => {
    setIsLoading(true);
    try {
      const response = await getChannels();
      setChannels(response.results || []);
    } catch (error) {
      console.error('Failed to load channels:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getChannelIcon = (channel: Channel) => {
    switch (channel.channel_type) {
      case 'private':
        return <Lock className="h-4 w-4" />;
      case 'direct':
        return <div className="w-4 h-4 rounded-full bg-gradient-to-br from-blue-500 to-purple-600" />;
      default:
        return <Hash className="h-4 w-4" />;
    }
  };

  if (isLoading) {
    return (
      <div className="p-4">
        <div className="animate-pulse space-y-2">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-10 bg-gray-200 dark:bg-gray-800 rounded" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-800">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-900 dark:text-white">
            Channels
          </h2>
          <Button size="sm" variant="ghost">
            <Plus className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Channel list */}
      <div className="flex-1 overflow-y-auto p-2">
        {channels.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              No channels yet
            </p>
            <Button size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Create Channel
            </Button>
          </div>
        ) : (
          <div className="space-y-1">
            {channels.map((channel) => (
              <button
                key={channel.id}
                onClick={() => onSelectChannel(channel)}
                className={cn(
                  'w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-left',
                  selectedChannelId === channel.id
                    ? 'bg-blue-50 dark:bg-blue-950 text-blue-600 dark:text-blue-400'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                )}
              >
                <div className="flex-shrink-0">
                  {getChannelIcon(channel)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium truncate">
                      {channel.name}
                    </span>
                    {channel.unread_count && channel.unread_count > 0 && (
                      <span className="ml-2 px-2 py-0.5 text-xs font-bold text-white bg-red-500 rounded-full">
                        {channel.unread_count > 99 ? '99+' : channel.unread_count}
                      </span>
                    )}
                  </div>
                  {channel.last_message && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">
                      {channel.last_message.content}
                    </p>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
