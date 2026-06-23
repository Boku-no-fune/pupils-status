/**
 * Tab3: 営業目標・アプローチ管理
 * - キャンペーンを小タブで切替 (夏期講習 / 中３後期特訓講座 …)
 * - 在籍生は「正会員」、それ以外はアプローチ状況を表示
 * - 生徒をクリックで生徒ページへ遷移
 * - 未入会ファネルと連携表示
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { FileText } from 'lucide-react'
import { dashboardApi } from '@/api/dashboard'
import { salesApi } from '@/api/sales'
import { prospectsApi } from '@/api/prospects'
import { useViewStore } from '@/stores/viewStore'
import GoalProgressBar from '@/components/ui/GoalProgressBar'
import { SalesStatusBadge } from '@/components/ui/Badge'
import { gradeLabel } from '@/components/ui/GradeLabel'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import type { CampaignRow } from '@/types'

export default function SalesTab() {
  const navigate = useNavigate()
  const showAll = useViewStore((s) => s.showAll)
  const [showReport, setShowReport] = useState(false)
  const [activeProduct, setActiveProduct] = useState<string | null>(null)

  const { data: progress, isLoading: progressLoading } = useQuery({
    queryKey: ['sales-progress'],
    queryFn: () => dashboardApi.salesProgress(),
  })
  const { data: funnel } = useQuery({ queryKey: ['prospect-funnel'], queryFn: () => prospectsApi.funnel() })
  const { data: report } = useQuery({
    queryKey: ['sales-report'],
    queryFn: () => salesApi.getReport(),
    enabled: showReport,
  })

  // キャンペーン(小タブ)。progressの各エントリ = 1キャンペーン
  const campaigns = progress || []
  const current = activeProduct
    ? campaigns.find((c) => c.target_product === activeProduct)
    : campaigns[0]
  const product = current?.target_product || ''

  const { data: rows, isLoading: rowsLoading } = useQuery({
    queryKey: ['campaign-rows', product, showAll],
    queryFn: () => salesApi.campaignRows(product, showAll),
    enabled: !!product,
  })

  if (progressLoading) return <LoadingSpinner text="営業データを読み込み中..." />

  return (
    <div className="space-y-6">
      {/* キャンペーン小タブ */}
      <div className="flex flex-wrap gap-2 border-b border-gray-100 pb-3">
        {campaigns.map((c) => (
          <button
            key={c.goal_id}
            onClick={() => setActiveProduct(c.target_product || null)}
            className={`text-sm px-4 py-1.5 rounded-full border transition-colors ${
              product === c.target_product
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-600 border-gray-200 hover:border-blue-300'
            }`}
          >
            {c.target_product || c.goal_type}
          </button>
        ))}
      </div>

      {/* 目標進捗 */}
      {current && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-5 border border-blue-100">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-gray-900">{current.target_product} 申込目標</h3>
              <p className="text-sm text-gray-500">期間: {current.period}</p>
            </div>
            <button onClick={() => setShowReport(!showReport)} className="btn-secondary text-xs gap-1.5">
              <FileText size={14} /> レポート生成
            </button>
          </div>
          <GoalProgressBar current={current.signed_up} target={current.target_count} label="申込達成率" />
          <div className="grid grid-cols-4 gap-3 mt-4 text-center">
            {[
              { label: '申込済', value: current.signed_up, color: 'text-green-600' },
              { label: '交渉中', value: current.in_progress, color: 'text-blue-600' },
              { label: '辞退', value: current.declined, color: 'text-red-500' },
              { label: '未着手', value: current.not_started, color: 'text-gray-500' },
            ].map((item) => (
              <div key={item.label} className="bg-white rounded-lg p-3 shadow-sm">
                <div className={`text-xl font-bold ${item.color}`}>{item.value}</div>
                <div className="text-xs text-gray-500">{item.label}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {showReport && report?.report_text && (
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-semibold text-gray-800">上司報告用サマリー</h4>
            <button onClick={() => window.print()} className="btn-secondary text-xs">印刷</button>
          </div>
          <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans bg-gray-50 rounded-lg p-4">{report.report_text}</pre>
        </div>
      )}

      {/* アプローチ状況一覧 (在籍生は正会員) */}
      <div>
        <h3 className="font-semibold text-gray-800 mb-3">アプローチ状況一覧 — {product}</h3>
        {rowsLoading ? (
          <LoadingSpinner />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">生徒名</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">学年</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">クラス</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">アクション</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">担当者</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {(rows || []).map((r: CampaignRow) => (
                  <tr
                    key={r.id}
                    onClick={() => r.student_id && navigate(`/students/${r.student_id}`)}
                    className="hover:bg-blue-50 cursor-pointer"
                  >
                    <td className="px-4 py-3 font-medium text-gray-900">{r.student_name || '—'}</td>
                    <td className="px-4 py-3 text-gray-500">{r.grade ? gradeLabel(r.grade) : '—'}</td>
                    <td className="px-4 py-3 text-gray-500">{r.class_label || '—'}</td>
                    <td className="px-4 py-3">
                      {r.is_member ? (
                        <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700">正会員</span>
                      ) : (
                        <SalesStatusBadge status={r.status} />
                      )}
                    </td>
                    <td className="px-4 py-3 text-gray-600">{r.assigned_teacher_name || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {(rows?.length || 0) === 0 && (
              <div className="text-center text-gray-400 py-8">対象データがありません</div>
            )}
          </div>
        )}
      </div>

      {/* 未入会ファネル連携 */}
      {funnel && (
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h3 className="font-semibold text-gray-800 mb-1">未入会ファネル（{funnel.total_prospects}名）</h3>
          <p className="text-xs text-gray-400 mb-3">「未入会生徒状況」タブと連携。各ステージの完了数。</p>
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
    </div>
  )
}
