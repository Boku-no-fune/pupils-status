/**
 * 生徒詳細ページ
 * 上段: 基本情報 + 特記事項
 * 左カラム: タイムライン / 試験成績(折れ線・種別切替・手入力) / 出欠カレンダー / 映像視聴履歴
 * 右カラム: リスク / スタッフ記録 / プロフィール / 要望クレーム / 英検漢検 / 紹介 / コンタクト / 支払 / 営業
 */

import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import type { LucideIcon } from 'lucide-react'
import {
  ArrowLeft, Calendar, TrendingUp, Phone, CreditCard, Target, AlertTriangle,
  MessageSquare, Award, Share2, Video, ClipboardList, BookUser,
} from 'lucide-react'
import { studentsApi } from '@/api/students'
import { gradeLabel } from '@/components/ui/GradeLabel'
import { StudentStatusBadge, SalesStatusBadge, RiskBadge } from '@/components/ui/Badge'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import AttendanceCalendar from '@/components/charts/AttendanceCalendar'
import ScoreRadarChart from '@/components/charts/ScoreRadarChart'
import PhotoUpload from '@/components/ui/PhotoUpload'
import StaffNoteSection from '@/components/ui/StaffNoteSection'
import SpecialNotesSection from '@/components/students/SpecialNotesSection'
import TestScoreSection from '@/components/students/TestScoreSection'
import {
  PhoneListSection, TeacherAssignSection, ProfileMemoSection,
  ParentRequestSection, ExamCertSection, ReferralSection, VideoHistorySection,
} from '@/components/students/StudentDetailSections'
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
    <div className="p-6"><LoadingSpinner text="生徒データを読み込み中..." /></div>
  )

  if (isError || !student) return (
    <div className="p-6 text-center text-red-500">生徒データの取得に失敗しました</div>
  )

  return (
    <div className="p-6 max-w-screen-xl mx-auto space-y-6">
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
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold text-gray-900">{student.name}</h1>
                {student.class_group && (
                  <span className="text-xs bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-full border border-indigo-200">
                    {student.class_group.name}（{student.class_group.level}）
                  </span>
                )}
              </div>
              <div className="flex items-center gap-3 mt-1 text-sm text-gray-500 flex-wrap">
                <span>{gradeLabel(student.grade)}</span>
                {student.gender && <span>• {student.gender}</span>}
                {student.school && <span>• {student.school}{student.school_type ? `（${student.school_type}）` : ''}</span>}
                {student.member_number && <span className="font-mono text-xs">• 会員番号 {student.member_number}</span>}
              </div>
            </div>
          </div>
          <StudentStatusBadge status={student.status as StudentStatus} />
        </div>

        {/* 基本情報グリッド */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-100">
          <InfoItem label="保護者氏名" value={student.parent_name || '—'} />
          <InfoItem label="入会日" value={student.enrolled_at || '—'} />
          <InfoItem label="最終来室" value={student.last_visit || '—'} />
          <InfoItem
            label="出席率 (30日)"
            value={student.attendance_rate_30d !== undefined ? `${student.attendance_rate_30d.toFixed(0)}%` : '—'}
          />
          <InfoItem label="兄弟姉妹" value={student.sibling_info || '—'} />
        </div>

        {/* 電話番号 + 担当講師 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 pt-4 border-t border-gray-100">
          <div>
            <p className="text-xs text-gray-400 mb-2">電話番号</p>
            <PhoneListSection studentId={student.id} phones={student.phones} />
          </div>
          <div>
            <p className="text-xs text-gray-400 mb-2">担当講師</p>
            <TeacherAssignSection studentId={student.id} teachers={student.teachers || []} />
          </div>
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

      {/* 特記事項 (最上段コンテナ直下) */}
      <SpecialNotesSection studentId={student.id} notes={student.special_notes} />

      {/* 2カラムレイアウト */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左カラム */}
        <div className="lg:col-span-2 space-y-6">
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

          <Section icon={TrendingUp} title="試験成績">
            {student.test_scores.length === 0 ? (
              <EmptyState text="テストデータがありません" />
            ) : (
              <div className="space-y-6">
                <TestScoreSection studentId={student.id} scores={student.test_scores} />
                <div className="pt-2 border-t border-gray-100">
                  <p className="text-sm font-medium text-gray-600 mb-3">最新テスト 科目バランス</p>
                  <ScoreRadarChart scores={student.test_scores} />
                </div>
              </div>
            )}
          </Section>

          <Section icon={Calendar} title="出欠カレンダー (直近3ヶ月)">
            {student.recent_attendances.length === 0 ? (
              <EmptyState text="出欠データがありません" />
            ) : (
              <AttendanceCalendar attendances={student.recent_attendances} months={3} />
            )}
          </Section>

          <Section icon={Video} title="映像授業 視聴履歴">
            <VideoHistorySection logs={student.video_lesson_logs} />
          </Section>
        </div>

        {/* 右カラム */}
        <div className="space-y-6">
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

          <Section icon={MessageSquare} title="スタッフ記録">
            <StaffNoteSection studentId={student.id} notes={student.staff_notes || []} />
          </Section>

          <Section icon={BookUser} title="プロフィールメモ">
            <ProfileMemoSection studentId={student.id} memos={student.profile_memos} />
          </Section>

          <Section icon={ClipboardList} title="保護者 要望・クレーム">
            <ParentRequestSection studentId={student.id} requests={student.parent_requests} />
          </Section>

          <Section icon={Award} title="英検・漢検">
            <ExamCertSection studentId={student.id} certs={student.exam_certifications} />
          </Section>

          <Section icon={Share2} title="紹介・被紹介履歴">
            <ReferralSection made={student.referrals_made} received={student.referrals_received} />
          </Section>

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
  icon: LucideIcon
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
  return <p className="text-sm text-gray-400 text-center py-4">{text}</p>
}
