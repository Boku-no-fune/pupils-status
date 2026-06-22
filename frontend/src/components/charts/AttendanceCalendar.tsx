/**
 * 出欠カレンダー
 * 月ごとにグリッド表示し、出欠ステータスを色で表現する
 */

import { useMemo } from 'react'
import clsx from 'clsx'
import type { Attendance } from '@/types'

interface Props {
  attendances: Attendance[]
  months?: number
}

const STATUS_COLORS: Record<string, string> = {
  present: 'bg-green-400',
  absent: 'bg-red-400',
  late: 'bg-yellow-400',
  early_leave: 'bg-orange-400',
}

const WEEKDAY_LABELS = ['月', '火', '水', '木', '金', '土', '日']

export default function AttendanceCalendar({ attendances, months = 3 }: Props) {
  const attendanceMap = useMemo(() => {
    const map: Record<string, Attendance> = {}
    attendances.forEach((a) => {
      map[a.class_date] = a
    })
    return map
  }, [attendances])

  // 表示する月を生成
  const monthsToShow = useMemo(() => {
    const result = []
    const today = new Date()
    for (let m = months - 1; m >= 0; m--) {
      const d = new Date(today.getFullYear(), today.getMonth() - m, 1)
      result.push({ year: d.getFullYear(), month: d.getMonth() + 1 })
    }
    return result
  }, [months])

  return (
    <div className="space-y-6">
      {/* 凡例 */}
      <div className="flex items-center gap-4 text-xs text-gray-500">
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-sm bg-green-400 inline-block" />出席</span>
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-sm bg-red-400 inline-block" />欠席</span>
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-sm bg-yellow-400 inline-block" />遅刻</span>
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-sm bg-orange-400 inline-block" />早退</span>
        <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-sm bg-red-400 inline-flex items-center justify-center"><span className="w-1 h-1 rounded-full bg-white" /></span>欠席(振替/映像)</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {monthsToShow.map(({ year, month }) => (
          <MonthCalendar
            key={`${year}-${month}`}
            year={year}
            month={month}
            attendanceMap={attendanceMap}
          />
        ))}
      </div>
    </div>
  )
}

function MonthCalendar({
  year,
  month,
  attendanceMap,
}: {
  year: number
  month: number
  attendanceMap: Record<string, Attendance>
}) {
  // 月の全日程を生成
  const daysInMonth = new Date(year, month, 0).getDate()
  const firstDayOfWeek = new Date(year, month - 1, 1).getDay() // 0=日
  // 月曜始まりに調整
  const startOffset = (firstDayOfWeek + 6) % 7

  const cells: (number | null)[] = Array(startOffset).fill(null)
  for (let d = 1; d <= daysInMonth; d++) {
    cells.push(d)
  }

  return (
    <div>
      <h4 className="text-sm font-semibold text-gray-700 mb-2">{year}年{month}月</h4>
      {/* 曜日ヘッダー */}
      <div className="grid grid-cols-7 gap-0.5 mb-0.5">
        {WEEKDAY_LABELS.map((label) => (
          <div key={label} className="text-center text-xs text-gray-400 py-1">{label}</div>
        ))}
      </div>
      {/* 日付グリッド */}
      <div className="grid grid-cols-7 gap-0.5">
        {cells.map((day, idx) => {
          if (day === null) {
            return <div key={`empty-${idx}`} />
          }
          const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
          const att = attendanceMap[dateStr]
          const status = att?.status
          const hasMakeup = status === 'absent' && !!att?.makeup_type
          const isToday =
            dateStr === new Date().toISOString().split('T')[0]

          const title = att
            ? `${dateStr}: ${statusLabel(status as string)}${hasMakeup ? `（${att.makeup_type}${att.makeup_note ? ': ' + att.makeup_note : ''}）` : ''}`
            : dateStr

          return (
            <div
              key={dateStr}
              title={title}
              className={clsx(
                'relative aspect-square rounded-sm flex items-center justify-center text-xs',
                status ? STATUS_COLORS[status] : 'bg-gray-100',
                status ? 'text-white' : 'text-gray-400',
                isToday ? 'ring-2 ring-blue-500 ring-offset-1' : ''
              )}
            >
              {day}
              {hasMakeup && (
                <span className="absolute bottom-0.5 right-0.5 w-1.5 h-1.5 rounded-full bg-white" />
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    present: '出席',
    absent: '欠席',
    late: '遅刻',
    early_leave: '早退',
  }
  return labels[status] || status
}
