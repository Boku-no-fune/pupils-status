/**
 * 統計サマリーカードコンポーネント
 */

import clsx from 'clsx'
import type { LucideIcon } from 'lucide-react'

interface StatCardProps {
  title: string
  value: string | number
  icon: LucideIcon
  iconColor?: string
  bgColor?: string
  suffix?: string
  description?: string
}

export default function StatCard({
  title,
  value,
  icon: Icon,
  iconColor = 'text-blue-600',
  bgColor = 'bg-blue-50',
  suffix,
  description,
}: StatCardProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-500 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900">
            {value}
            {suffix && <span className="text-base font-normal text-gray-500 ml-1">{suffix}</span>}
          </p>
          {description && <p className="text-xs text-gray-400 mt-1">{description}</p>}
        </div>
        <div className={clsx('w-10 h-10 rounded-lg flex items-center justify-center', bgColor)}>
          <Icon size={20} className={iconColor} />
        </div>
      </div>
    </div>
  )
}
