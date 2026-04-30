import apiClient from './client'
import type { StudentListResponse, StudentDetail } from '@/types'

export interface StudentListParams {
  status?: string
  grade?: number
  teacher_id?: number
  classroom_id?: number
  search?: string
  page?: number
  per_page?: number
}

export const studentsApi = {
  list: async (params: StudentListParams = {}): Promise<StudentListResponse> => {
    const { data } = await apiClient.get('/api/students', { params })
    return data
  },

  get: async (id: number): Promise<StudentDetail> => {
    const { data } = await apiClient.get(`/api/students/${id}`)
    return data
  },

  update: async (id: number, payload: Record<string, unknown>) => {
    const { data } = await apiClient.patch(`/api/students/${id}`, payload)
    return data
  },
}
