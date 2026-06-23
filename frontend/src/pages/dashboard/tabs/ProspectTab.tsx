/**
 * Tab: 未入会生徒状況
 * 生徒ごとに、問い合わせ〜季節講習受講の各ステージ状況を一覧表示。
 * 各ステージは 未対応/対応中/完了 + 対応メモ を手入力で更新できる。
 * 上部にファネル集計を表示 (営業目標・アプローチタブと連携)。
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { X } from 'lucide-react'
import { prospectsApi } from '@/api/prospects'
import { gradeLabel } from '@/components/ui/GradeLabel'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import type { Prospect, ProspectStage } from '@/types'

const STAGES = ['問い合わせ', '資料請求', '入会テスト', '体験授業', 'イベント参加', '季節講習受講']
const STATUS_STYLE: Record<string, string> = {
  完了: 'bg-green-100 text-green-700 border-green-200',
  対応中: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  未対応: 'bg-gray-50 text-gray-400 border-gray-200',
}

export default function ProspectTab() {
  const navigate = useNavigate()
  const { data: prospects, isLoading } = useQuery({ queryKey: ['prospects'], queryFn: () => prospectsApi.list() })
  const { data: funnel } = useQuery({ queryKey: ['prospect-funnel'], queryFn: () => prospectsApi.funnel() })
  const [editing, setEditing] = useState<{ prospect: Prospect; stage: ProspectStage } | null>(null)

  if (isLoading) return <LoadingSpinner text="未入会生徒を読み込み中..." />

  return (
    <div className="space-y-6">
      {/* ファネル集計 */}
      {funnel && (
        <div>
          <h3 className="text-base font-semibold text-gray-800 mb-1">入会前ファネル（{funnel.total_prospects}名）</h3>
          <p className="text-xs text-gray-400 mb-3">各ステージの完了状況。営業目標・アプローチタブと連携しています。</p>
          <div className="grid grid-cols-2 md:grid-cols-6 gap-2">
            {funnel.stages.map((s) => (
              <div key={s.stage} className="border border-gray-100 rounded-lg p-3 text-center">
                <p className="text-xs text-gray-500 mb-1">{s.stage}</p>
                <p className="text-xl font-bold text-gray-800">{s.完了}</p>
                <p className="text-[11px] text-gray-400">対応中 {s.対応中} / 未 {s.未対応}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 生徒×ステージ 一覧 */}
      <div className="overflow-x-auto">
        <table className="text-sm border-collapse w-full">
          <thead>
            <tr className="bg-gray-50">
              <th className="sticky left-0 bg-gray-50 px-3 py-2 text-left text-xs font-semibold text-gray-500 border-b border-gray-200 min-w-36">氏名</th>
              <th className="px-3 py-2 text-left text-xs font-semibold text-gray-500 border-b border-gray-200">学年</th>
              <th className="px-3 py-2 text-left text-xs font-semibold text-gray-500 border-b border-gray-200">経路</th>
              {STAGES.map((s) => (
                <th key={s} className="px-2 py-2 text-center text-xs font-semibold text-gray-500 border-b border-gray-200 whitespace-nowrap">{s}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {prospects?.map((p) => (
              <tr key={p.id} className="hover:bg-gray-50">
                <td className="sticky left-0 bg-white px-3 py-2 font-medium whitespace-nowrap">
                  <button onClick={() => navigate(`/prospects/${p.id}`)} className="text-blue-700 hover:underline">{p.name}</button>
                </td>
                <td className="px-3 py-2 text-gray-500">{p.grade ? gradeLabel(p.grade) : '—'}</td>
                <td className="px-3 py-2 text-gray-500 whitespace-nowrap">{p.source || '—'}</td>
                {STAGES.map((stageName) => {
                  const stage = p.stages.find((s) => s.stage === stageName) || { stage: stageName, status: '未対応' as const }
                  return (
                    <td key={stageName} className="px-2 py-2 text-center">
                      <button
                        onClick={() => setEditing({ prospect: p, stage })}
                        title={stage.memo || ''}
                        className={`text-xs px-2 py-1 rounded-full border w-16 ${STATUS_STYLE[stage.status]} hover:opacity-80`}
                      >
                        {stage.status}
                        {stage.memo && <span className="block text-[10px] opacity-70 truncate">{stage.memo.slice(0, 8)}</span>}
                      </button>
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="bg-blue-50 rounded-lg p-4 text-sm text-blue-700">
        <p className="font-medium mb-1">この画面について</p>
        <ul className="list-disc list-inside space-y-1 text-blue-600">
          <li>各ステージのマークをクリックすると、状況(未対応/対応中/完了)と対応メモを編集できます</li>
          <li>イベント参加・季節講習受講は時期に応じてシステムから追加されます</li>
          <li>入力内容は上部ファネル集計および営業目標・アプローチタブに反映されます</li>
        </ul>
      </div>

      {editing && (
        <StageEditor
          prospect={editing.prospect}
          stage={editing.stage}
          onClose={() => setEditing(null)}
        />
      )}
    </div>
  )
}

function StageEditor({
  prospect, stage, onClose,
}: {
  prospect: Prospect; stage: ProspectStage; onClose: () => void
}) {
  const queryClient = useQueryClient()
  const [status, setStatus] = useState(stage.status)
  const [memo, setMemo] = useState(stage.memo || '')

  const mutation = useMutation({
    mutationFn: () => prospectsApi.upsertStage(prospect.id, { stage: stage.stage, status, memo }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prospects'] })
      queryClient.invalidateQueries({ queryKey: ['prospect-funnel'] })
      onClose()
    },
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={onClose}>
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200">
          <h3 className="text-base font-semibold text-gray-800">
            {prospect.name} <span className="text-sm text-gray-400 ml-1">/ {stage.stage}</span>
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700"><X size={20} /></button>
        </div>
        <div className="p-5 space-y-4">
          <div>
            <p className="text-xs text-gray-500 mb-2">状況</p>
            <div className="flex gap-2">
              {['未対応', '対応中', '完了'].map((st) => (
                <button
                  key={st}
                  onClick={() => setStatus(st as ProspectStage['status'])}
                  className={`flex-1 text-sm px-3 py-2 rounded-lg border ${
                    status === st ? STATUS_STYLE[st] + ' font-semibold' : 'bg-white border-gray-200 text-gray-500'
                  }`}
                >
                  {st}
                </button>
              ))}
            </div>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-2">対応メモ</p>
            <textarea
              value={memo}
              onChange={(e) => setMemo(e.target.value)}
              rows={3}
              placeholder="対応内容を入力..."
              className="w-full text-sm px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-400 resize-none"
            />
          </div>
          <div className="flex gap-2 justify-end">
            <button onClick={onClose} className="text-sm px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">キャンセル</button>
            <button
              onClick={() => mutation.mutate()}
              disabled={mutation.isPending}
              className="text-sm px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-40"
            >
              {mutation.isPending ? '保存中...' : '保存'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
