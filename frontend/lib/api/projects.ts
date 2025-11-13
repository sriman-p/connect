/**
 * Projects API Service
 * Handles project CRUD operations
 */

import apiClient from './client';
import type { Project, PaginatedResponse } from '../types/api';

/**
 * Get all projects with optional filters
 */
export const getProjects = async (params?: {
  workspace?: number;
  status?: string;
  search?: string;
}): Promise<PaginatedResponse<Project>> => {
  const response = await apiClient.get<PaginatedResponse<Project>>('/projects/', {
    params,
  });
  return response.data;
};

/**
 * Get single project by ID
 */
export const getProject = async (id: number): Promise<Project> => {
  const response = await apiClient.get<Project>(`/projects/${id}/`);
  return response.data;
};

/**
 * Create new project
 */
export const createProject = async (
  data: Partial<Project>
): Promise<Project> => {
  const response = await apiClient.post<Project>('/projects/', data);
  return response.data;
};

/**
 * Update project
 */
export const updateProject = async (
  id: number,
  data: Partial<Project>
): Promise<Project> => {
  const response = await apiClient.patch<Project>(`/projects/${id}/`, data);
  return response.data;
};

/**
 * Delete project
 */
export const deleteProject = async (id: number): Promise<void> => {
  await apiClient.delete(`/projects/${id}/`);
};
