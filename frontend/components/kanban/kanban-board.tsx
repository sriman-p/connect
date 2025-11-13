'use client';

/**
 * Kanban Board Component
 * Drag-and-drop issue board
 */

import { useState, useEffect } from 'react';
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import { KanbanColumn } from './kanban-column';
import { KanbanCard } from './kanban-card';
import { getKanbanBoard, moveIssue } from '@/lib/api/issues';
import type { Issue, KanbanBoard as KanbanBoardType } from '@/lib/types/api';
import { Loader2 } from 'lucide-react';

interface KanbanBoardProps {
  projectId: number;
}

const COLUMN_CONFIGS = [
  { id: 'backlog', title: 'Backlog', color: 'gray' },
  { id: 'todo', title: 'To Do', color: 'blue' },
  { id: 'in_progress', title: 'In Progress', color: 'yellow' },
  { id: 'in_review', title: 'In Review', color: 'purple' },
  { id: 'done', title: 'Done', color: 'green' },
  { id: 'cancelled', title: 'Cancelled', color: 'red' },
] as const;

export function KanbanBoard({ projectId }: KanbanBoardProps) {
  const [board, setBoard] = useState<KanbanBoardType | null>(null);
  const [activeIssue, setActiveIssue] = useState<Issue | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  useEffect(() => {
    loadBoard();
  }, [projectId]);

  const loadBoard = async () => {
    setIsLoading(true);
    try {
      const data = await getKanbanBoard(projectId);
      setBoard(data);
    } catch (error) {
      console.error('Failed to load Kanban board:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event;
    const issue = findIssue(active.id as number);
    setActiveIssue(issue);
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;

    setActiveIssue(null);

    if (!over || !board) return;

    const issueId = active.id as number;
    const newStatus = over.id as keyof KanbanBoardType;

    // Find the issue
    const issue = findIssue(issueId);

    if (!issue || issue.status === newStatus) return;

    // Optimistically update UI
    const updatedBoard = { ...board };
    const oldStatus = issue.status as keyof KanbanBoardType;

    // Remove from old column
    updatedBoard[oldStatus] = updatedBoard[oldStatus].filter(
      (i) => i.id !== issueId
    );

    // Add to new column
    updatedBoard[newStatus] = [...updatedBoard[newStatus], issue];

    setBoard(updatedBoard);

    // Update on server
    try {
      await moveIssue(issueId, { status: newStatus });
    } catch (error) {
      console.error('Failed to move issue:', error);
      // Revert on error
      loadBoard();
    }
  };

  const findIssue = (id: number): Issue | null => {
    if (!board) return null;

    for (const column of Object.values(board)) {
      const issue = column.find((i: Issue) => i.id === id);
      if (issue) return issue;
    }

    return null;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    );
  }

  if (!board) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Failed to load Kanban board</p>
      </div>
    );
  }

  return (
    <DndContext
      sensors={sensors}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="flex gap-4 overflow-x-auto pb-4">
        {COLUMN_CONFIGS.map((column) => (
          <KanbanColumn
            key={column.id}
            id={column.id}
            title={column.title}
            color={column.color}
            issues={board[column.id] || []}
          />
        ))}
      </div>

      <DragOverlay>
        {activeIssue ? <KanbanCard issue={activeIssue} isDragging /> : null}
      </DragOverlay>
    </DndContext>
  );
}
