import apiClient from './client'
import type {
  DashboardStats,
  AttendanceTrendPoint,
  ScoreTrendPoint,
  SalesProgress,
  RiskStudent,
  StudentListResponse,
  LearningProgress,
  ClassInfo,
  StatStudent,
  TeacherBrief,
} from '@/types'

export const dashboardApi = {
  stats: async (classroomId?: number): Promise<DashboardStats> => {
    const { data } = await apiClient.get('/api/dashboard/stats', {
      params: classroomId ? { classroom_id: classroomId } : {},
    })
    return data
  },

  studentList: async (params = {}): Promise<StudentListResponse> => {
    const { data } = await apiClient.get('/api/dashboard/student-list', { params })
    return data
  },

  statStudents: async (kind: string, classroomId?: number): Promise<StatStudent[]> => {
    const { data } = await apiClient.get('/api/dashboard/stat-students', {
      params: { kind, classroom_id: classroomId },
    })
    return data
  },

  classes: async (): Promise<ClassInfo[]> => {
    const { data } = await apiClient.get('/api/dashboard/classes')
    return data
  },

  teachers: async (): Promise<TeacherBrief[]> => {
    const { data } = await apiClient.get('/api/dashboard/teachers')
    return data
  },

  attendanceTrend: async (months = 6, classGroupId?: number): Promise<AttendanceTrendPoint[]> => {
    const { data } = await apiClient.get('/api/dashboard/attendance-trend', {
      params: { months, class_group_id: classGroupId },
    })
    return data
  },

  scoreTrend: async (months = 6, classGroupId?: number, testType?: string): Promise<ScoreTrendPoint[]> => {
    const { data } = await apiClient.get('/api/dashboard/score-trend', {
      params: { months, class_group_id: classGroupId, test_type: testType },
    })
    return data
  },

  riskStudents: async (classroomId?: number): Promise<RiskStudent[]> => {
    const { data } = await apiClient.get('/api/dashboard/risk-students', {
      params: classroomId ? { classroom_id: classroomId } : {},
    })
    return data
  },

  salesProgress: async (period?: string): Promise<SalesProgress[]> => {
    const { data } = await apiClient.get('/api/dashboard/sales-progress', {
      params: period ? { period } : {},
    })
    return data
  },

  learningProgress: async (classroomId?: number): Promise<LearningProgress> => {
    const { data } = await apiClient.get('/api/dashboard/learning-progress', {
      params: classroomId ? { classroom_id: classroomId } : {},
    })
    return data
  },
}
