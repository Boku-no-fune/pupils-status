/**
 * 認証ストア (Zustand + localStorage永続化)
 * JWTトークンとユーザー情報を管理する
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'

interface AuthState {
  token: string | null
  user: User | null
  // アクション
  setAuth: (token: string, user: User) => void
  clearAuth: () => void
  isAuthenticated: () => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,

      setAuth: (token, user) => {
        set({ token, user })
      },

      clearAuth: () => {
        set({ token: null, user: null })
      },

      isAuthenticated: () => {
        return !!get().token && !!get().user
      },
    }),
    {
      name: 'pupils-status-auth',  // localStorageのキー名
    }
  )
)
