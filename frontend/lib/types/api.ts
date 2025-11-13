/**
 * API Types and Interfaces
 * TypeScript definitions for API requests and responses
 */

// ============================================================================
// User & Authentication
// ============================================================================

export interface User {
  id: number;
  email: string;
  full_name: string;
  avatar_url?: string;
  role: 'admin' | 'manager' | 'member' | 'guest';
  timezone: string;
  language: string;
  is_active: boolean;
  is_email_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  tokens: {
    access: string;
    refresh: string;
  };
}

export interface RegisterRequest {
  email: string;
  full_name: string;
  password: string;
  password_confirm: string;
  timezone?: string;
  language?: string;
}

export interface RegisterResponse {
  user: User;
  tokens: {
    access: string;
    refresh: string;
  };
  message: string;
}

export interface TokenRefreshRequest {
  refresh: string;
}

export interface TokenRefreshResponse {
  access: string;
  refresh?: string;
}

// ============================================================================
// Workspace
// ============================================================================

export interface Workspace {
  id: number;
  name: string;
  slug: string;
  description?: string;
  logo_url?: string;
  owner: number;
  owner_data?: User;
  member_count: number;
  project_count: number;
  created_at: string;
  updated_at: string;
}

export interface WorkspaceMember {
  id: number;
  workspace: number;
  user: number;
  user_data?: User;
  role: 'owner' | 'admin' | 'member' | 'guest';
  permissions: number;
  permissions_list: string[];
  is_active: boolean;
  joined_at: string;
}

// ============================================================================
// Project
// ============================================================================

export interface Project {
  id: number;
  workspace: number;
  workspace_data?: Workspace;
  name: string;
  identifier: string;
  description?: string;
  status: 'planning' | 'active' | 'on_hold' | 'completed' | 'cancelled';
  start_date?: string;
  target_date?: string;
  completed_at?: string;
  lead?: number;
  lead_data?: User;
  color: string;
  icon?: string;
  is_archived: boolean;
  issue_count: number;
  completed_issue_count: number;
  progress: number;
  created_at: string;
  updated_at: string;
}

export interface ProjectMember {
  id: number;
  project: number;
  user: number;
  user_data?: User;
  role: 'lead' | 'member' | 'viewer';
  joined_at: string;
}

// ============================================================================
// Issue
// ============================================================================

export interface Issue {
  id: number;
  workspace: number;
  project: number;
  project_data?: Project;
  identifier: string;
  title: string;
  description?: string;
  status: 'backlog' | 'todo' | 'in_progress' | 'in_review' | 'done' | 'cancelled';
  priority: 'none' | 'low' | 'medium' | 'high' | 'urgent';
  issue_type: 'bug' | 'feature' | 'improvement' | 'task' | 'epic';
  assignee?: number;
  assignee_data?: User;
  reporter: number;
  reporter_data?: User;
  parent?: number;
  parent_data?: Partial<Issue>;
  labels: number[];
  labels_data?: Label[];
  estimate_points?: number;
  sort_order: number;
  start_date?: string;
  target_date?: string;
  started_at?: string;
  completed_at?: string;
  comment_count: number;
  sub_issue_count: number;
  comments?: IssueComment[];
  attachments?: IssueAttachment[];
  created_at: string;
  updated_at: string;
}

export interface Label {
  id: number;
  workspace: number;
  name: string;
  color: string;
  created_at: string;
}

export interface IssueComment {
  id: number;
  issue: number;
  author: number;
  author_data?: User;
  content: string;
  is_edited: boolean;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
}

export interface IssueAttachment {
  id: number;
  issue: number;
  file_name: string;
  file_url: string;
  file_size: number;
  file_type: string;
  uploaded_by: number;
  uploaded_at: string;
}

// ============================================================================
// Messaging
// ============================================================================

export interface Channel {
  id: number;
  workspace: number;
  workspace_data?: Workspace;
  name: string;
  slug: string;
  description?: string;
  channel_type: 'public' | 'private' | 'direct';
  created_by: number;
  created_by_data?: User;
  is_archived: boolean;
  member_count: number;
  unread_count?: number;
  last_message?: Message;
  created_at: string;
  updated_at: string;
}

export interface ChannelMember {
  id: number;
  channel: number;
  user: number;
  user_data?: User;
  mute_notifications: boolean;
  last_read_at?: string;
  joined_at: string;
}

export interface Message {
  id: number;
  channel: number;
  author: number;
  author_data?: User;
  content: string;
  message_type: 'text' | 'file' | 'system';
  parent_message?: number;
  parent_message_data?: Partial<Message>;
  thread_reply_count: number;
  mentions: number[];
  mentions_data?: User[];
  is_edited: boolean;
  is_deleted: boolean;
  reactions?: MessageReaction[];
  reaction_summary?: ReactionSummary[];
  attachments?: MessageAttachment[];
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}

export interface MessageReaction {
  id: number;
  message: number;
  user: number;
  user_data?: User;
  emoji: string;
  created_at: string;
}

export interface ReactionSummary {
  emoji: string;
  count: number;
  users: User[];
}

export interface MessageAttachment {
  id: number;
  message: number;
  file_name: string;
  file_url: string;
  file_size: number;
  file_type: string;
  thumbnail_url?: string;
  uploaded_at: string;
}

// ============================================================================
// Kanban Board
// ============================================================================

export interface KanbanBoard {
  backlog: Issue[];
  todo: Issue[];
  in_progress: Issue[];
  in_review: Issue[];
  done: Issue[];
  cancelled: Issue[];
}

// ============================================================================
// API Response Wrappers
// ============================================================================

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  error?: string;
  detail?: string;
  message?: string;
  [key: string]: any;
}
