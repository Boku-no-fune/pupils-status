import apiClient from './client'
import type {
  DashboardStats,
  AttendanceTrendPoint,
  ScoreTrendPoint,
  SalesProgress,
  RiskStudent,
  StudentListResponse,
  LearningProgress,
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

  attendanceTrend: async (months = 6, classroomId?: number): Promise<AttendanceTrendPoint[]> => {
    const { data } = await apiClient.get('/api/dashboard/attendance-trend', {
      params: { months, classroom_id: classroomId },
    })
    return data
  },

  scoreTrend: async (months = 6, classroomId?: number): Promise<ScoreTrendPoint[]> => {
    const { data } = await apiClient.get('/api/dashboard/score-trend', {
      params: { months, classroom_id: classroomId },
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
