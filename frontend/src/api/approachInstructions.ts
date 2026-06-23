import apiClient from './client'
import type { ApproachInstruction } from '@/types'

export const approachApi = {
  list: async (): Promise<ApproachInstruction[]> => {
    const { data } = await apiClient.get('/api/approach-instructions')
    return data
  },
  create: async (payload: {
    title: string; content: string; target_type: string; target_value?: string
    period?: string; pdf_data?: string; pdf_filename?: string
  }): Promise<ApproachInstruction> => {
    const { data } = await apiClient.post('/api/approach-instructions', payload)
    return data
  },
  remove: async (id: number) => {
    const { data } = await apiClient.delete(`/api/approach-instructions/${id}`)
    return data
  },
  getPdf: async (id: number): Promise<{ pdf_data: string; pdf_filename?: string }> => {
    const { data } = await apiClient.get(`/api/approach-instructions/${id}/pdf`)
    return data
  },
}
