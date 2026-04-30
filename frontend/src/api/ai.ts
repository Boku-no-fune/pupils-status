import apiClient from './client'
import type { RiskScore } from '@/types'

export const aiApi = {
  getRiskAnalysis: async (studentId: number): Promise<RiskScore & { study_plan?: string }> => {
    const { data } = await apiClient.get(`/api/ai/risk/${studentId}`)
    return data
  },
}
