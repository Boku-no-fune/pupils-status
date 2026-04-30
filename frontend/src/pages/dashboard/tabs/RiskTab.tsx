/**
 * Tab4: リスク・AI提案
 * ダミーAIロジックによるリスク生徒一覧と提案表示
 */

import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { AlertTriangle, Lightbulb, TrendingDown, UserX } from 'lucide-react'
import { dashboardApi } from '@/api/dashboard'
import { RiskBadge } from '@/components/ui/Badge'
import { gradeLabel } from '@/components/ui/GradeLabel'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import type { RiskStudent } from '@/types'

export default function RiskTab() {
  const navigate = useNavigate()

  const { data: riskStudents, isLoading } = useQuery({
    queryKey: ['risk-students'],
    queryFn: () => dashboardApi.riskStudents(),
  })

  if (isLoading) return <LoadingSpinner text="リスク分析中..." />

  const highRisk = riskStudents?.filter((s) => s.risk_level === 'high') || []
  const mediumRisk = riskStudents?.filter((s) => s.risk_level === 'medium') || []
  const lowRisk = riskStudents?.filter((s) => s.risk_level === 'low') || []

  return (
    <div className="space-y-6">
      {/* AIラベル */}
      <div className="flex items-center gap-2 text-sm text-indigo-600 bg-indigo-50 rounded-lg px-4 py-3">
        <Lightbulb size={16} />
        <span>
          <strong>AIリスク分析</strong> — ルールベースのリスク判定とAI提案を表示しています。
          実際のClaude AI統合後は、より詳細な分析が可能になります。
        </span>
      </div>

      {/* 高リスク */}
      {highRisk.length > 0 && (
        <section>
          <h3 className="flex items-center gap-2 text-base font-semibold text-red-700 mb-3">
            <AlertTriangle size={18} />
            高リスク生徒 ({highRisk.length}名)
          </h3>
          <div className="grid gap-3">
            {highRisk.map((student) => (
              <RiskStudentCard
                key={student.student_id}
                student={student}
                onClick={() => navigate(`/students/${student.student_id}`)}
              />
            ))}
          </div>
        </section>
      )}

      {/* 中リスク */}
      {mediumRisk.length > 0 && (
        <section>
          <h3 className="flex items-center gap-2 text-base font-semibold text-orange-700 mb-3">
            <TrendingDown size={18} />
            中リスク生徒 ({mediumRisk.length}名)
          </h3>
          <div className="grid gap-3">
            {mediumRisk.slice(0, 10).map((student) => (
              <RiskStudentCard
                key={student.student_id}
                student={student}
                onClick={() => navigate(`/students/${student.student_id}`)}
              />
            ))}
          </div>
        </section>
      )}

      {/* 統計サマリー */}
      <div className="grid grid-cols-3 gap-4 pt-2">
        <div className="bg-red-50 rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-red-600">{highRisk.length}</div>
          <div className="text-sm text-red-500 mt-1">高リスク</div>
        </div>
        <div className="bg-orange-50 rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-orange-600">{mediumRisk.length}</div>
          <div className="text-sm text-orange-500 mt-1">中リスク</div>
        </div>
        <div className="bg-green-50 rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-green-600">{lowRisk.length}</div>
          <div className="text-sm text-green-500 mt-1">低リスク</div>
        </div>
      </div>
    </div>
  )
}

function RiskStudentCard({
  student,
  onClick,
}: {
  student: RiskStudent
  onClick: () => void
}) {
  return (
    <div
      onClick={onClick}
      className="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-md transition-shadow cursor-pointer"
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-semibold text-gray-900">{student.student_name}</span>
            <span className="text-sm text-gray-500">{gradeLabel(student.grade)}</span>
          </div>
          <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
            <span>出席率: <span className={student.attendance_rate_30d < 60 ? 'text-red-600 font-medium' : 'text-gray-700'}>
              {student.attendance_rate_30d.toFixed(0)}%
            </span></span>
            <span>成績: <span className={student.score_trend === 'declining' ? 'text-red-600 font-medium' : 'text-gray-700'}>
              {student.score_trend === 'declining' ? '下降中' : student.score_trend === 'improving' ? '上昇中' : '安定'}
            </span></span>
          </div>
        </div>
        <RiskBadge level={student.risk_level} />
      </div>

      {/* リスク要因 */}
      {student.factors.length > 0 && (
        <div className="mb-3">
          <p className="text-xs font-medium text-gray-500 mb-1">リスク要因</p>
          <ul className="space-y-1">
            {student.factors.map((factor, i) => (
              <li key={i} className="text-xs text-red-600 flex items-start gap-1.5">
                <span className="mt-0.5">•</span>
                {factor}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* AI提案 */}
      {student.suggestions.length > 0 && (
        <div className="bg-indigo-50 rounded-lg p-3">
          <p className="text-xs font-medium text-indigo-600 mb-1.5 flex items-center gap-1">
            <Lightbulb size={12} />
            AI提案
          </p>
          <ul className="space-y-1">
            {student.suggestions.slice(0, 2).map((suggestion, i) => (
              <li key={i} className="text-xs text-indigo-700">
                {i + 1}. {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
