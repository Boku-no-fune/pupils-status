/**
 * ダッシュボード上部カードのドリルダウン用モーダル
 * 休会中 / 高リスク / 平均出席率(低い順) の該当生徒を一覧表示
 */

import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { X } from 'lucide-react'
import { dashboardApi } from '@/api/dashboard'
import { gradeLabel } from '@/components/ui/GradeLabel'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

interface Props {
  kind: 'on_leave' | 'high_risk' | 'low_attendance'
  title: string
  onClose: () => void
}

export default function StatStudentsModal({ kind, title, onClose }: Props) {
  const navigate = useNavigate()
  const { data, isLoading } = useQuery({
    queryKey: ['stat-students', kind],
    queryFn: () => dashboardApi.statStudents(kind),
  })

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[80vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200">
          <h3 className="text-base font-semibold text-gray-800">
            {title}
            {data && <span className="ml-2 text-sm text-gray-400">{data.length} 名</span>}
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700">
            <X size={20} />
          </button>
        </div>

        <div className="overflow-y-auto p-2">
          {isLoading ? (
            <LoadingSpinner text="読み込み中..." />
          ) : !data || data.length === 0 ? (
            <p className="text-center text-gray-400 py-8 text-sm">該当する生徒はいません</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-gray-400 border-b border-gray-100">
                  <th className="px-3 py-2 text-left">氏名</th>
                  <th className="px-3 py-2 text-left">学年</th>
                  <th className="px-3 py-2 text-left">クラス</th>
                  <th className="px-3 py-2 text-left">出席率</th>
                  <th className="px-3 py-2 text-left">担当</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {data.map((s) => (
                  <tr
                    key={s.id}
                    onClick={() => { onClose(); navigate(`/students/${s.id}`) }}
                    className="hover:bg-blue-50 cursor-pointer"
                  >
                    <td className="px-3 py-2 font-medium text-gray-800">{s.name}</td>
                    <td className="px-3 py-2 text-gray-500">{gradeLabel(s.grade)}</td>
                    <td className="px-3 py-2 text-gray-500">{s.class_label || '—'}</td>
                    <td className="px-3 py-2">
                      <span className={
                        s.attendance_rate_30d < 60 ? 'text-red-600 font-semibold' :
                        s.attendance_rate_30d < 75 ? 'text-yellow-600 font-medium' : 'text-green-600'
                      }>
                        {s.attendance_rate_30d.toFixed(0)}%
                      </span>
                    </td>
                    <td className="px-3 py-2 text-gray-500">{s.assigned_teacher_name || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  )
}
