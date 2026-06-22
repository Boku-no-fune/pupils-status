/**
 * ダッシュボードメインページ
 * 5タブ構成: 生徒一覧 / 出欠・成績 / 営業目標 / リスク・AI提案 / 学習進捗
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Users, TrendingUp, Target, AlertTriangle, BookOpen } from 'lucide-react'
import clsx from 'clsx'
import { dashboardApi } from '@/api/dashboard'
import StatCard from '@/components/ui/StatCard'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import StatStudentsModal from '@/components/dashboard/StatStudentsModal'
import StudentListTab from './tabs/StudentListTab'
import AttendanceScoreTab from './tabs/AttendanceScoreTab'
import SalesTab from './tabs/SalesTab'
import RiskTab from './tabs/RiskTab'
import LearningProgressTab from './tabs/LearningProgressTab'

type StatKind = 'on_leave' | 'high_risk' | 'low_attendance'
const STAT_TITLES: Record<StatKind, string> = {
  on_leave: '休会中の生徒',
  high_risk: '高リスク生徒（出席率60%未満）',
  low_attendance: '出席率が低い生徒',
}

const TABS = [
  { id: 'students', label: '生徒一覧・ステータス', icon: Users },
  { id: 'charts', label: '出欠・成績グラフ', icon: TrendingUp },
  { id: 'sales', label: '営業目標・アプローチ', icon: Target },
  { id: 'risk', label: 'リスク・AI提案', icon: AlertTriangle },
  { id: 'learning', label: '学習進捗', icon: BookOpen },
]

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState('students')
  const [statModal, setStatModal] = useState<StatKind | null>(null)

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => dashboardApi.stats(),
  })

  return (
    <div className="p-6 max-w-screen-xl mx-auto">
      {/* ページヘッダー */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">ダッシュボード</h1>
        <p className="text-sm text-gray-500 mt-1">生徒の状況・営業進捗・リスク管理</p>
      </div>

      {/* サマリーカード */}
      {statsLoading ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-xl border border-gray-200 p-5 h-24 animate-pulse" />
          ))}
        </div>
      ) : stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <StatCard
            title="在籍生徒"
            value={stats.total_enrolled + stats.total_trial}
            suffix="名"
            icon={Users}
            iconColor="text-blue-600"
            bgColor="bg-blue-50"
            description={`体験中 ${stats.total_trial} 名含む`}
          />
          <StatCard
            title="平均出席率"
            value={stats.avg_attendance_rate}
            suffix="%"
            icon={TrendingUp}
            iconColor="text-green-600"
            bgColor="bg-green-50"
            description="直近30日間"
            onClick={() => setStatModal('low_attendance')}
          />
          <StatCard
            title="休会中"
            value={stats.total_on_leave}
            suffix="名"
            icon={Users}
            iconColor="text-yellow-600"
            bgColor="bg-yellow-50"
            onClick={() => setStatModal('on_leave')}
          />
          <StatCard
            title="高リスク生徒"
            value={stats.high_risk_count}
            suffix="名"
            icon={AlertTriangle}
            iconColor="text-red-600"
            bgColor="bg-red-50"
            description="要フォロー"
            onClick={() => setStatModal('high_risk')}
          />
        </div>
      )}

      {/* タブナビゲーション */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="flex border-b border-gray-200 overflow-x-auto">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={clsx(
                'flex items-center gap-2 px-5 py-4 text-sm font-medium whitespace-nowrap transition-colors border-b-2 -mb-px',
                activeTab === tab.id
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              )}
            >
              <tab.icon size={16} />
              {tab.label}
            </button>
          ))}
        </div>

        {/* タブコンテンツ */}
        <div className="p-6">
          {activeTab === 'students' && <StudentListTab />}
          {activeTab === 'charts' && <AttendanceScoreTab />}
          {activeTab === 'sales' && <SalesTab />}
          {activeTab === 'risk' && <RiskTab />}
          {activeTab === 'learning' && <LearningProgressTab />}
        </div>
      </div>

      {/* サマリーカードのドリルダウン */}
      {statModal && (
        <StatStudentsModal
          kind={statModal}
          title={STAT_TITLES[statModal]}
          onClose={() => setStatModal(null)}
        />
      )}
    </div>
  )
}
