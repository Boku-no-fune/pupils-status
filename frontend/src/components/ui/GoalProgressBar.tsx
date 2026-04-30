/**
 * 営業目標進捗バーコンポーネント
 */

import clsx from 'clsx'

interface Props {
  current: number
  target: number
  label?: string
}

export default function GoalProgressBar({ current, target, label }: Props) {
  const pct = target > 0 ? Math.min((current / target) * 100, 100) : 0
  const barColor =
    pct >= 80 ? 'bg-green-500' : pct >= 50 ? 'bg-yellow-500' : 'bg-red-500'

  return (
    <div className="space-y-2">
      {label && (
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">{label}</span>
          <span className="font-semibold text-gray-900">
            {current} / {target} 名 ({pct.toFixed(0)}%)
          </span>
        </div>
      )}
      <div className="w-full h-4 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={clsx('h-full rounded-full transition-all duration-500', barColor)}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
