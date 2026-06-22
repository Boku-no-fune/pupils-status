/**
 * Tab: スタッフ記録・保護者アプローチの月別実施状況
 * 生徒 × 月 のマトリクス。各セルの回数をクリックすると内容をポップアップ表示。
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { X } from 'lucide-react'
import { dashboardApi } from '@/api/dashboard'
import { studentsApi } from '@/api/students'
import { gradeLabel } from '@/components/ui/GradeLabel'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

export default function ActivityMatrixTab() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['activity-matrix'],
    queryFn: () => dashboardApi.activityMatrix(6),
  })
  const [popup, setPopup] = useState<{ studentId: number; studentName: string; month: string } | null>(null)

  if (isLoading) return <LoadingSpinner text="実施状況を読み込み中..." />
  if (isError || !data) return <div className="text-center text-red-500 py-8">データの取得に失敗しました</div>

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-base font-semibold text-gray-800 mb-1">スタッフ記録・保護者アプローチ 月別実施状況</h3>
        <p className="text-xs text-gray-400 mb-4">数字をクリックすると、その月の記録内容を表示します（スタッフ記録＋保護者アプローチの合計）</p>
      </div>

      <div className="overflow-x-auto">
        <table className="text-sm border-collapse">
          <thead>
            <tr className="bg-gray-50">
              <th className="sticky left-0 bg-gray-50 px-3 py-2 text-left text-xs font-semibold text-gray-500 border-b border-gray-200 min-w-40">生徒</th>
              <th className="px-3 py-2 text-left text-xs font-semibold text-gray-500 border-b border-gray-200">学年</th>
              <th className="px-3 py-2 text-left text-xs font-semibold text-gray-500 border-b border-gray-200">クラス</th>
              {data.months.map((m) => (
                <th key={m} className="px-3 py-2 text-center text-xs font-semibold text-gray-500 border-b border-gray-200 whitespace-nowrap">
                  {m.replace('-', '/')}
                </th>
              ))}
              <th className="px-3 py-2 text-center text-xs font-semibold text-gray-500 border-b border-gray-200">計</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {data.rows.map((row) => (
              <tr key={row.student_id} className="hover:bg-gray-50">
                <td className="sticky left-0 bg-white px-3 py-2 font-medium text-gray-900 whitespace-nowrap">{row.student_name}</td>
                <td className="px-3 py-2 text-gray-500">{gradeLabel(row.grade)}</td>
                <td className="px-3 py-2 text-gray-500">{row.class_label || '—'}</td>
                {row.cells.map((cell) => (
                  <td key={cell.month} className="px-3 py-2 text-center">
                    {cell.total > 0 ? (
                      <button
                        onClick={() => setPopup({ studentId: row.student_id, studentName: row.student_name, month: cell.month })}
                        title={`スタッフ記録 ${cell.staff} / 保護者 ${cell.contact}`}
                        className="inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 transition-colors"
                      >
                        {cell.total}
                      </button>
                    ) : (
                      <span className="text-gray-300">·</span>
                    )}
                  </td>
                ))}
                <td className="px-3 py-2 text-center font-semibold text-gray-700">{row.total}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {popup && (
        <ActivityPopup
          studentId={popup.studentId}
          studentName={popup.studentName}
          month={popup.month}
          onClose={() => setPopup(null)}
        />
      )}
    </div>
  )
}

function ActivityPopup({
  studentId, studentName, month, onClose,
}: {
  studentId: number; studentName: string; month: string; onClose: () => void
}) {
  const { data, isLoading } = useQuery({
    queryKey: ['activities', studentId, month],
    queryFn: () => studentsApi.listActivities(studentId, month),
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={onClose}>
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[80vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200">
          <h3 className="text-base font-semibold text-gray-800">
            {studentName} <span className="text-sm text-gray-400 ml-2">{month.replace('-', '年')}月</span>
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700"><X size={20} /></button>
        </div>
        <div className="overflow-y-auto p-4 space-y-3">
          {isLoading ? (
            <LoadingSpinner text="読み込み中..." />
          ) : !data || data.length === 0 ? (
            <p className="text-center text-gray-400 py-6 text-sm">記録がありません</p>
          ) : (
            data.map((r, i) => (
              <div key={i} className="border border-gray-100 rounded-lg p-3 bg-gray-50">
                <div className="flex items-center gap-2 mb-1 flex-wrap">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${r.kind === 'スタッフ記録' ? 'bg-indigo-50 text-indigo-600' : 'bg-emerald-50 text-emerald-600'}`}>
                    {r.kind}
                  </span>
                  <span className="text-xs font-medium text-gray-600">{r.type}</span>
                  <span className="text-xs text-gray-400">
                    {new Date(r.occurred_at).toLocaleDateString('ja-JP', { month: 'numeric', day: 'numeric' })}
                  </span>
                  {r.teacher_name && <span className="text-xs text-gray-400">• {r.teacher_name}</span>}
                </div>
                {r.content && <p className="text-sm text-gray-700 whitespace-pre-wrap">{r.content}</p>}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
