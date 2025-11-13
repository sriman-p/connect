/**
 * Issues API Service
 * Handles issue CRUD and Kanban board operations
 */

import apiClient from './client';
import type { Issue, KanbanBoard, PaginatedResponse } from '../types/api';

/**
 * Get all issues with optional filters
 */
export const getIssues = async (params?: {
  project?: number;
  status?: string;
  assignee?: number;
  priority?: string;
  search?: string;
}): Promise<PaginatedResponse<Issue>> => {
  const response = await apiClient.get<PaginatedResponse<Issue>>('/issues/', {
    params,
  });
  return response.data;
};

/**
 * Get Kanban board for a project
 */
export const getKanbanBoard = async (projectId: number): Promise<KanbanBoard> => {
  const response = await apiClient.get<KanbanBoard>('/issues/kanban/', {
    params: { project: projectId },
  });
  return response.data;
};

/**
 * Get single issue by ID
 */
export const getIssue = async (id: number): Promise<Issue> => {
  const response = await apiClient.get<Issue>(`/issues/${id}/`);
  return response.data;
};

/**
 * Create new issue
 */
export const createIssue = async (
  data: Partial<Issue>
): Promise<Issue> => {
  const response = await apiClient.post<Issue>('/issues/', data);
  return response.data;
};

/**
 * Update issue
 */
export const updateIssue = async (
  id: number,
  data: Partial<Issue>
): Promise<Issue> => {
  const response = await apiClient.patch<Issue>(`/issues/${id}/`, data);
  return response.data;
};

/**
 * Delete issue
 */
export const deleteIssue = async (id: number): Promise<void> => {
  await apiClient.delete(`/issues/${id}/`);
};

/**
 * Move issue to different status/column
 */
export const moveIssue = async (
  id: number,
  data: { status: string; sort_order?: number }
): Promise<Issue> => {
  const response = await apiClient.post<{ issue: Issue }>(
    `/issues/${id}/move/`,
    data
  );
  return response.data.issue;
};

/**
 * Assign issue to user
 */
export const assignIssue = async (
  id: number,
  userId: number | null
): Promise<Issue> => {
  const response = await apiClient.post<{ issue: Issue }>(
    `/issues/${id}/assign/`,
    { assignee: userId }
  );
  return response.data.issue;
};

/**
 * Update issue priority
 */
export const updateIssuePriority = async (
  id: number,
  priority: 'none' | 'low' | 'medium' | 'high' | 'urgent'
): Promise<Issue> => {
  return updateIssue(id, { priority });
};
