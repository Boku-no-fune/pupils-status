import apiClient from './client'
import type { StudentListResponse, StudentDetail, StaffNote, VideoLessonLog } from '@/types'

export interface StudentListParams {
  status?: string
  grade?: number
  teacher_id?: number
  classroom_id?: number
  search?: string
  school_type?: string
  division?: string
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

  uploadPhoto: async (id: number, photoData: string | null) => {
    const { data } = await apiClient.put(`/api/students/${id}/photo`, { photo_data: photoData })
    return data
  },

  // スタッフ記録
  listStaffNotes: async (id: number): Promise<StaffNote[]> => {
    const { data } = await apiClient.get(`/api/students/${id}/staff-notes`)
    return data
  },

  createStaffNote: async (id: number, payload: {
    note_type: string
    content: string
    occurred_at: string
  }) => {
    const { data } = await apiClient.post(`/api/students/${id}/staff-notes`, payload)
    return data
  },

  deleteStaffNote: async (studentId: number, noteId: number) => {
    const { data } = await apiClient.delete(`/api/students/${studentId}/staff-notes/${noteId}`)
    return data
  },

  // 映像授業ログ
  listVideoLogs: async (id: number): Promise<VideoLessonLog[]> => {
    const { data } = await apiClient.get(`/api/students/${id}/video-logs`)
    return data
  },
}
