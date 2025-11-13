/**
 * Projects Page
 * View and manage projects with Kanban board
 */

'use client';

import { useState, useEffect } from 'react';
import { Metadata } from 'next';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { KanbanBoard } from '@/components/kanban/kanban-board';
import { getProjects } from '@/lib/api/projects';
import type { Project } from '@/lib/types/api';

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    setIsLoading(true);
    try {
      const response = await getProjects();
      const projectList = response.results || [];
      setProjects(projectList);

      // Select first project by default
      if (projectList.length > 0 && !selectedProject) {
        setSelectedProject(projectList[0]);
      }
    } catch (error) {
      console.error('Failed to load projects:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex-shrink-0 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Projects
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Manage your projects and track progress
              </p>
            </div>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Project
            </Button>
          </div>

          {/* Project selector */}
          {projects.length > 0 && (
            <div className="flex items-center gap-4">
              <Select
                value={selectedProject?.id.toString()}
                onValueChange={(value) => {
                  const project = projects.find((p) => p.id === parseInt(value));
                  if (project) setSelectedProject(project);
                }}
              >
                <SelectTrigger className="w-64">
                  <SelectValue placeholder="Select a project" />
                </SelectTrigger>
                <SelectContent>
                  {projects.map((project) => (
                    <SelectItem key={project.id} value={project.id.toString()}>
                      <div className="flex items-center gap-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: project.color }}
                        />
                        {project.name}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {selectedProject && (
                <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                  <div>
                    <span className="font-medium">{selectedProject.issue_count}</span>{' '}
                    issues
                  </div>
                  <div>
                    <span className="font-medium">{selectedProject.progress}%</span>{' '}
                    complete
                  </div>
                  <div className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded text-xs font-medium">
                    {selectedProject.status}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Kanban board */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full overflow-x-auto p-6">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                <p className="text-gray-600 dark:text-gray-400">
                  Loading projects...
                </p>
              </div>
            </div>
          ) : projects.length === 0 ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  No projects found. Create your first project to get started.
                </p>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Project
                </Button>
              </div>
            </div>
          ) : selectedProject ? (
            <KanbanBoard projectId={selectedProject.id} />
          ) : (
            <div className="flex items-center justify-center h-64">
              <p className="text-gray-600 dark:text-gray-400">
                Select a project to view its Kanban board
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
