import apiClient from './client'
import type { Prospect, ProspectFunnel } from '@/types'

export const prospectsApi = {
  list: async (): Promise<Prospect[]> => {
    const { data } = await apiClient.get('/api/prospects')
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
