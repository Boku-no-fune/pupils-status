/**
 * axiosクライアント設定
 * - JWTトークンを Authorization: Bearer ヘッダーに自動付与
 * - 401レスポンス時はログアウトしてログインページへリダイレクト
 */

import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

// 本番: VITE_API_BASE_URL を使用。開発時はvite.config.tsのproxyが処理する
const baseURL = import.meta.env.VITE_API_BASE_URL || ''

export const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// リクエストインターセプター: JWTトークンを自動付与
apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// レスポンスインターセプター: 401でログアウト
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().clearAuth()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
