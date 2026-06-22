/**
 * Tab3: 営業目標・アプローチ管理
 * 目標進捗バー + アプローチ状況テーブル + レポート生成
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { FileText, RefreshCw } from 'lucide-react'
import { dashboardApi } from '@/api/dashboard'
import { salesApi } from '@/api/sales'
import { prospectsApi } from '@/api/prospects'
import GoalProgressBar from '@/components/ui/GoalProgressBar'
import { SalesStatusBadge } from '@/components/ui/Badge'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import type { SalesAction } from '@/types'

const ACTION_TYPE_LABELS: Record<string, string> = {
  trial_invitation: '体験招待',
  phone_follow: '電話フォロー',
  dm_campaign: 'DMキャンペーン',
  visit: '来塾案内',
}

export default function SalesTab() {
  const [showReport, setShowReport] = useState(false)
  const [statusFilter, setStatusFilter] = useState('')
  const queryClient = useQueryClient()

  const { data: progress, isLoading: progressLoading } = useQuery({
    queryKey: ['sales-progress'],
    queryFn: () => dashboardApi.salesProgress(),
  })

  const { data: actions, isLoading: actionsLoading } = useQuery({
    queryKey: ['sales-actions', statusFilter],
    queryFn: () => salesApi.listActions(statusFilter ? { status: statusFilter } : {}),
  })

  const { data: report, isLoading: reportLoading } = useQuery({
    queryKey: ['sales-report'],
    queryFn: () => salesApi.getReport(),
    enabled: showReport,
  })

  const { data: funnel } = useQuery({
    queryKey: ['prospect-funnel'],
    queryFn: () => prospectsApi.funnel(),
  })

  const updateAction = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      salesApi.updateAction(id, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sales-actions'] })
      queryClient.invalidateQueries({ queryKey: ['sales-progress'] })
    },
  })

  const p = progress?.[0]

  return (
    <div className="space-y-6">
      {/* 営業目標進捗 */}
      {progressLoading ? (
        <LoadingSpinner text="目標データを読み込み中..." />
      ) : p ? (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-5 border border-blue-100">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-gray-900">{p.target_product || p.goal_type} 申込目標</h3>
              <p className="text-sm text-gray-500">期間: {p.period}</p>
            </div>
            <button
              onClick={() => setShowReport(!showReport)}
              className="btn-secondary text-xs gap-1.5"
            >
              <FileText size={14} />
              レポート生成
            </button>
          </div>
          <GoalProgressBar
            current={p.signed_up}
            target={p.target_count}
            label="申込達成率"
          />
          <div className="grid grid-cols-4 gap-3 mt-4 text-center">
            {[
              { label: '申込済', value: p.signed_up, color: 'text-green-600' },
              { label: '交渉中', value: p.in_progress, color: 'text-blue-600' },
              { label: '辞退', value: p.declined, color: 'text-red-500' },
              { label: '未着手', value: p.not_started, color: 'text-gray-500' },
            ].map((item) => (
              <div key={item.label} className="bg-white rounded-lg p-3 shadow-sm">
                <div className={`text-xl font-bold ${item.color}`}>{item.value}</div>
                <div className="text-xs text-gray-500">{item.label}</div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center text-gray-400 py-6">営業目標が設定されていません</div>
      )}

      {/* レポート表示 */}
      {showReport && report && (
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-semibold text-gray-800">上司報告用サマリー</h4>
            <button
              onClick={() => window.print()}
              className="btn-secondary text-xs"
            >
              印刷
            </button>
          </div>
          <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans bg-gray-50 rounded-lg p-4">
            {report.report_text}
          </pre>
        </div>
      )}

      {/* 未入会ファネル連携 */}
      {funnel && (
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h3 className="font-semibold text-gray-800 mb-1">未入会ファネル（{funnel.total_prospects}名）</h3>
          <p className="text-xs text-gray-400 mb-3">「未入会生徒状況」タブと連携。各ステージの完了数を表示。</p>
          <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
            {funnel.stages.map((s) => (
              <div key={s.stage} className="border border-gray-100 rounded-lg p-2 text-center">
                <p className="text-[11px] text-gray-500 mb-0.5">{s.stage}</p>
                <p className="text-lg font-bold text-gray-800">{s.完了}</p>
                <p className="text-[10px] text-gray-400">対応中 {s.対応中}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* アプローチ一覧テーブル */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-gray-800">アプローチ状況一覧</h3>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-sm px-3 py-1.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">すべて</option>
            <option value="pending">未着手</option>
            <option value="in_progress">アプローチ済</option>
            <option value="signed_up">申込済</option>
            <option value="declined">辞退</option>
          </select>
        </div>

        {actionsLoading ? (
          <LoadingSpinner />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">生徒名</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">アクション</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">対象商品</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">ステータス</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">担当者</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">日時</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {(actions || []).slice(0, 50).map((action: SalesAction) => (
                  <tr key={action.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{action.student_name || '—'}</td>
                    <td className="px-4 py-3 text-gray-600">
                      {ACTION_TYPE_LABELS[action.action_type] || action.action_type}
                    </td>
                    <td className="px-4 py-3 text-gray-600">{action.target_product || '—'}</td>
                    <td className="px-4 py-3">
                      <SalesStatusBadge status={action.status} />
                    </td>
                    <td className="px-4 py-3 text-gray-600">{action.assigned_teacher_name || '—'}</td>
                    <td className="px-4 py-3 text-gray-400 text-xs">
                      {action.actioned_at ? new Date(action.actioned_at).toLocaleDateString('ja-JP') : '—'}
                    </td>
                    <td className="px-4 py-3">
                      {action.status !== 'signed_up' && action.status !== 'declined' && (
                        <select
                          value={action.status}
                          onChange={(e) => updateAction.mutate({ id: action.id, status: e.target.value })}
                          className="text-xs px-2 py-1 border border-gray-300 rounded focus:outline-none"
                        >
                          <option value="pending">未着手</option>
                          <option value="in_progress">アプローチ済</option>
                          <option value="signed_up">申込済</option>
                          <option value="declined">辞退</option>
                        </select>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {(actions?.length || 0) === 0 && (
              <div className="text-center text-gray-400 py-8">アクションデータがありません</div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
