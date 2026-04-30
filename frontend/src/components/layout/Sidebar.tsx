/**
 * サイドバーナビゲーション
 * ロールに応じてメニュー項目を制御する
 */

import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  TrendingUp,
  AlertTriangle,
  LogOut,
  GraduationCap,
} from 'lucide-react'
import clsx from 'clsx'
import { useAuthStore } from '@/stores/authStore'

const navItems = [
  {
    to: '/dashboard',
    icon: LayoutDashboard,
    label: 'ダッシュボード',
    roles: ['admin', 'room_manager', 'teacher', 'parttime'],
  },
]

export default function Sidebar() {
  const { user, clearAuth } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    clearAuth()
    navigate('/login')
  }

  const roleLabel: Record<string, string> = {
    admin: '管理者',
    room_manager: '教室長',
    teacher: '講師',
    parttime: 'アルバイト',
  }

  return (
    <aside className="w-64 bg-gray-900 text-white flex flex-col h-screen sticky top-0">
      {/* ロゴ */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-gray-700">
        <div className="w-9 h-9 bg-blue-500 rounded-lg flex items-center justify-center">
          <GraduationCap size={20} />
        </div>
        <div>
          <div className="text-sm font-bold text-white">学習塾CRM</div>
          <div className="text-xs text-gray-400">校務管理システム</div>
        </div>
      </div>

      {/* ユーザー情報 */}
      <div className="px-4 py-4 border-b border-gray-700">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-sm font-bold">
            {user?.name?.charAt(0) || 'U'}
          </div>
          <div>
            <div className="text-sm font-medium text-white truncate max-w-[140px]">{user?.name}</div>
            <div className="text-xs text-gray-400">{roleLabel[user?.role || ''] || user?.role}</div>
          </div>
        </div>
      </div>

      {/* ナビゲーション */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems
          .filter((item) => item.roles.includes(user?.role || ''))
          .map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors',
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                )
              }
            >
              <item.icon size={18} />
              {item.label}
            </NavLink>
          ))}
      </nav>

      {/* ログアウト */}
      <div className="p-3 border-t border-gray-700">
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
        >
          <LogOut size={18} />
          ログアウト
        </button>
      </div>
    </aside>
  )
}
