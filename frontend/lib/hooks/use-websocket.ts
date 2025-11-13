/**
 * WebSocket Hook
 * Manages WebSocket connection for real-time messaging
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import { getAccessToken } from '../utils/token';
import type { Message } from '../types/api';

interface UseWebSocketProps {
  channelId: number;
  onMessage?: (message: Message) => void;
  onTyping?: (data: { user_id: number; user_name: string; is_typing: boolean }) => void;
  onUserStatus?: (data: { user_id: number; status: 'online' | 'offline' }) => void;
}

interface SendMessageData {
  content: string;
  parent_message_id?: number;
}

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

export function useWebSocket({
  channelId,
  onMessage,
  onTyping,
  onUserStatus,
}: UseWebSocketProps) {
  const socketRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Connect to WebSocket
  useEffect(() => {
    const token = getAccessToken();

    if (!token || !channelId) {
      setError('Missing authentication or channel ID');
      return;
    }

    // Create WebSocket connection
    const wsUrl = `${WS_URL}/ws/chat/${channelId}/`;
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      setError(null);

      // Send authentication
      socket.send(
        JSON.stringify({
          type: 'auth',
          token,
        })
      );
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        switch (data.type) {
          case 'chat_message':
            onMessage?.(data.message);
            break;

          case 'typing_indicator':
            onTyping?.({
              user_id: data.user_id,
              user_name: data.user_name,
              is_typing: data.is_typing,
            });
            break;

          case 'user_status':
            onUserStatus?.({
              user_id: data.user_id,
              status: data.status,
            });
            break;

          case 'error':
            setError(data.message || 'WebSocket error');
            break;

          default:
            console.log('Unknown message type:', data.type);
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    socket.onerror = (event) => {
      console.error('WebSocket error:', event);
      setError('WebSocket connection error');
    };

    socket.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };

    socketRef.current = socket;

    // Cleanup on unmount
    return () => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    };
  }, [channelId, onMessage, onTyping, onUserStatus]);

  // Send message
  const sendMessage = useCallback((data: SendMessageData) => {
    const socket = socketRef.current;

    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setError('WebSocket not connected');
      return;
    }

    socket.send(
      JSON.stringify({
        type: 'message',
        content: data.content,
        parent_message_id: data.parent_message_id,
      })
    );
  }, []);

  // Send typing indicator
  const sendTyping = useCallback((isTyping: boolean) => {
    const socket = socketRef.current;

    if (!socket || socket.readyState !== WebSocket.OPEN) {
      return;
    }

    socket.send(
      JSON.stringify({
        type: 'typing',
        is_typing: isTyping,
      })
    );
  }, []);

  // Send reaction
  const sendReaction = useCallback((messageId: number, emoji: string) => {
    const socket = socketRef.current;

    if (!socket || socket.readyState !== WebSocket.OPEN) {
      return;
    }

    socket.send(
      JSON.stringify({
        type: 'reaction',
        message_id: messageId,
        emoji,
      })
    );
  }, []);

  return {
    isConnected,
    error,
    sendMessage,
    sendTyping,
    sendReaction,
  };
}
