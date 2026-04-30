/**
 * アプリケーション共通レイアウト
 * サイドバー + メインコンテンツエリア
 */

import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'

export default function AppLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* サイドバー */}
      <Sidebar />

      {/* メインコンテンツ */}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  )
}
