/**
 * 出席率推移 折れ線グラフ (Recharts)
 */

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { AttendanceTrendPoint } from '@/types'

interface Props {
  data: AttendanceTrendPoint[]
}

export default function AttendanceLineChart({ data }: Props) {
  if (!data || data.length === 0) {
    return <div className="flex items-center justify-center h-48 text-gray-400 text-sm">データなし</div>
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis
          dataKey="month"
          tick={{ fontSize: 12, fill: '#6b7280' }}
          tickFormatter={(v: string) => v.replace('-', '/')}
        />
        <YAxis
          domain={[0, 100]}
          tickFormatter={(v: number) => `${v}%`}
          tick={{ fontSize: 12, fill: '#6b7280' }}
          width={45}
        />
        <Tooltip
          formatter={(value: number) => [`${value}%`, '出席率']}
          labelFormatter={(label: string) => `${label.replace('-', '/')}月`}
          contentStyle={{ fontSize: 12, borderRadius: 8 }}
        />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Line
          type="monotone"
          dataKey="rate"
          name="出席率 (%)"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={{ r: 4, fill: '#3b82f6' }}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
