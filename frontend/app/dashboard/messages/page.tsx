/**
 * Messages Page
 * Real-time messaging interface
 */

'use client';

import { useState } from 'react';
import { Hash } from 'lucide-react';
import { ChannelList } from '@/components/messaging/channel-list';
import { MessageFeed } from '@/components/messaging/message-feed';
import { MessageInput } from '@/components/messaging/message-input';
import type { Channel } from '@/lib/types/api';

export default function MessagesPage() {
  const [selectedChannel, setSelectedChannel] = useState<Channel | null>(null);

  return (
    <div className="h-full flex">
      {/* Channel sidebar */}
      <div className="w-64 border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
        <ChannelList
          selectedChannelId={selectedChannel?.id}
          onSelectChannel={setSelectedChannel}
        />
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col">
        {selectedChannel ? (
          <>
            {/* Channel header */}
            <div className="flex-shrink-0 h-16 px-6 flex items-center border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
              <Hash className="h-5 w-5 text-gray-500 dark:text-gray-400 mr-2" />
              <div>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {selectedChannel.name}
                </h2>
                {selectedChannel.description && (
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {selectedChannel.description}
                  </p>
                )}
              </div>
            </div>

            {/* Message feed */}
            <div className="flex-1 overflow-hidden">
              <MessageFeed channel={selectedChannel} />
            </div>

            {/* Message input */}
            <div className="flex-shrink-0">
              <MessageInput channel={selectedChannel} />
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <Hash className="h-16 w-16 text-gray-300 dark:text-gray-700 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                No channel selected
              </h3>
              <p className="text-gray-500 dark:text-gray-400">
                Select a channel from the sidebar to start messaging
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
