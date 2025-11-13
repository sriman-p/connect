'use client';

/**
 * Kanban Column Component
 * Column container for Kanban cards
 */

import { useDroppable } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { KanbanCard } from './kanban-card';
import type { Issue } from '@/lib/types/api';
import { cn } from '@/lib/utils';

interface KanbanColumnProps {
  id: string;
  title: string;
  color: string;
  issues: Issue[];
}

const COLOR_VARIANTS: Record<string, string> = {
  gray: 'border-gray-300 dark:border-gray-700',
  blue: 'border-blue-300 dark:border-blue-700',
  yellow: 'border-yellow-300 dark:border-yellow-700',
  purple: 'border-purple-300 dark:border-purple-700',
  green: 'border-green-300 dark:border-green-700',
  red: 'border-red-300 dark:border-red-700',
};

export function KanbanColumn({ id, title, color, issues }: KanbanColumnProps) {
  const { setNodeRef, isOver } = useDroppable({ id });

  return (
    <div className="flex-shrink-0 w-80">
      <div
        className={cn(
          'bg-gray-50 dark:bg-gray-900 rounded-lg border-2 transition-colors',
          COLOR_VARIANTS[color] || COLOR_VARIANTS.gray,
          isOver && 'border-blue-500 dark:border-blue-400 bg-blue-50 dark:bg-blue-950'
        )}
      >
        {/* Column header */}
        <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-sm text-gray-900 dark:text-white">
              {title}
            </h3>
            <span className="text-xs font-medium text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-800 px-2 py-1 rounded">
              {issues.length}
            </span>
          </div>
        </div>

        {/* Column content */}
        <div
          ref={setNodeRef}
          className="p-3 space-y-3 min-h-[200px] max-h-[calc(100vh-300px)] overflow-y-auto"
        >
          <SortableContext
            items={issues.map((issue) => issue.id)}
            strategy={verticalListSortingStrategy}
          >
            {issues.map((issue) => (
              <KanbanCard key={issue.id} issue={issue} />
            ))}
          </SortableContext>

          {issues.length === 0 && (
            <p className="text-sm text-gray-400 dark:text-gray-600 text-center py-8">
              No issues
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
