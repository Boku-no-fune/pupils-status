/**
 * アプリケーションルーティング
 * ロール別ガードを適用した React Router v6 構成
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import AppLayout from '@/components/layout/AppLayout'
import LoginPage from '@/pages/LoginPage'
import DashboardPage from '@/pages/dashboard/DashboardPage'
import StudentDetailPage from '@/pages/students/StudentDetailPage'
import ProspectDetailPage from '@/pages/prospects/ProspectDetailPage'

// 認証ガード
function RequireAuth({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated())
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  return <>{children}</>
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* ログインページ */}
        <Route path="/login" element={<LoginPage />} />

        {/* 認証が必要なページ */}
        <Route
          path="/"
          element={
            <RequireAuth>
              <AppLayout />
            </RequireAuth>
          }
        >
          {/* デフォルトはダッシュボードへリダイレクト */}
          <Route index element={<Navigate to="/dashboard" replace />} />

          {/* ダッシュボード */}
          <Route path="dashboard" element={<DashboardPage />} />

          {/* 生徒詳細 */}
          <Route path="students/:studentId" element={<StudentDetailPage />} />

          {/* 未入会生徒 詳細 */}
          <Route path="prospects/:prospectId" element={<ProspectDetailPage />} />
        </Route>

        {/* 未知のパスはダッシュボードへ */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
