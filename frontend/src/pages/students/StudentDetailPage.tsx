/**
 * 生徒詳細ページ
 * 8セクション構成: 基本情報 / タイムライン / 成績 / 出欠カレンダー /
 *                  保護者コンタクト / 支払い / 営業 / リスク・AI
 */

import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Calendar, TrendingUp, Phone, CreditCard, Target, AlertTriangle, MessageSquare } from 'lucide-react'
import { studentsApi } from '@/api/students'
import { gradeLabel } from '@/components/ui/GradeLabel'
import { StudentStatusBadge, SalesStatusBadge, RiskBadge } from '@/components/ui/Badge'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import AttendanceCalendar from '@/components/charts/AttendanceCalendar'
import ScoreBarChart from '@/components/charts/ScoreBarChart'
import ScoreRadarChart from '@/components/charts/ScoreRadarChart'
import PhotoUpload from '@/components/ui/PhotoUpload'
import StaffNoteSection from '@/components/ui/StaffNoteSection'
import type { StudentStatus, RiskLevel } from '@/types'

export default function StudentDetailPage() {
  const { studentId } = useParams<{ studentId: string }>()
  const navigate = useNavigate()
  const id = parseInt(studentId || '0')

  const { data: student, isLoading, isError } = useQuery({
    queryKey: ['student-detail', id],
    queryFn: () => studentsApi.get(id),
    enabled: !!id,
  })

  if (isLoading) return (
    <div className="p-6">
      <LoadingSpinner text="生徒データを読み込み中..." />
    </div>
  )

  if (isError || !student) return (
    <div className="p-6 text-center text-red-500">
      生徒データの取得に失敗しました
    </div>
  )

  // ScoreBarChart用にデータを変換
  const scoreTrendData = (() => {
    const sessions: Record<string, { test_id: string; test_name: string; test_date?: string; scores: Record<string, number> }> = {}
    student.test_scores.forEach((ts) => {
      if (!sessions[ts.test_id]) {
        sessions[ts.test_id] = {
          test_id: ts.test_id,
          test_name: ts.test_name || ts.test_id,
          test_date: ts.test_date,
          scores: {},
        }
      }
      sessions[ts.test_id].scores[ts.subject] = ts.raw_score
    })
    return Object.values(sessions).sort((a, b) => a.test_id.localeCompare(b.test_id))
  })()

  return (
    <div className="p-6 max-w-screen-xl mx-auto space-y-6">
      {/* 戻るボタン */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
      >
        <ArrowLeft size={16} />
        ダッシュボードに戻る
      </button>

      {/* ヘッダー */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <PhotoUpload studentId={student.id} photoData={student.photo_data} />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{student.name}</h1>
              <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
                <span>{gradeLabel(student.grade)}</span>
                {student.school && <span>• {student.school}</span>}
                {student.assigned_teacher_name && <span>• 担当: {student.assigned_teacher_name}</span>}
              </div>
            </div>
          </div>
          <StudentStatusBadge status={student.status as StudentStatus} />
        </div>

        {/* 基本情報グリッド */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-100">
          <InfoItem label="入会日" value={student.enrolled_at || '—'} />
          <InfoItem label="体験日" value={student.trial_at || '—'} />
          <InfoItem label="最終来室" value={student.last_visit || '—'} />
          <InfoItem
            label="出席率 (30日)"
            value={student.attendance_rate_30d !== undefined ? `${student.attendance_rate_30d.toFixed(0)}%` : '—'}
          />
        </div>

        {/* 受講講座 */}
        {student.enrollments.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <p className="text-xs text-gray-400 mb-2">受講講座</p>
            <div className="flex flex-wrap gap-2">
              {student.enrollments
                .filter((e) => !e.ended_at)
                .map((e) => (
                  <span key={e.id} className="text-xs bg-blue-50 text-blue-700 px-2.5 py-1 rounded-full border border-blue-200">
                    {e.course?.name || `講座 ${e.course_id}`}
                  </span>
                ))}
            </div>
          </div>
        )}

        {/* 志望校 */}
        {student.target_schools.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <p className="text-xs text-gray-400 mb-2">志望校</p>
            <div className="flex flex-wrap gap-2">
              {student.target_schools.map((ts) => (
                <span key={ts.id} className="text-xs bg-purple-50 text-purple-700 px-2.5 py-1 rounded-full border border-purple-200">
                  第{ts.priority}志望: {ts.school_name}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 2カラムレイアウト: 左 (成績・出欠) | 右 (コンタクト・支払い・営業) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左カラム (2/3) */}
        <div className="lg:col-span-2 space-y-6">
          {/* タイムライン */}
          <Section icon={Calendar} title="イベントタイムライン">
            {student.enrollment_events.length === 0 ? (
              <EmptyState text="イベント記録がありません" />
            ) : (
              <div className="space-y-3">
                {[...student.enrollment_events]
                  .sort((a, b) => new Date(b.occurred_at).getTime() - new Date(a.occurred_at).getTime())
                  .map((event) => (
                    <div key={event.id} className="flex items-start gap-3">
                      <div className="w-2 h-2 rounded-full bg-blue-400 mt-2 flex-shrink-0" />
                      <div>
                        <span className="text-sm font-medium text-gray-800">{event.event_type}</span>
                        <span className="text-xs text-gray-400 ml-2">
                          {new Date(event.occurred_at).toLocaleDateString('ja-JP')}
                        </span>
                        {event.note && <p className="text-xs text-gray-500 mt-0.5">{event.note}</p>}
                      </div>
                    </div>
                  ))}
              </div>
            )}
          </Section>

          {/* 成績グラフ */}
          <Section icon={TrendingUp} title="テスト成績推移">
            {scoreTrendData.length === 0 ? (
              <EmptyState text="テストデータがありません" />
            ) : (
              <div className="space-y-6">
                <ScoreBarChart data={scoreTrendData} />
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-3">最新テスト 科目バランス</p>
                  <ScoreRadarChart scores={student.test_scores} />
                </div>
              </div>
            )}
          </Section>

          {/* 出欠カレンダー */}
          <Section icon={Calendar} title="出欠カレンダー (直近3ヶ月)">
            {student.recent_attendances.length === 0 ? (
              <EmptyState text="出欠データがありません" />
            ) : (
              <AttendanceCalendar attendances={student.recent_attendances} months={3} />
            )}
          </Section>
        </div>

        {/* 右カラム (1/3) */}
        <div className="space-y-6">
          {/* リスクスコア */}
          {student.risk_score && (
            <Section icon={AlertTriangle} title="リスク・AI提案">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">リスクレベル</span>
                  <RiskBadge level={student.risk_score.risk_level as RiskLevel} />
                </div>
                <div className="text-sm text-gray-600">
                  出席率: <span className={student.risk_score.attendance_rate_30d < 60 ? 'text-red-600 font-medium' : 'text-gray-800'}>
                    {student.risk_score.attendance_rate_30d.toFixed(0)}%
                  </span>
                </div>
                {student.risk_score.factors.length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-gray-500 mb-1">要因</p>
                    <ul className="space-y-1">
                      {student.risk_score.factors.map((f, i) => (
                        <li key={i} className="text-xs text-red-600">• {f}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {student.risk_score.suggestions.length > 0 && (
                  <div className="bg-indigo-50 rounded-lg p-3">
                    <p className="text-xs font-medium text-indigo-600 mb-1.5">AI提案</p>
                    <ul className="space-y-1.5">
                      {student.risk_score.suggestions.map((s, i) => (
                        <li key={i} className="text-xs text-indigo-700">{i + 1}. {s}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </Section>
          )}

          {/* スタッフ記録 */}
          <Section icon={MessageSquare} title="スタッフ記録">
            <StaffNoteSection studentId={student.id} notes={student.staff_notes || []} />
          </Section>

          {/* 保護者コンタクト */}
          <Section icon={Phone} title="保護者コンタクト">
            {student.parent_contacts.length === 0 ? (
              <EmptyState text="コンタクト記録がありません" />
            ) : (
              <div className="space-y-3">
                {student.parent_contacts.slice(0, 5).map((c) => (
                  <div key={c.id} className="border-b border-gray-100 pb-3 last:border-0 last:pb-0">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-gray-700">{c.contact_type}</span>
                      <span className="text-xs text-gray-400">{new Date(c.occurred_at).toLocaleDateString('ja-JP')}</span>
                    </div>
                    {c.teacher_name && <p className="text-xs text-gray-500">{c.teacher_name}</p>}
                    {c.summary && <p className="text-xs text-gray-600 mt-1">{c.summary}</p>}
                  </div>
                ))}
              </div>
            )}
          </Section>

          {/* 支払い */}
          <Section icon={CreditCard} title="支払い状況">
            {student.payments.length === 0 ? (
              <EmptyState text="支払いデータがありません" />
            ) : (
              <div className="space-y-2">
                {student.payments.slice(0, 6).map((p) => (
                  <div key={p.id} className="flex items-center justify-between text-sm">
                    <div>
                      <span className="text-gray-700">{p.category}</span>
                      <span className="text-xs text-gray-400 ml-2">{p.paid_at || p.due_at}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-gray-800">¥{p.amount.toLocaleString()}</span>
                      <span className={`text-xs px-1.5 py-0.5 rounded ${p.status === 'paid' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                        {p.status === 'paid' ? '済' : '未'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Section>

          {/* 営業アクション */}
          <Section icon={Target} title="営業アクション">
            {student.sales_actions.length === 0 ? (
              <EmptyState text="アクション記録がありません" />
            ) : (
              <div className="space-y-2">
                {student.sales_actions.slice(0, 5).map((a) => (
                  <div key={a.id} className="flex items-start justify-between gap-2">
                    <div>
                      <p className="text-xs text-gray-700">{a.target_product || a.action_type}</p>
                      {a.note && <p className="text-xs text-gray-400 mt-0.5">{a.note}</p>}
                    </div>
                    <SalesStatusBadge status={a.status} />
                  </div>
                ))}
              </div>
            )}
          </Section>
        </div>
      </div>
    </div>
  )
}

// ===== ヘルパーコンポーネント =====

function Section({
  icon: Icon,
  title,
  children,
}: {
  icon: React.ComponentType<{ size?: number; className?: string }>
  title: string
  children: React.ReactNode
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
      <h2 className="flex items-center gap-2 text-sm font-semibold text-gray-800 mb-4">
        <Icon size={16} className="text-blue-500" />
        {title}
      </h2>
      {children}
    </div>
  )
}

function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-gray-400">{label}</p>
      <p className="text-sm font-medium text-gray-800 mt-0.5">{value}</p>
    </div>
  )
}

function EmptyState({ text }: { text: string }) {
  return (
    <p className="text-sm text-gray-400 text-center py-4">{text}</p>
  )
}
