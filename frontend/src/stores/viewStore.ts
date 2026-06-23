/**
 * 全タブ共通の表示フィルタ状態
 * 講師ログイン時、既定は担当生徒のみ (showAll=false)。トグルで全生徒表示。
 */
import { create } from 'zustand'

interface ViewState {
  showAll: boolean
  setShowAll: (v: boolean) => void
}

export const useViewStore = create<ViewState>((set) => ({
  showAll: false,
  setShowAll: (v) => set({ showAll: v }),
}))
