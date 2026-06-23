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
  ActivityMatrix,
  MapData,
} from '@/types'

export const dashboardApi = {
  stats: async (showAll = false): Promise<DashboardStats> => {
    const { data } = await apiClient.get('/api/dashboard/stats', { params: { show_all: showAll } })
    return data
  },

  studentList: async (params = {}): Promise<StudentListResponse> => {
    const { data } = await apiClient.get('/api/dashboard/student-list', { params })
    return data
  },

  statStudents: async (kind: string, showAll = false): Promise<StatStudent[]> => {
    const { data } = await apiClient.get('/api/dashboard/stat-students', {
      params: { kind, show_all: showAll },
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

  riskStudents: async (showAll = false): Promise<RiskStudent[]> => {
    const { data } = await apiClient.get('/api/dashboard/risk-students', {
      params: { show_all: showAll },
    })
    return data
  },

  salesProgress: async (period?: string): Promise<SalesProgress[]> => {
    const { data } = await apiClient.get('/api/dashboard/sales-progress', {
      params: period ? { period } : {},
    })
    return data
  },

  learningProgress: async (showAll = false): Promise<LearningProgress> => {
    const { data } = await apiClient.get('/api/dashboard/learning-progress', {
      params: { show_all: showAll },
    })
    return data
  },

  activityMatrix: async (months = 6, showAll = false): Promise<ActivityMatrix> => {
    const { data } = await apiClient.get('/api/dashboard/activity-matrix', { params: { months, show_all: showAll } })
    return data
  },

  mapData: async (showAll = false): Promise<MapData> => {
    const { data } = await apiClient.get('/api/dashboard/map-data', { params: { show_all: showAll } })
    return data
  },
}
