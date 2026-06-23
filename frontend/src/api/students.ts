import apiClient from './client'
import type { StudentListResponse, StudentDetail, StaffNote, VideoLessonLog, TeacherBrief, ActivityRecord } from '@/types'

export interface StudentListParams {
  status?: string
  grade?: number
  class_group_id?: number
  teacher_id?: number
  classroom_id?: number
  search?: string
  school_type?: string
  division?: string
  sort_by?: string
  sort_dir?: string
  show_all?: boolean
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

  listStaffNotesFiltered: async (id: number, params: { tag?: string; search?: string }): Promise<StaffNote[]> => {
    const { data } = await apiClient.get(`/api/students/${id}/staff-notes`, { params })
    return data
  },

  createStaffNote: async (id: number, payload: {
    note_type: string
    content: string
    tags?: string[]
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

  // 月別実施状況のポップアップ明細
  listActivities: async (id: number, month: string): Promise<ActivityRecord[]> => {
    const { data } = await apiClient.get(`/api/students/${id}/activities`, { params: { month } })
    return data
  },

  // ===== 特記事項 =====
  createSpecialNote: async (id: number, payload: { content: string; importance: string }) => {
    const { data } = await apiClient.post(`/api/students/${id}/special-notes`, payload)
    return data
  },
  deleteSpecialNote: async (id: number, noteId: number) => {
    const { data } = await apiClient.delete(`/api/students/${id}/special-notes/${noteId}`)
    return data
  },

  // ===== プロフィール定型メモ =====
  createProfileMemo: async (id: number, payload: { category: string; content: string }) => {
    const { data } = await apiClient.post(`/api/students/${id}/profile-memos`, payload)
    return data
  },
  deleteProfileMemo: async (id: number, memoId: number) => {
    const { data } = await apiClient.delete(`/api/students/${id}/profile-memos/${memoId}`)
    return data
  },

  // ===== 保護者要望・クレーム =====
  createParentRequest: async (id: number, payload: { request_type: string; content: string; status?: string }) => {
    const { data } = await apiClient.post(`/api/students/${id}/parent-requests`, payload)
    return data
  },
  updateParentRequest: async (id: number, reqId: number, status: string) => {
    const { data } = await apiClient.patch(`/api/students/${id}/parent-requests/${reqId}`, { status })
    return data
  },
  deleteParentRequest: async (id: number, reqId: number) => {
    const { data } = await apiClient.delete(`/api/students/${id}/parent-requests/${reqId}`)
    return data
  },

  // ===== 電話番号メモ =====
  createPhone: async (id: number, payload: { phone_number: string; memo?: string }) => {
    const { data } = await apiClient.post(`/api/students/${id}/phones`, payload)
    return data
  },
  updatePhoneMemo: async (id: number, phoneId: number, memo: string) => {
    const { data } = await apiClient.patch(`/api/students/${id}/phones/${phoneId}`, { memo })
    return data
  },
  deletePhone: async (id: number, phoneId: number) => {
    const { data } = await apiClient.delete(`/api/students/${id}/phones/${phoneId}`)
    return data
  },

  // ===== 試験成績の手入力 =====
  createTestScore: async (id: number, payload: {
    test_id: string; test_name?: string; test_type?: string
    subject: string; raw_score: number; rank?: number; deviation_value?: number; test_date?: string
  }) => {
    const { data } = await apiClient.post(`/api/students/${id}/test-scores`, payload)
    return data
  },
  deleteTestScore: async (id: number, scoreId: number) => {
    const { data } = await apiClient.delete(`/api/students/${id}/test-scores/${scoreId}`)
    return data
  },

  // ===== 英検・漢検 =====
  createExamCert: async (id: number, payload: {
    exam_type: string; level: string; score?: number; result?: string; exam_date?: string
  }) => {
    const { data } = await apiClient.post(`/api/students/${id}/exam-certs`, payload)
    return data
  },
  deleteExamCert: async (id: number, certId: number) => {
    const { data } = await apiClient.delete(`/api/students/${id}/exam-certs/${certId}`)
    return data
  },

  // ===== 担当講師の追加・削除 =====
  addTeacher: async (id: number, userId: number): Promise<{ teachers: TeacherBrief[] }> => {
    const { data } = await apiClient.post(`/api/students/${id}/teachers`, { user_id: userId })
    return data
  },
  removeTeacher: async (id: number, userId: number): Promise<{ teachers: TeacherBrief[] }> => {
    const { data } = await apiClient.delete(`/api/students/${id}/teachers/${userId}`)
    return data
  },
}
