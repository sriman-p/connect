'use client';

/**
 * Message Feed Component
 * Displays messages in a chat feed
 */

import { useEffect, useRef, useState } from 'react';
import { format, isToday, isYesterday } from 'date-fns';
import { Loader2, Smile } from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { getMessages } from '@/lib/api/messaging';
import { useWebSocket } from '@/lib/hooks/use-websocket';
import type { Message, Channel } from '@/lib/types/api';
import { cn } from '@/lib/utils';

interface MessageFeedProps {
  channel: Channel;
}

export function MessageFeed({ channel }: MessageFeedProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [typingUsers, setTypingUsers] = useState<Set<string>>(new Set());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // WebSocket connection
  const { isConnected } = useWebSocket({
    channelId: channel.id,
    onMessage: (newMessage) => {
      setMessages((prev) => [...prev, newMessage]);
      scrollToBottom();
    },
    onTyping: ({ user_name, is_typing }) => {
      setTypingUsers((prev) => {
        const newSet = new Set(prev);
        if (is_typing) {
          newSet.add(user_name);
        } else {
          newSet.delete(user_name);
        }
        return newSet;
      });
    },
  });

  useEffect(() => {
    loadMessages();
  }, [channel.id]);

  const loadMessages = async () => {
    setIsLoading(true);
    try {
      const response = await getMessages(channel.id, { limit: 50 });
      setMessages(response.results || []);
      setTimeout(scrollToBottom, 100);
    } catch (error) {
      console.error('Failed to load messages:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatMessageTime = (timestamp: string) => {
    const date = new Date(timestamp);

    if (isToday(date)) {
      return format(date, 'h:mm a');
    } else if (isYesterday(date)) {
      return `Yesterday at ${format(date, 'h:mm a')}`;
    } else {
      return format(date, 'MMM d, h:mm a');
    }
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Connection status */}
      {!isConnected && (
        <div className="px-4 py-2 bg-yellow-50 dark:bg-yellow-950 border-b border-yellow-200 dark:border-yellow-800">
          <p className="text-sm text-yellow-800 dark:text-yellow-200">
            Reconnecting...
          </p>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-500 dark:text-gray-400">
              No messages yet. Start the conversation!
            </p>
          </div>
        ) : (
          <>
            {messages.map((message, index) => {
              const showAvatar =
                index === 0 ||
                messages[index - 1].author !== message.author ||
                new Date(message.created_at).getTime() -
                  new Date(messages[index - 1].created_at).getTime() >
                  300000; // 5 minutes

              return (
                <div
                  key={message.id}
                  className={cn('flex gap-3', !showAvatar && 'ml-11')}
                >
                  {showAvatar && (
                    <Avatar className="h-8 w-8 flex-shrink-0">
                      <AvatarImage
                        src={message.author_data?.avatar_url}
                        alt={message.author_data?.full_name}
                      />
                      <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white text-xs">
                        {message.author_data
                          ? getInitials(message.author_data.full_name)
                          : 'U'}
                      </AvatarFallback>
                    </Avatar>
                  )}

                  <div className="flex-1 min-w-0">
                    {showAvatar && (
                      <div className="flex items-baseline gap-2 mb-1">
                        <span className="text-sm font-semibold text-gray-900 dark:text-white">
                          {message.author_data?.full_name || 'Unknown User'}
                        </span>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {formatMessageTime(message.created_at)}
                        </span>
                      </div>
                    )}

                    <div className="text-sm text-gray-900 dark:text-gray-100">
                      {message.is_deleted ? (
                        <span className="italic text-gray-500">
                          Message deleted
                        </span>
                      ) : (
                        <p className="whitespace-pre-wrap break-words">
                          {message.content}
                        </p>
                      )}
                    </div>

                    {/* Reactions */}
                    {message.reaction_summary &&
                      message.reaction_summary.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {message.reaction_summary.map((reaction) => (
                            <button
                              key={reaction.emoji}
                              className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-colors"
                            >
                              <span>{reaction.emoji}</span>
                              <span className="text-gray-600 dark:text-gray-400">
                                {reaction.count}
                              </span>
                            </button>
                          ))}
                        </div>
                      )}
                  </div>
                </div>
              );
            })}

            {/* Typing indicator */}
            {typingUsers.size > 0 && (
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 ml-11">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <span
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: '0.2s' }}
                  />
                  <span
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: '0.4s' }}
                  />
                </div>
                <span>
                  {Array.from(typingUsers).join(', ')}{' '}
                  {typingUsers.size === 1 ? 'is' : 'are'} typing...
                </span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </>
        )}
      </div>
    </div>
  );
}
