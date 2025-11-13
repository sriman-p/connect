/**
 * Messaging API Service
 * Handles channels and messages
 */

import apiClient from './client';
import type {
  Channel,
  Message,
  MessageReaction,
  PaginatedResponse,
} from '../types/api';

/**
 * Get all channels
 */
export const getChannels = async (params?: {
  workspace?: number;
  channel_type?: string;
}): Promise<PaginatedResponse<Channel>> => {
  const response = await apiClient.get<PaginatedResponse<Channel>>('/channels/', {
    params,
  });
  return response.data;
};

/**
 * Get single channel
 */
export const getChannel = async (id: number): Promise<Channel> => {
  const response = await apiClient.get<Channel>(`/channels/${id}/`);
  return response.data;
};

/**
 * Create new channel
 */
export const createChannel = async (
  data: Partial<Channel>
): Promise<Channel> => {
  const response = await apiClient.post<Channel>('/channels/', data);
  return response.data;
};

/**
 * Get messages for a channel
 */
export const getMessages = async (
  channelId: number,
  params?: { limit?: number; offset?: number }
): Promise<PaginatedResponse<Message>> => {
  const response = await apiClient.get<PaginatedResponse<Message>>(
    `/channels/${channelId}/messages/`,
    { params }
  );
  return response.data;
};

/**
 * Send a message
 */
export const sendMessage = async (data: {
  channel: number;
  content: string;
  parent_message?: number;
}): Promise<Message> => {
  const response = await apiClient.post<Message>('/messages/', data);
  return response.data;
};

/**
 * Edit a message
 */
export const editMessage = async (
  id: number,
  content: string
): Promise<Message> => {
  const response = await apiClient.patch<Message>(`/messages/${id}/`, {
    content,
  });
  return response.data;
};

/**
 * Delete a message
 */
export const deleteMessage = async (id: number): Promise<void> => {
  await apiClient.delete(`/messages/${id}/`);
};

/**
 * Toggle reaction on a message
 */
export const toggleReaction = async (
  messageId: number,
  emoji: string
): Promise<MessageReaction> => {
  const response = await apiClient.post<MessageReaction>(
    `/messages/${messageId}/toggle_reaction/`,
    { emoji }
  );
  return response.data;
};

/**
 * Mark channel as read
 */
export const markChannelAsRead = async (
  channelId: number
): Promise<void> => {
  await apiClient.post(`/channels/${channelId}/mark_read/`);
};
