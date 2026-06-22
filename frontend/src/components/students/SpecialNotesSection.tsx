/**
 * 特記事項セクション (最上段コンテナ直下)
 * 手入力で追記、重要度タグ(高/中/低)を付与。
 */

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { AlertCircle, Plus, Trash2 } from 'lucide-react'
import { studentsApi } from '@/api/students'
import type { SpecialNote } from '@/types'

interface Props {
  studentId: number
  notes: SpecialNote[]
}

const IMPORTANCE_STYLE: Record<string, string> = {
  高: 'bg-red-100 text-red-700 border-red-200',
  中: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  低: 'bg-gray-100 text-gray-600 border-gray-200',
}

export default function SpecialNotesSection({ studentId, notes }: Props) {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [content, setContent] = useState('')
  const [importance, setImportance] = useState('中')

  const createMutation = useMutation({
    mutationFn: () => studentsApi.createSpecialNote(studentId, { content, importance }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['student-detail', studentId] })
      setContent('')
      setShowForm(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => studentsApi.deleteSpecialNote(studentId, id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['student-detail', studentId] }),
  })

  return (
    <div className="bg-white rounded-xl border border-amber-200 p-5 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <h2 className="flex items-center gap-2 text-sm font-semibold text-gray-800">
          <AlertCircle size={16} className="text-amber-500" />
          特記事項
        </h2>
        {!showForm && (
          <button onClick={() => setShowForm(true)} className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700">
            <Plus size={14} /> 追加
          </button>
        )}
      </div>

      {notes.length === 0 && !showForm ? (
        <p className="text-sm text-gray-400">特記事項はありません</p>
      ) : (
        <div className="space-y-2">
          {notes.map((note) => (
            <div key={note.id} className="flex items-start gap-2 group">
              <span className={`text-xs px-2 py-0.5 rounded-full border flex-shrink-0 ${IMPORTANCE_STYLE[note.importance] || IMPORTANCE_STYLE['中']}`}>
                {note.importance}
              </span>
              <p className="flex-1 text-sm text-gray-700 whitespace-pre-wrap">{note.content}</p>
              <button
                onClick={() => deleteMutation.mutate(note.id)}
                className="text-gray-300 hover:text-red-400 opacity-0 group-hover:opacity-100 flex-shrink-0"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      )}

      {showForm && (
        <div className="mt-3 border border-blue-200 bg-blue-50 rounded-lg p-3 space-y-2">
          <div className="flex gap-2 items-center">
            <span className="text-xs text-gray-500">重要度:</span>
            {['高', '中', '低'].map((lv) => (
              <button
                key={lv}
                onClick={() => setImportance(lv)}
                className={`text-xs px-2.5 py-1 rounded-full border ${
                  importance === lv ? IMPORTANCE_STYLE[lv] : 'bg-white text-gray-400 border-gray-200'
                }`}
              >
                {lv}
              </button>
            ))}
          </div>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="特記事項を入力..."
            rows={2}
            className="w-full text-sm px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-400 resize-none"
          />
          <div className="flex gap-2">
            <button
              onClick={() => createMutation.mutate()}
              disabled={!content.trim() || createMutation.isPending}
              className="text-sm px-4 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-40"
            >
              保存
            </button>
            <button onClick={() => { setShowForm(false); setContent('') }}
              className="text-sm px-4 py-1.5 border border-gray-300 rounded-lg hover:bg-white">
              キャンセル
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
