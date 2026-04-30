import apiClient from './client'
import type { TokenResponse } from '@/types'

export const authApi = {
  login: async (email: string, password: string): Promise<TokenResponse> => {
    const { data } = await apiClient.post<TokenResponse>('/api/auth/login', { email, password })
    return data
  },

  me: async () => {
    const { data } = await apiClient.get('/api/auth/me')
    return data
  },
}
