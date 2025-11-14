'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api/client';
import CollaborativeEditor from '@/components/documents/collaborative-editor';
import PageTransition from '@/components/animations/page-transition';
import AnimatedButton, { AnimatedIconButton } from '@/components/animations/animated-button';

interface Document {
  id: number;
  title: string;
  slug: string;
  doc_type: string;
  content: any;
  workspace: number;
  project: number | null;
  permission_level: string;
  is_archived: boolean;
  created_by: {
    id: number;
    email: string;
    full_name: string;
  };
  updated_at: string;
}

export default function DocumentEditorPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [title, setTitle] = useState('');

  const { data: document, isLoading } = useQuery<Document>({
    queryKey: ['document', params.id],
    queryFn: async () => {
      const response = await apiClient.get(`/documents/${params.id}/`);
      setTitle(response.data.title);
      return response.data;
    },
  });

  const updateTitleMutation = useMutation({
    mutationFn: async (newTitle: string) => {
      const response = await apiClient.patch(`/documents/${params.id}/`, {
        title: newTitle,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['document', params.id] });
      setIsEditingTitle(false);
    },
  });

  const saveContentMutation = useMutation({
    mutationFn: async (content: any) => {
      const response = await apiClient.patch(`/documents/${params.id}/`, {
        content,
      });
      return response.data;
    },
  });

  const archiveMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post(`/documents/${params.id}/archive/`);
      return response.data;
    },
    onSuccess: () => {
      router.push('/documents');
    },
  });

  const handleSaveTitle = () => {
    if (title.trim() && title !== document?.title) {
      updateTitleMutation.mutate(title);
    } else {
      setIsEditingTitle(false);
    }
  };

  if (isLoading || !document) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  return (
    <PageTransition>
      <div className="min-h-screen bg-white flex flex-col">
        {/* Top Bar */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="border-b border-gray-200 px-6 py-4"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4 flex-1">
              <AnimatedIconButton onClick={() => router.push('/documents')}>
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </AnimatedIconButton>

              {isEditingTitle ? (
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  onBlur={handleSaveTitle}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleSaveTitle();
                    if (e.key === 'Escape') {
                      setTitle(document.title);
                      setIsEditingTitle(false);
                    }
                  }}
                  className="text-2xl font-semibold border-b-2 border-blue-500 focus:outline-none px-2"
                  autoFocus
                />
              ) : (
                <h1
                  className="text-2xl font-semibold cursor-pointer hover:text-blue-600 transition-colors"
                  onClick={() => setIsEditingTitle(true)}
                >
                  {document.title}
                </h1>
              )}

              {updateTitleMutation.isPending && (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />
              )}
            </div>

            <div className="flex items-center gap-2">
              <AnimatedButton
                variant="ghost"
                size="sm"
                onClick={() => {
                  if (confirm('Are you sure you want to archive this document?')) {
                    archiveMutation.mutate();
                  }
                }}
              >
                Archive
              </AnimatedButton>

              <AnimatedButton variant="ghost" size="sm">
                Share
              </AnimatedButton>

              <AnimatedButton variant="ghost" size="sm">
                •••
              </AnimatedButton>
            </div>
          </div>

          {/* Document Info */}
          <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
            <span>Created by {document.created_by.full_name}</span>
            <span>•</span>
            <span>Last updated {new Date(document.updated_at).toLocaleDateString()}</span>
            <span>•</span>
            <span className="capitalize">{document.permission_level}</span>
          </div>
        </motion.div>

        {/* Editor */}
        <div className="flex-1 overflow-hidden">
          <CollaborativeEditor
            documentId={params.id}
            initialContent={document.content}
            onSave={(content) => saveContentMutation.mutate(content)}
            readonly={false}
          />
        </div>
      </div>
    </PageTransition>
  );
}
