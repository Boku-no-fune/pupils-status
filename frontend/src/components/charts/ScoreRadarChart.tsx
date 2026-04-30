/**
 * 科目バランス レーダーチャート (Recharts)
 * 生徒詳細ページの最新テスト結果表示用
 */

import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'
import type { TestScore } from '@/types'

interface Props {
  scores: TestScore[]
}

export default function ScoreRadarChart({ scores }: Props) {
  if (!scores || scores.length === 0) {
    return <div className="flex items-center justify-center h-48 text-gray-400 text-sm">データなし</div>
  }

  // 最新セッションのみ使用
  const latestTestId = scores
    .map((s) => s.test_id)
    .sort()
    .pop()

  const latestScores = scores.filter((s) => s.test_id === latestTestId)

  const data = latestScores.map((s) => ({
    subject: s.subject,
    score: Math.round(s.raw_score),
  }))

  return (
    <ResponsiveContainer width="100%" height={240}>
      <RadarChart data={data} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
        <PolarGrid />
        <PolarAngleAxis dataKey="subject" tick={{ fontSize: 12, fill: '#374151' }} />
        <Radar
          name="スコア"
          dataKey="score"
          stroke="#3b82f6"
          fill="#3b82f6"
          fillOpacity={0.3}
        />
        <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
      </RadarChart>
    </ResponsiveContainer>
  )
}
