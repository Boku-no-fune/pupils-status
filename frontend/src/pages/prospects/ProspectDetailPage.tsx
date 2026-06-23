/**
 * 未入会(見込み)生徒 詳細ページ
 * ステージ状況 + スタッフ記録 (入会時にこの記録が在籍生に引き継がれる想定)
 */

import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, UserPlus, MessageSquare, Plus, Trash2, ListChecks } from 'lucide-react'
import { prospectsApi } from '@/api/prospects'
import { gradeLabel } from '@/components/ui/GradeLabel'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

const STATUS_STYLE: Record<string, string> = {
  完了: 'bg-green-100 text-green-700',
  対応中: 'bg-yellow-100 text-yellow-700',
  未対応: 'bg-gray-100 text-gray-500',
}

export default function ProspectDetailPage() {
  const { prospectId } = useParams<{ prospectId: string }>()
  const navigate = useNavigate()
  const id = parseInt(prospectId || '0')
  const queryClient = useQueryClient()

  const { data: p, isLoading, isError } = useQuery({
    queryKey: ['prospect-detail', id],
    queryFn: () => prospectsApi.get(id),
    enabled: !!id,
  })

  const [content, setContent] = useState('')
  const createNote = useMutation({
    mutationFn: () => prospectsApi.createNote(id, { note_type: 'その他', content }),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['prospect-detail', id] }); setContent('') },
  })
  const deleteNote = useMutation({
    mutationFn: (noteId: number) => prospectsApi.deleteNote(id, noteId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['prospect-detail', id] }),
  })

  if (isLoading) return <div className="p-6"><LoadingSpinner text="読み込み中..." /></div>
  if (isError || !p) return <div className="p-6 text-center text-red-500">データの取得に失敗しました</div>

  return (
    <div className="p-6 max-w-screen-lg mx-auto space-y-6">
      <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900">
        <ArrowLeft size={16} /> 戻る
      </button>

      {/* ヘッダー */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-amber-100 flex items-center justify-center">
            <UserPlus size={22} className="text-amber-500" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-gray-900">{p.name}</h1>
              <span className="text-xs bg-amber-50 text-amber-700 px-2 py-0.5 rounded-full border border-amber-200">未入会（見込み）</span>
            </div>
            <div className="flex items-center gap-3 mt-1 text-sm text-gray-500 flex-wrap">
              {p.grade && <span>{gradeLabel(p.grade)}</span>}
              {p.school && <span>• {p.school}</span>}
              {p.source && <span>• 経路: {p.source}</span>}
              {p.first_contact_at && <span>• 初回接触: {p.first_contact_at}</span>}
            </div>
            {p.address && <p className="text-xs text-gray-400 mt-1">{p.address}</p>}
          </div>
        </div>
      </div>

      {/* ステージ状況 */}
      <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
        <h2 className="flex items-center gap-2 text-sm font-semibold text-gray-800 mb-4">
          <ListChecks size={16} className="text-blue-500" /> 入会前ファネル ステージ状況
        </h2>
        <div className="space-y-2">
          {p.stages.map((s) => (
            <div key={s.stage} className="flex items-center gap-3">
              <span className="text-sm text-gray-700 w-32 flex-shrink-0">{s.stage}</span>
              <span className={`text-xs px-2 py-0.5 rounded-full ${STATUS_STYLE[s.status]}`}>{s.status}</span>
              {s.memo && <span className="text-xs text-gray-500">{s.memo}</span>}
              {s.occurred_at && <span className="text-xs text-gray-300 ml-auto">{s.occurred_at}</span>}
            </div>
          ))}
        </div>
        <p className="text-xs text-gray-400 mt-3">※ ステージの編集は「未入会生徒状況」タブから行えます。</p>
      </div>

      {/* スタッフ記録 (入会時に引き継ぎ) */}
      <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
        <h2 className="flex items-center gap-2 text-sm font-semibold text-gray-800 mb-1">
          <MessageSquare size={16} className="text-blue-500" /> スタッフ記録
        </h2>
        <p className="text-xs text-gray-400 mb-4">入会時、この記録はそのまま在籍生の記録に引き継がれます。</p>

        <div className="space-y-2 mb-3">
          {p.staff_notes.length === 0 ? (
            <p className="text-sm text-gray-400">記録がありません</p>
          ) : p.staff_notes.map((n) => (
            <div key={n.id} className="border border-gray-100 rounded-lg p-3 bg-gray-50 group">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <span className="text-xs font-semibold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full">{n.note_type}</span>
                    <span className="text-xs text-gray-400">{new Date(n.occurred_at).toLocaleDateString('ja-JP')}</span>
                    {n.teacher_name && <span className="text-xs text-gray-400">• {n.teacher_name}</span>}
                  </div>
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">{n.content}</p>
                  {n.tags && n.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-1.5">
                      {n.tags.map((t) => <span key={t} className="text-xs text-blue-500">{t}</span>)}
                    </div>
                  )}
                </div>
                <button onClick={() => deleteNote.mutate(n.id)} className="text-gray-300 hover:text-red-400 opacity-0 group-hover:opacity-100">
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="flex gap-2">
          <input
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="記録を追加...（#タグ で分類）"
            className="flex-1 text-sm px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-400"
          />
          <button
            onClick={() => createNote.mutate()}
            disabled={!content.trim() || createNote.isPending}
            className="flex items-center gap-1 text-sm px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-40"
          >
            <Plus size={14} /> 追加
          </button>
        </div>
      </div>
    </div>
  )
}
