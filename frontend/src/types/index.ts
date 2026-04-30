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

export interface Student {
  id: number
  name: string
  grade: number
  school?: string
  status: StudentStatus
  enrolled_at?: string
  trial_at?: string
  withdrawn_at?: string
  assigned_teacher_id?: number
  assigned_teacher_name?: string
  classroom_id?: number
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
}

export interface TestScore {
  id: number
  test_id: string
  test_name?: string
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

export interface StudentDetail extends Student {
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
