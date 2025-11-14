'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import apiClient from '@/lib/api/client';
import CollaborativeSpreadsheet from '@/components/spreadsheets/collaborative-spreadsheet';
import PageTransition from '@/components/animations/page-transition';
import AnimatedButton, { AnimatedIconButton } from '@/components/animations/animated-button';

interface Spreadsheet {
  id: number;
  title: string;
  slug: string;
  workspace: number;
  project: number | null;
  permission_level: string;
  is_archived: boolean;
  created_by: {
    id: number;
    email: string;
    full_name: string;
  };
  sheets: Sheet[];
  updated_at: string;
}

interface Sheet {
  id: number;
  name: string;
  position: number;
  row_count: number;
  column_count: number;
  tab_color: string;
}

export default function SpreadsheetEditorPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [title, setTitle] = useState('');
  const [activeSheetId, setActiveSheetId] = useState<string>('');

  const { data: spreadsheet, isLoading } = useQuery<Spreadsheet>({
    queryKey: ['spreadsheet', params.id],
    queryFn: async () => {
      const response = await apiClient.get(`/spreadsheets/${params.id}/`);
      setTitle(response.data.title);
      if (response.data.sheets && response.data.sheets.length > 0) {
        setActiveSheetId(response.data.sheets[0].id.toString());
      }
      return response.data;
    },
  });

  const updateTitleMutation = useMutation({
    mutationFn: async (newTitle: string) => {
      const response = await apiClient.patch(`/spreadsheets/${params.id}/`, {
        title: newTitle,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['spreadsheet', params.id] });
      setIsEditingTitle(false);
    },
  });

  const archiveMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post(`/spreadsheets/${params.id}/archive/`);
      return response.data;
    },
    onSuccess: () => {
      router.push('/spreadsheets');
    },
  });

  const createSheetMutation = useMutation({
    mutationFn: async () => {
      const position = spreadsheet?.sheets.length || 0;
      const response = await apiClient.post('/sheets/', {
        spreadsheet: params.id,
        name: `Sheet${position + 1}`,
        position,
      });
      return response.data;
    },
    onSuccess: (newSheet) => {
      queryClient.invalidateQueries({ queryKey: ['spreadsheet', params.id] });
      setActiveSheetId(newSheet.id.toString());
    },
  });

  const handleSaveTitle = () => {
    if (title.trim() && title !== spreadsheet?.title) {
      updateTitleMutation.mutate(title);
    } else {
      setIsEditingTitle(false);
    }
  };

  if (isLoading || !spreadsheet) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600" />
      </div>
    );
  }

  const activeSheet = spreadsheet.sheets.find(s => s.id.toString() === activeSheetId);

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
              <AnimatedIconButton onClick={() => router.push('/spreadsheets')}>
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
                      setTitle(spreadsheet.title);
                      setIsEditingTitle(false);
                    }
                  }}
                  className="text-2xl font-semibold border-b-2 border-green-500 focus:outline-none px-2"
                  autoFocus
                />
              ) : (
                <h1
                  className="text-2xl font-semibold cursor-pointer hover:text-green-600 transition-colors"
                  onClick={() => setIsEditingTitle(true)}
                >
                  {spreadsheet.title}
                </h1>
              )}

              {updateTitleMutation.isPending && (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-600" />
              )}
            </div>

            <div className="flex items-center gap-2">
              <AnimatedButton
                variant="ghost"
                size="sm"
                onClick={() => {
                  if (confirm('Are you sure you want to archive this spreadsheet?')) {
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

          {/* Spreadsheet Info */}
          <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
            <span>Created by {spreadsheet.created_by.full_name}</span>
            <span>•</span>
            <span>Last updated {new Date(spreadsheet.updated_at).toLocaleDateString()}</span>
            <span>•</span>
            <span className="capitalize">{spreadsheet.permission_level}</span>
          </div>
        </motion.div>

        {/* Spreadsheet */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {activeSheet ? (
            <CollaborativeSpreadsheet
              spreadsheetId={params.id}
              sheetId={activeSheetId}
              rows={activeSheet.row_count}
              columns={activeSheet.column_count}
              readonly={false}
            />
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <p className="text-gray-600 mb-4">No sheets available</p>
                <AnimatedButton
                  variant="primary"
                  onClick={() => createSheetMutation.mutate()}
                  disabled={createSheetMutation.isPending}
                >
                  {createSheetMutation.isPending ? 'Creating...' : 'Create Sheet'}
                </AnimatedButton>
              </div>
            </div>
          )}
        </div>

        {/* Sheet Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="border-t border-gray-200 bg-gray-50 px-6 py-3 flex items-center gap-2 overflow-x-auto"
        >
          {spreadsheet.sheets.map((sheet) => (
            <button
              key={sheet.id}
              onClick={() => setActiveSheetId(sheet.id.toString())}
              className={`px-4 py-2 rounded-t-lg whitespace-nowrap transition-colors ${
                activeSheetId === sheet.id.toString()
                  ? 'bg-white border-t-2 border-green-500 font-medium'
                  : 'bg-gray-100 hover:bg-gray-200'
              }`}
              style={{
                borderBottomColor: activeSheetId === sheet.id.toString() ? sheet.tab_color : undefined,
              }}
            >
              {sheet.name}
            </button>
          ))}

          <AnimatedIconButton
            onClick={() => createSheetMutation.mutate()}
            disabled={createSheetMutation.isPending}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </AnimatedIconButton>
        </motion.div>
      </div>
    </PageTransition>
  );
}
