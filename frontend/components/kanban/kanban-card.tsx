'use client';

/**
 * Kanban Card Component
 * Individual issue card for Kanban board
 */

import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { GripVertical, MessageSquare, Paperclip } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import type { Issue } from '@/lib/types/api';

interface KanbanCardProps {
  issue: Issue;
  isDragging?: boolean;
}

const PRIORITY_COLORS: Record<string, string> = {
  none: 'text-gray-400',
  low: 'text-blue-500',
  medium: 'text-yellow-500',
  high: 'text-orange-500',
  urgent: 'text-red-500',
};

const TYPE_ICONS: Record<string, string> = {
  bug: '🐛',
  feature: '✨',
  improvement: '🔧',
  task: '📋',
  epic: '🎯',
};

export function KanbanCard({ issue, isDragging = false }: KanbanCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging: isSortableDragging,
  } = useSortable({ id: issue.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={cn(
        'bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-3 shadow-sm hover:shadow-md transition-shadow cursor-grab active:cursor-grabbing',
        (isDragging || isSortableDragging) && 'opacity-50'
      )}
      {...attributes}
      {...listeners}
    >
      {/* Card header */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <span className="text-lg flex-shrink-0">
            {TYPE_ICONS[issue.issue_type] || '📋'}
          </span>
          <span className="text-xs font-mono text-gray-500 dark:text-gray-400 flex-shrink-0">
            {issue.identifier}
          </span>
        </div>
        <GripVertical className="h-4 w-4 text-gray-400 flex-shrink-0" />
      </div>

      {/* Card title */}
      <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3 line-clamp-2">
        {issue.title}
      </h4>

      {/* Card footer */}
      <div className="flex items-center justify-between gap-2">
        {/* Priority badge */}
        <div className="flex items-center gap-2">
          {issue.priority !== 'none' && (
            <div
              className={cn(
                'text-xs font-medium px-2 py-0.5 rounded',
                PRIORITY_COLORS[issue.priority]
              )}
            >
              {issue.priority.charAt(0).toUpperCase() + issue.priority.slice(1)}
            </div>
          )}

          {/* Comment count */}
          {issue.comment_count > 0 && (
            <div className="flex items-center gap-1 text-gray-500 dark:text-gray-400">
              <MessageSquare className="h-3 w-3" />
              <span className="text-xs">{issue.comment_count}</span>
            </div>
          )}

          {/* Attachment count */}
          {issue.attachments && issue.attachments.length > 0 && (
            <div className="flex items-center gap-1 text-gray-500 dark:text-gray-400">
              <Paperclip className="h-3 w-3" />
              <span className="text-xs">{issue.attachments.length}</span>
            </div>
          )}
        </div>

        {/* Assignee avatar */}
        {issue.assignee_data && (
          <Avatar className="h-6 w-6">
            <AvatarImage
              src={issue.assignee_data.avatar_url}
              alt={issue.assignee_data.full_name}
            />
            <AvatarFallback className="text-xs bg-gradient-to-br from-blue-500 to-purple-600 text-white">
              {getInitials(issue.assignee_data.full_name)}
            </AvatarFallback>
          </Avatar>
        )}
      </div>

      {/* Labels */}
      {issue.labels_data && issue.labels_data.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {issue.labels_data.slice(0, 3).map((label) => (
            <span
              key={label.id}
              className="text-xs px-2 py-0.5 rounded"
              style={{
                backgroundColor: `${label.color}20`,
                color: label.color,
              }}
            >
              {label.name}
            </span>
          ))}
          {issue.labels_data.length > 3 && (
            <span className="text-xs text-gray-500">
              +{issue.labels_data.length - 3}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
