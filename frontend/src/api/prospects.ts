import apiClient from './client'
import type { Prospect, ProspectFunnel, ProspectDetail } from '@/types'

export const prospectsApi = {
  list: async (): Promise<Prospect[]> => {
    const { data } = await apiClient.get('/api/prospects')
    return data
  },

  get: async (id: number): Promise<ProspectDetail> => {
    const { data } = await apiClient.get(`/api/prospects/${id}`)
    return data
  },

  createNote: async (id: number, payload: { note_type: string; content: string }) => {
    const { data } = await apiClient.post(`/api/prospects/${id}/staff-notes`, payload)
    return data
  },

  deleteNote: async (id: number, noteId: number) => {
    const { data } = await apiClient.delete(`/api/prospects/${id}/staff-notes/${noteId}`)
    return data
  },

  funnel: async (): Promise<ProspectFunnel> => {
    const { data } = await apiClient.get('/api/prospects/funnel')
    return data
  },

  upsertStage: async (prospectId: number, payload: { stage: string; status: string; memo?: string }) => {
    const { data } = await apiClient.post(`/api/prospects/${prospectId}/stages`, payload)
    return data
  },
}
