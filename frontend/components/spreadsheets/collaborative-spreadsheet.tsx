'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { motion } from 'framer-motion';

interface Cell {
  row: number;
  column: number;
  value: string;
  formula?: string;
  format?: CellFormat;
}

interface CellFormat {
  bold?: boolean;
  italic?: boolean;
  color?: string;
  backgroundColor?: string;
  fontSize?: number;
}

interface ActiveUser {
  user_id: number;
  user_name: string;
  user_email: string;
  user_color: string;
  session_id: string;
  selected_cell?: { row: number; column: number };
  selected_range?: {
    startRow: number;
    startCol: number;
    endRow: number;
    endCol: number;
  };
}

interface CollaborativeSpreadsheetProps {
  spreadsheetId: string;
  sheetId: string;
  rows?: number;
  columns?: number;
  readonly?: boolean;
}

export default function CollaborativeSpreadsheet({
  spreadsheetId,
  sheetId,
  rows = 100,
  columns = 26,
  readonly = false,
}: CollaborativeSpreadsheetProps) {
  const [cells, setCells] = useState<Map<string, Cell>>(new Map());
  const [selectedCell, setSelectedCell] = useState<{ row: number; column: number } | null>(null);
  const [editingCell, setEditingCell] = useState<{ row: number; column: number } | null>(null);
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);
  const [activeUsers, setActiveUsers] = useState<ActiveUser[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [sequenceNumber, setSequenceNumber] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Initialize WebSocket connection
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const wsUrl = `ws://localhost:8000/ws/spreadsheets/${spreadsheetId}/?token=${token}`;
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

        case 'cell_changed':
          // Update cell from other users
          const cellKey = `${data.cell_data.row}-${data.cell_data.column}`;
          setCells((prev) => {
            const newCells = new Map(prev);
            newCells.set(cellKey, data.cell_data);
            return newCells;
          });
          break;

        case 'cell_selection':
          // Update user's selected cell
          setActiveUsers((prev) =>
            prev.map((user) =>
              user.session_id === data.session_id
                ? { ...user, selected_cell: data.selected_cell }
                : user
            )
          );
          break;

        case 'range_selection':
          // Update user's selected range
          setActiveUsers((prev) =>
            prev.map((user) =>
              user.session_id === data.session_id
                ? { ...user, selected_range: data.selected_range }
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
  }, [spreadsheetId]);

  const getCellKey = (row: number, column: number) => `${row}-${column}`;

  const getCell = (row: number, column: number): Cell => {
    const key = getCellKey(row, column);
    return cells.get(key) || { row, column, value: '' };
  };

  const updateCell = useCallback(
    (row: number, column: number, value: string, formula?: string) => {
      const cellKey = getCellKey(row, column);
      const updatedCell: Cell = { row, column, value, formula };

      setCells((prev) => {
        const newCells = new Map(prev);
        newCells.set(cellKey, updatedCell);
        return newCells;
      });

      // Send update via WebSocket
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        const seq = sequenceNumber + 1;
        setSequenceNumber(seq);

        websocket.send(
          JSON.stringify({
            type: 'cell_update',
            cell_data: {
              sheet_id: sheetId,
              row,
              column,
              value,
              formula,
              data_type: 'text',
              version: 1,
            },
            base_version: 1,
            sequence_number: seq,
          })
        );
      }
    },
    [websocket, sequenceNumber, sheetId]
  );

  const selectCell = useCallback(
    (row: number, column: number) => {
      setSelectedCell({ row, column });

      // Send selection to WebSocket
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(
          JSON.stringify({
            type: 'cell_select',
            selected_cell: { row, column },
          })
        );
      }
    },
    [websocket]
  );

  const startEditing = useCallback((row: number, column: number) => {
    setEditingCell({ row, column });
    setTimeout(() => {
      inputRef.current?.focus();
    }, 0);
  }, []);

  const stopEditing = useCallback(() => {
    if (editingCell && inputRef.current) {
      updateCell(editingCell.row, editingCell.column, inputRef.current.value);
    }
    setEditingCell(null);
  }, [editingCell, updateCell]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent, row: number, column: number) => {
      if (e.key === 'Enter') {
        if (editingCell) {
          stopEditing();
          selectCell(row + 1, column);
        } else {
          startEditing(row, column);
        }
      } else if (e.key === 'Escape') {
        setEditingCell(null);
      } else if (!editingCell) {
        // Navigate with arrow keys
        if (e.key === 'ArrowUp' && row > 0) {
          selectCell(row - 1, column);
        } else if (e.key === 'ArrowDown' && row < rows - 1) {
          selectCell(row + 1, column);
        } else if (e.key === 'ArrowLeft' && column > 0) {
          selectCell(row, column - 1);
        } else if (e.key === 'ArrowRight' && column < columns - 1) {
          selectCell(row, column + 1);
        }
      }
    },
    [editingCell, stopEditing, selectCell, startEditing, rows, columns]
  );

  const columnToLetter = (column: number): string => {
    let result = '';
    let col = column;
    while (col >= 0) {
      result = String.fromCharCode((col % 26) + 65) + result;
      col = Math.floor(col / 26) - 1;
    }
    return result;
  };

  return (
    <div className="w-full h-full flex flex-col bg-white">
      {/* Toolbar */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="border-b border-gray-200 p-2 flex items-center gap-2 bg-white sticky top-0 z-10"
      >
        <button className="px-3 py-1 rounded bg-gray-100 hover:bg-gray-200">
          <strong>B</strong>
        </button>
        <button className="px-3 py-1 rounded bg-gray-100 hover:bg-gray-200">
          <em>I</em>
        </button>

        <div className="h-6 w-px bg-gray-300 mx-2" />

        <select className="px-2 py-1 border border-gray-300 rounded">
          <option>Arial</option>
          <option>Times New Roman</option>
          <option>Courier New</option>
        </select>

        <select className="px-2 py-1 border border-gray-300 rounded">
          <option>10</option>
          <option>12</option>
          <option>14</option>
          <option>16</option>
        </select>

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
          <span className="text-sm text-gray-600">Editing now:</span>
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

      {/* Spreadsheet grid */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="flex-1 overflow-auto relative"
      >
        <table className="border-collapse w-full">
          <thead className="bg-gray-100 sticky top-0">
            <tr>
              <th className="border border-gray-300 w-12 h-8 text-xs font-medium text-gray-600">
                #
              </th>
              {Array.from({ length: columns }, (_, i) => (
                <th
                  key={i}
                  className="border border-gray-300 min-w-[100px] h-8 text-xs font-medium text-gray-600"
                >
                  {columnToLetter(i)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: rows }, (_, rowIndex) => (
              <tr key={rowIndex}>
                <td className="border border-gray-300 bg-gray-100 text-center text-xs font-medium text-gray-600 sticky left-0">
                  {rowIndex + 1}
                </td>
                {Array.from({ length: columns }, (_, colIndex) => {
                  const cell = getCell(rowIndex, colIndex);
                  const isSelected =
                    selectedCell?.row === rowIndex && selectedCell?.column === colIndex;
                  const isEditing =
                    editingCell?.row === rowIndex && editingCell?.column === colIndex;

                  // Check if any other user has this cell selected
                  const userSelection = activeUsers.find(
                    (user) =>
                      user.selected_cell?.row === rowIndex &&
                      user.selected_cell?.column === colIndex
                  );

                  return (
                    <td
                      key={colIndex}
                      className={`border border-gray-300 h-8 relative ${
                        isSelected ? 'ring-2 ring-blue-500' : ''
                      }`}
                      style={{
                        backgroundColor: userSelection?.user_color
                          ? `${userSelection.user_color}20`
                          : undefined,
                      }}
                      onClick={() => selectCell(rowIndex, colIndex)}
                      onDoubleClick={() => startEditing(rowIndex, colIndex)}
                      tabIndex={0}
                      onKeyDown={(e) => handleKeyDown(e, rowIndex, colIndex)}
                    >
                      {isEditing ? (
                        <input
                          ref={inputRef}
                          type="text"
                          defaultValue={cell.value}
                          className="w-full h-full px-1 outline-none"
                          onBlur={stopEditing}
                          onKeyDown={(e) => handleKeyDown(e, rowIndex, colIndex)}
                        />
                      ) : (
                        <div className="px-1 truncate text-sm">{cell.value}</div>
                      )}
                      {userSelection && (
                        <div
                          className="absolute -top-3 -right-3 w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-medium shadow-lg"
                          style={{ backgroundColor: userSelection.user_color }}
                          title={userSelection.user_name}
                        >
                          {userSelection.user_name.charAt(0).toUpperCase()}
                        </div>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </motion.div>

      {/* Formula bar */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="border-t border-gray-200 p-2 flex items-center gap-2 bg-white"
      >
        <div className="font-mono text-sm text-gray-600 min-w-[60px]">
          {selectedCell && `${columnToLetter(selectedCell.column)}${selectedCell.row + 1}`}
        </div>
        <input
          type="text"
          className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm"
          placeholder="Enter formula or value..."
          value={selectedCell ? getCell(selectedCell.row, selectedCell.column).value : ''}
          onChange={(e) => {
            if (selectedCell) {
              updateCell(selectedCell.row, selectedCell.column, e.target.value);
            }
          }}
        />
      </motion.div>
    </div>
  );
}
