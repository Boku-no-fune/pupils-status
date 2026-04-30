/**
 * 科目別スコア推移 棒グラフ (Recharts)
 */

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { ScoreTrendPoint } from '@/types'

interface Props {
  data: ScoreTrendPoint[]
}

// 科目ごとの色
const SUBJECT_COLORS: Record<string, string> = {
  国語: '#6366f1',
  数学: '#3b82f6',
  英語: '#22c55e',
  理科: '#f59e0b',
  社会: '#ec4899',
}

export default function ScoreBarChart({ data }: Props) {
  if (!data || data.length === 0) {
    return <div className="flex items-center justify-center h-48 text-gray-400 text-sm">データなし</div>
  }

  // Rechartsが使えるフラットな形式に変換
  const chartData = data.map((d) => ({
    name: d.test_name,
    ...d.scores,
  }))

  const subjects = Object.keys(data[0]?.scores || {})

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#6b7280' }} />
        <YAxis domain={[0, 100]} tick={{ fontSize: 12, fill: '#6b7280' }} width={35} />
        <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        {subjects.map((subject) => (
          <Bar
            key={subject}
            dataKey={subject}
            fill={SUBJECT_COLORS[subject] || '#94a3b8'}
            radius={[3, 3, 0, 0]}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  )
}
