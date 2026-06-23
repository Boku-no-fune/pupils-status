/**
 * 宿題提出状況セクション (生徒詳細)
 */

import type { HomeworkSummary } from '@/types'

export default function HomeworkSection({ summary }: { summary: HomeworkSummary }) {
  if (!summary || summary.total === 0) {
    return <p className="text-sm text-gray-400">宿題データがありません</p>
  }
  const rate = summary.rate
  const barColor = rate >= 80 ? 'bg-green-400' : rate >= 50 ? 'bg-yellow-400' : 'bg-red-400'
  const textColor = rate >= 80 ? 'text-green-600' : rate >= 50 ? 'text-yellow-600' : 'text-red-600'

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-600">直近60日の提出率</span>
        <span className={`text-lg font-bold ${textColor}`}>{rate.toFixed(0)}%</span>
      </div>
      <div className="w-full h-2.5 bg-gray-100 rounded-full">
        <div className={`h-full rounded-full ${barColor}`} style={{ width: `${rate}%` }} />
      </div>
      <p className="text-xs text-gray-400">{summary.submitted} / {summary.total} 件 提出</p>

      {/* 直近の提出状況 (ドット) */}
      <div className="flex flex-wrap gap-1 pt-1">
        {summary.recent.map((h) => (
          <span
            key={h.id}
            title={`${h.assigned_date}: ${h.submitted ? '提出済' : '未提出'}`}
            className={`w-4 h-4 rounded-sm ${h.submitted ? 'bg-green-400' : 'bg-red-300'}`}
          />
        ))}
      </div>
      <div className="flex items-center gap-3 text-xs text-gray-400">
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-sm bg-green-400 inline-block" />提出</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-sm bg-red-300 inline-block" />未提出</span>
      </div>
    </div>
  )
}
