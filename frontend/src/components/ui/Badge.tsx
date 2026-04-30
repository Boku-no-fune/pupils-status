/**
 * ステータスバッジコンポーネント
 */

import clsx from 'clsx'
import type { StudentStatus, RiskLevel } from '@/types'

// 生徒ステータスバッジ
const statusConfig: Record<StudentStatus, { label: string; className: string }> = {
  enrolled: { label: '在籍', className: 'bg-green-100 text-green-700 border-green-200' },
  trial: { label: '体験', className: 'bg-blue-100 text-blue-700 border-blue-200' },
  on_leave: { label: '休会', className: 'bg-yellow-100 text-yellow-700 border-yellow-200' },
  withdrawn: { label: '退会', className: 'bg-gray-100 text-gray-500 border-gray-200' },
}

export function StudentStatusBadge({ status }: { status: StudentStatus }) {
  const config = statusConfig[status] || { label: status, className: 'bg-gray-100 text-gray-500' }
  return (
    <span className={clsx('inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border', config.className)}>
      {config.label}
    </span>
  )
}

// リスクレベルバッジ
const riskConfig: Record<RiskLevel, { label: string; className: string }> = {
  high: { label: '高リスク', className: 'bg-red-100 text-red-700 border-red-200' },
  medium: { label: '中リスク', className: 'bg-orange-100 text-orange-700 border-orange-200' },
  low: { label: '低リスク', className: 'bg-green-100 text-green-700 border-green-200' },
}

export function RiskBadge({ level }: { level: RiskLevel }) {
  const config = riskConfig[level]
  return (
    <span className={clsx('inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border', config.className)}>
      {config.label}
    </span>
  )
}

// 営業アクションステータスバッジ
const actionStatusConfig: Record<string, { label: string; className: string }> = {
  pending: { label: '未着手', className: 'bg-gray-100 text-gray-500 border-gray-200' },
  in_progress: { label: 'アプローチ済', className: 'bg-blue-100 text-blue-700 border-blue-200' },
  signed_up: { label: '申込済', className: 'bg-green-100 text-green-700 border-green-200' },
  declined: { label: '辞退', className: 'bg-red-100 text-red-500 border-red-200' },
}

export function SalesStatusBadge({ status }: { status: string }) {
  const config = actionStatusConfig[status] || { label: status, className: 'bg-gray-100 text-gray-500' }
  return (
    <span className={clsx('inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border', config.className)}>
      {config.label}
    </span>
  )
}

// 出欠ステータスバッジ
const attendanceConfig: Record<string, { label: string; className: string }> = {
  present: { label: '出席', className: 'bg-green-100 text-green-700' },
  absent: { label: '欠席', className: 'bg-red-100 text-red-700' },
  late: { label: '遅刻', className: 'bg-yellow-100 text-yellow-700' },
  early_leave: { label: '早退', className: 'bg-orange-100 text-orange-700' },
}

export function AttendanceBadge({ status }: { status: string }) {
  const config = attendanceConfig[status] || { label: status, className: 'bg-gray-100 text-gray-500' }
  return (
    <span className={clsx('inline-flex items-center px-2 py-0.5 rounded text-xs font-medium', config.className)}>
      {config.label}
    </span>
  )
}
