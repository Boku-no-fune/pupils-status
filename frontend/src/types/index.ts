/**
 * TypeScript型定義 — バックエンドのPydanticスキーマと対応
 */

// ===== ユーザー・認証 =====
export type UserRole = 'admin' | 'room_manager' | 'teacher' | 'parttime'

export interface User {
  id: number
  name: string
  email: string
  role: UserRole
  classroom_id?: number
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

// ===== 生徒 =====
export type StudentStatus = 'enrolled' | 'trial' | 'on_leave' | 'withdrawn'
export type RiskLevel = 'high' | 'medium' | 'low'

export interface GradeChange {
  subject: string
  change: number
  direction: 'up' | 'down' | 'stable'
}

export interface TeacherBrief {
  id: number
  name: string
  role?: string
}

export interface ClassGroupBrief {
  id: number
  name: string
  level: string
  grade: number
}

export interface Student {
  id: number
  name: string
  member_number?: string
  grade: number
  school?: string
  school_type?: string   // 公立 / 私立 / 国立
  status: StudentStatus
  enrolled_at?: string
  trial_at?: string
  withdrawn_at?: string
  assigned_teacher_id?: number
  assigned_teacher_name?: string
  classroom_id?: number
  // クラス・部門・複数担当
  class_label?: string
  divisions?: string[]
  teachers?: TeacherBrief[]
  // ダッシュボード集計フィールド
  last_visit?: string
  attendance_rate_30d?: number
  recent_grade_change?: GradeChange
}

export interface EnrollmentEvent {
  id: number
  event_type: string
  occurred_at: string
  note?: string
}

export interface Enrollment {
  id: number
  course_id: number
  course?: { id: number; name: string; subject?: string }
  started_at: string
  ended_at?: string
  change_type: string
}

export interface Attendance {
  id: number
  class_date: string
  status: 'present' | 'absent' | 'late' | 'early_leave'
  note?: string
  makeup_type?: string   // 映像視聴 / 振替
  makeup_note?: string
}

export interface TestScore {
  id: number
  test_id: string
  test_name?: string
  test_type?: string   // 塾内試験A/B, 業者模試A/B, 学校定期テスト, その他
  subject: string
  raw_score: number
  rank?: number
  deviation_value?: number
  test_date?: string
}

export interface TargetSchool {
  id: number
  school_name: string
  priority: number
  recorded_at?: string
}

export interface SchoolGrade {
  id: number
  term: string
  subject: string
  score?: number
  grade_notation?: string
}

export interface Payment {
  id: number
  amount: number
  paid_at?: string
  due_at?: string
  category: string
  status: 'paid' | 'pending'
}

export interface ParentContact {
  id: number
  contact_type: string
  occurred_at: string
  summary?: string
  teacher_id?: number
  teacher_name?: string
}

export interface SalesAction {
  id: number
  action_type: string
  target_product?: string
  status: 'pending' | 'in_progress' | 'signed_up' | 'declined'
  note?: string
  actioned_at?: string
  assigned_to?: number
  assigned_teacher_name?: string
  student_id?: number
  student_name?: string
}

export interface RiskScore {
  risk_level: RiskLevel
  attendance_rate_30d: number
  score_trend: 'declining' | 'stable' | 'improving'
  factors: string[]
  suggestions: string[]
}

export interface StaffNote {
  id: number
  note_type: string
  content: string
  tags?: string[]
  occurred_at: string
  teacher_id?: number
  teacher_name?: string
}

// ===== 生徒詳細の追加情報 =====
export interface StudentPhone {
  id: number
  phone_number: string
  memo?: string
  position: number
}

export interface SpecialNote {
  id: number
  content: string
  importance: '高' | '中' | '低'
  created_at?: string
}

export interface ProfileMemo {
  id: number
  category: string
  content: string
  created_at?: string
}

export interface ParentRequest {
  id: number
  request_type: '要望' | 'クレーム'
  content: string
  status: '対応中' | '対応済'
  occurred_at: string
}

export interface ExamCertification {
  id: number
  exam_type: '英検' | '漢検'
  level: string
  score?: number
  result: '合格' | '不合格' | '受験予定'
  exam_date?: string
}

export interface ReferralMade {
  id: number
  referred_student_id?: number
  referred_name?: string
  occurred_at?: string
  note?: string
}

export interface ReferralReceived {
  id: number
  referrer_student_id?: number
  referrer_name?: string
  occurred_at?: string
  note?: string
}

export interface VideoLessonLog {
  id: number
  lesson_name: string
  lesson_category?: string
  viewed_at: string
  duration_minutes: number
  completion_rate?: number
  source_system?: string
}

export interface StudentDetail extends Student {
  photo_data?: string
  gender?: string
  parent_name?: string
  sibling_info?: string
  class_group_id?: number
  class_group?: ClassGroupBrief
  enrollment_events: EnrollmentEvent[]
  enrollments: Enrollment[]
  recent_attendances: Attendance[]
  test_scores: TestScore[]
  target_schools: TargetSchool[]
  school_grades: SchoolGrade[]
  parent_contacts: ParentContact[]
  payments: Payment[]
  sales_actions: SalesAction[]
  risk_score?: RiskScore
  staff_notes: StaffNote[]
  video_lesson_logs: VideoLessonLog[]
  phones: StudentPhone[]
  special_notes: SpecialNote[]
  profile_memos: ProfileMemo[]
  parent_requests: ParentRequest[]
  exam_certifications: ExamCertification[]
  referrals_made: ReferralMade[]
  referrals_received: ReferralReceived[]
}

// ===== ダッシュボード =====
export interface DashboardStats {
  total_enrolled: number
  total_trial: number
  total_on_leave: number
  total_withdrawn: number
  high_risk_count: number
  avg_attendance_rate: number
}

export interface AttendanceTrendPoint {
  month: string
  present_count: number
  absent_count: number
  late_count: number
  rate: number
}

export interface ScoreTrendPoint {
  test_id: string
  test_name: string
  test_date?: string
  scores: Record<string, number>
}

export interface SalesProgress {
  goal_id: number
  goal_type: string
  target_product?: string
  target_count: number
  period: string
  signed_up: number
  in_progress: number
  declined: number
  not_started: number
  progress_pct: number
}

export interface RiskStudent {
  student_id: number
  student_name: string
  grade: number
  status: StudentStatus
  risk_level: RiskLevel
  attendance_rate_30d: number
  score_trend: string
  factors: string[]
  suggestions: string[]
  study_plan?: string
}

export interface StudentListResponse {
  total: number
  page: number
  per_page: number
  students: Student[]
}

export interface ClassInfo {
  id: number
  name: string
  grade: number
  level: string
  student_count: number
  teachers: TeacherBrief[]
}

export interface StatStudent {
  id: number
  name: string
  grade: number
  status: StudentStatus
  class_label?: string
  attendance_rate_30d: number
  assigned_teacher_name?: string
}

// ===== 月別実施状況 =====
export interface ActivityCell {
  month: string
  staff: number
  contact: number
  total: number
}
export interface ActivityRow {
  student_id: number
  student_name: string
  grade: number
  class_label?: string
  cells: ActivityCell[]
  total: number
}
export interface ActivityMatrix {
  months: string[]
  rows: ActivityRow[]
}
export interface ActivityRecord {
  kind: string       // スタッフ記録 / 保護者アプローチ
  type: string
  content?: string
  occurred_at: string
  teacher_name?: string
}

// ===== 未入会(見込み)生徒 =====
export interface ProspectStage {
  stage: string
  id?: number
  status: '未対応' | '対応中' | '完了'
  memo?: string
  occurred_at?: string
}
export interface Prospect {
  id: number
  name: string
  grade?: number
  school?: string
  source?: string
  status: string
  assigned_teacher_name?: string
  first_contact_at?: string
  stages: ProspectStage[]
}
export interface ProspectFunnelStage {
  stage: string
  未対応: number
  対応中: number
  完了: number
  total: number
}
export interface ProspectFunnel {
  total_prospects: number
  stages: ProspectFunnelStage[]
}

// ===== 地図 =====
export interface MapStudent {
  id: number
  name: string
  grade: number
  school?: string
  address?: string
  home_lat: number
  home_lng: number
  school_lat?: number
  school_lng?: number
  class_label?: string
}
export interface MapSchool {
  name: string
  lat: number
  lng: number
  count: number
}
export interface MapData {
  classroom: { name: string; lat: number; lng: number }
  students: MapStudent[]
  schools: MapSchool[]
}

// ===== 学習進捗 =====
export interface VideoMonthlyPoint {
  month: string
  total_minutes: number
  view_count: number
}

export interface VideoCategoryPoint {
  category: string
  total_minutes: number
  view_count: number
}

export interface HomeworkSummaryItem {
  student_id: number
  student_name: string
  grade: number
  total: number
  submitted: number
  submission_rate: number
}

export interface LearningProgress {
  video_monthly: VideoMonthlyPoint[]
  video_by_category: VideoCategoryPoint[]
  homework_summary: HomeworkSummaryItem[]
}
