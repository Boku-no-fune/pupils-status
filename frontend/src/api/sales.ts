import apiClient from './client'
import type { SalesAction } from '@/types'

export const salesApi = {
  listActions: async (params = {}): Promise<SalesAction[]> => {
    const { data } = await apiClient.get('/api/sales/actions', { params })
    return data
  },

  updateAction: async (id: number, payload: { status?: string; note?: string }) => {
    const { data } = await apiClient.patch(`/api/sales/actions/${id}`, payload)
    return data
  },

  getProgress: async (period?: string) => {
    const { data } = await apiClient.get('/api/sales/progress', {
      params: period ? { period } : {},
    })
    return data
  },

  getReport: async (period?: string) => {
    const { data } = await apiClient.get('/api/sales/report', {
      params: period ? { period } : {},
    })
    return data
  },
}
