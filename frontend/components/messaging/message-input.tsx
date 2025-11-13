'use client';

/**
 * Message Input Component
 * Input field for sending messages
 */

import { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Smile } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { useWebSocket } from '@/lib/hooks/use-websocket';
import type { Channel } from '@/lib/types/api';

interface MessageInputProps {
  channel: Channel;
  onMessageSent?: () => void;
}

export function MessageInput({ channel, onMessageSent }: MessageInputProps) {
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const { sendMessage, sendTyping, isConnected } = useWebSocket({
    channelId: channel.id,
  });

  useEffect(() => {
    // Auto-focus textarea
    textareaRef.current?.focus();
  }, [channel.id]);

  const handleTyping = () => {
    if (!isTyping) {
      setIsTyping(true);
      sendTyping(true);
    }

    // Clear existing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Set new timeout to stop typing indicator
    typingTimeoutRef.current = setTimeout(() => {
      setIsTyping(false);
      sendTyping(false);
    }, 3000);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!message.trim() || !isConnected) return;

    // Send message via WebSocket
    sendMessage({ content: message.trim() });

    // Clear input
    setMessage('');

    // Stop typing indicator
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    setIsTyping(false);
    sendTyping(false);

    // Focus back on textarea
    textareaRef.current?.focus();

    // Callback
    onMessageSent?.();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Send on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
      <div className="p-4">
        <div className="flex items-end gap-2">
          {/* Attachment button */}
          <Button
            type="button"
            size="icon"
            variant="ghost"
            className="flex-shrink-0"
          >
            <Paperclip className="h-5 w-5" />
          </Button>

          {/* Message input */}
          <div className="flex-1 relative">
            <Textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => {
                setMessage(e.target.value);
                handleTyping();
              }}
              onKeyDown={handleKeyDown}
              placeholder={
                isConnected
                  ? `Message #${channel.name}`
                  : 'Connecting...'
              }
              disabled={!isConnected}
              className="min-h-[44px] max-h-32 resize-none"
              rows={1}
            />
          </div>

          {/* Emoji button */}
          <Button
            type="button"
            size="icon"
            variant="ghost"
            className="flex-shrink-0"
          >
            <Smile className="h-5 w-5" />
          </Button>

          {/* Send button */}
          <Button
            type="submit"
            size="icon"
            disabled={!message.trim() || !isConnected}
            className="flex-shrink-0"
          >
            <Send className="h-5 w-5" />
          </Button>
        </div>

        <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
          <kbd className="px-1.5 py-0.5 text-xs font-semibold bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded">
            Enter
          </kbd>{' '}
          to send,{' '}
          <kbd className="px-1.5 py-0.5 text-xs font-semibold bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded">
            Shift + Enter
          </kbd>{' '}
          for new line
        </p>
      </div>
    </form>
  );
}
