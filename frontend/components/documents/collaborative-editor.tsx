'use client';

import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Collaboration from '@tiptap/extension-collaboration';
import CollaborationCursor from '@tiptap/extension-collaboration-cursor';
import { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import * as Y from 'yjs';

interface CollaborativeEditorProps {
  documentId: string;
  initialContent?: any;
  onSave?: (content: any) => void;
  readonly?: boolean;
}

interface ActiveUser {
  user_id: number;
  user_name: string;
  user_email: string;
  user_color: string;
  session_id: string;
  cursor_position?: any;
}

export default function CollaborativeEditor({
  documentId,
  initialContent,
  onSave,
  readonly = false,
}: CollaborativeEditorProps) {
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);
  const [activeUsers, setActiveUsers] = useState<ActiveUser[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [ydoc] = useState(() => new Y.Doc());
  const [sequenceNumber, setSequenceNumber] = useState(0);

  // Initialize WebSocket connection
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const wsUrl = `ws://localhost:8000/ws/documents/${documentId}/?token=${token}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);

      // Send heartbeat every 30 seconds
      const heartbeatInterval = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'heartbeat' }));
        }
      }, 30000);

      return () => clearInterval(heartbeatInterval);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case 'active_users':
          setActiveUsers(data.users);
          break;

        case 'user_joined':
          setActiveUsers((prev) => [
            ...prev,
            {
              user_id: data.user_id,
              user_name: data.user_name,
              user_email: data.user_email,
              user_color: data.user_color,
              session_id: data.session_id,
            },
          ]);
          break;

        case 'user_left':
          setActiveUsers((prev) =>
            prev.filter((user) => user.session_id !== data.session_id)
          );
          break;

        case 'content_update':
          // Apply operation from other users
          applyRemoteOperation(data.operation);
          break;

        case 'cursor_update':
          // Update cursor position for user
          setActiveUsers((prev) =>
            prev.map((user) =>
              user.session_id === data.session_id
                ? { ...user, cursor_position: data.cursor_position }
                : user
            )
          );
          break;
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };

    setWebsocket(ws);

    return () => {
      ws.close();
    };
  }, [documentId]);

  const applyRemoteOperation = useCallback((operation: any) => {
    // Apply operation to the editor
    // This would involve applying the operation to the Y.Doc
    // and triggering an editor update
    console.log('Applying remote operation:', operation);
  }, []);

  const sendOperation = useCallback(
    (operation: any) => {
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        const seq = sequenceNumber + 1;
        setSequenceNumber(seq);

        websocket.send(
          JSON.stringify({
            type: 'content_change',
            operation,
            base_version: 1, // This should be the current document version
            sequence_number: seq,
          })
        );
      }
    },
    [websocket, sequenceNumber]
  );

  const sendCursorPosition = useCallback(
    (position: any) => {
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(
          JSON.stringify({
            type: 'cursor_move',
            cursor_position: position,
          })
        );
      }
    },
    [websocket]
  );

  const editor = useEditor({
    extensions: [
      StarterKit,
      Collaboration.configure({
        document: ydoc,
      }),
      CollaborationCursor.configure({
        provider: null, // We'll handle sync via WebSocket
      }),
    ],
    content: initialContent || '<p>Start typing...</p>',
    editable: !readonly,
    onUpdate: ({ editor }) => {
      // Send changes to WebSocket
      const json = editor.getJSON();

      // Get the last transaction
      const transaction = editor.state.tr;

      // Create operation from transaction
      const operation = {
        type: 'update',
        content: json,
      };

      sendOperation(operation);

      // Call onSave callback
      if (onSave) {
        onSave(json);
      }
    },
    onSelectionUpdate: ({ editor }) => {
      // Send cursor position
      const { from, to } = editor.state.selection;
      sendCursorPosition({ from, to });
    },
  });

  if (!editor) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  return (
    <div className="w-full h-full flex flex-col">
      {/* Toolbar */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="border-b border-gray-200 p-2 flex items-center gap-2 bg-white sticky top-0 z-10"
      >
        <button
          onClick={() => editor.chain().focus().toggleBold().run()}
          className={`px-3 py-1 rounded ${
            editor.isActive('bold') ? 'bg-blue-600 text-white' : 'bg-gray-100'
          }`}
        >
          <strong>B</strong>
        </button>
        <button
          onClick={() => editor.chain().focus().toggleItalic().run()}
          className={`px-3 py-1 rounded ${
            editor.isActive('italic') ? 'bg-blue-600 text-white' : 'bg-gray-100'
          }`}
        >
          <em>I</em>
        </button>
        <button
          onClick={() => editor.chain().focus().toggleStrike().run()}
          className={`px-3 py-1 rounded ${
            editor.isActive('strike') ? 'bg-blue-600 text-white' : 'bg-gray-100'
          }`}
        >
          <s>S</s>
        </button>

        <div className="h-6 w-px bg-gray-300 mx-2" />

        <button
          onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
          className={`px-3 py-1 rounded ${
            editor.isActive('heading', { level: 1 }) ? 'bg-blue-600 text-white' : 'bg-gray-100'
          }`}
        >
          H1
        </button>
        <button
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          className={`px-3 py-1 rounded ${
            editor.isActive('heading', { level: 2 }) ? 'bg-blue-600 text-white' : 'bg-gray-100'
          }`}
        >
          H2
        </button>

        <div className="h-6 w-px bg-gray-300 mx-2" />

        <button
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          className={`px-3 py-1 rounded ${
            editor.isActive('bulletList') ? 'bg-blue-600 text-white' : 'bg-gray-100'
          }`}
        >
          • List
        </button>
        <button
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          className={`px-3 py-1 rounded ${
            editor.isActive('orderedList') ? 'bg-blue-600 text-white' : 'bg-gray-100'
          }`}
        >
          1. List
        </button>

        {/* Connection status */}
        <div className="ml-auto flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-red-500'
            }`}
          />
          <span className="text-sm text-gray-600">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </motion.div>

      {/* Active users */}
      {activeUsers.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="border-b border-gray-200 p-2 bg-gray-50 flex items-center gap-2"
        >
          <span className="text-sm text-gray-600">Active users:</span>
          {activeUsers.map((user) => (
            <motion.div
              key={user.session_id}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
              className="flex items-center gap-1"
            >
              <div
                className="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-medium"
                style={{ backgroundColor: user.user_color }}
                title={user.user_name}
              >
                {user.user_name.charAt(0).toUpperCase()}
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* Editor */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="flex-1 overflow-auto p-8 bg-white"
      >
        <EditorContent
          editor={editor}
          className="prose prose-lg max-w-none focus:outline-none"
        />
      </motion.div>
    </div>
  );
}
