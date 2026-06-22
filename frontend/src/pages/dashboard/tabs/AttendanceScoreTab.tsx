/**
 * Tab2: 出欠・成績グラフ
 * - 出席率推移: クラス別にチェックボックスで絞り込み、比較グラフを追加可能
 * - 科目別平均スコア推移: クラス別 + 試験種別(項目)切替、比較グラフを追加可能
 */

import { useState } from 'react'
import { useQuery, useQueries } from '@tanstack/react-query'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import { Plus, X } from 'lucide-react'
import { dashboardApi } from '@/api/dashboard'
import ScoreBarChart from '@/components/charts/ScoreBarChart'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import type { AttendanceTrendPoint, ClassInfo } from '@/types'

const LINE_COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#ec4899', '#8b5cf6', '#06b6d4', '#ef4444', '#84cc16']
const TEST_TYPES = ['塾内試験A', '塾内試験B', '業者模試A', '業者模試B', '学校定期テスト']

export default function AttendanceScoreTab() {
  const { data: classes } = useQuery({ queryKey: ['classes'], queryFn: () => dashboardApi.classes() })

  return (
    <div className="space-y-10">
      <AttendanceComparison classes={classes || []} />
      <ScoreComparison classes={classes || []} />

      <div className="bg-blue-50 rounded-lg p-4 text-sm text-blue-700">
        <p className="font-medium mb-1">グラフについて</p>
        <ul className="list-disc list-inside space-y-1 text-blue-600">
          <li>グラフ下のクラスをチェックすると、そのクラスの推移を重ねて比較できます</li>
          <li>「比較グラフを追加」で別条件のグラフを並べて比較できます</li>
          <li>科目別スコアは試験種別(項目)を切り替えて表示できます</li>
        </ul>
      </div>
    </div>
  )
}

// ============ 出席率推移 ============
function AttendanceComparison({ classes }: { classes: ClassInfo[] }) {
  // 全体 + 各クラスの出席率を事前取得
  const entities = [{ id: 0, name: '全体' }, ...classes.map((c) => ({ id: c.id, name: c.name }))]
  const results = useQueries({
    queries: entities.map((e) => ({
      queryKey: ['att-trend', e.id],
      queryFn: () => dashboardApi.attendanceTrend(6, e.id || undefined),
    })),
  })
  const dataById: Record<number, AttendanceTrendPoint[]> = {}
  entities.forEach((e, i) => { dataById[e.id] = results[i].data || [] })

  const [panels, setPanels] = useState<number[]>([0]) // パネルごとのキー
  const loading = results.some((r) => r.isLoading)

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-semibold text-gray-800">出席率推移 (過去6ヶ月)</h3>
        <button
          onClick={() => setPanels((p) => [...p, Date.now()])}
          className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700"
        >
          <Plus size={15} /> 比較グラフを追加
        </button>
      </div>

      {loading ? (
        <LoadingSpinner text="出席データを読み込み中..." />
      ) : (
        <div className="space-y-6">
          {panels.map((key) => (
            <AttendancePanel
              key={key}
              entities={entities}
              dataById={dataById}
              removable={panels.length > 1}
              onRemove={() => setPanels((p) => p.filter((k) => k !== key))}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function AttendancePanel({
  entities, dataById, removable, onRemove,
}: {
  entities: { id: number; name: string }[]
  dataById: Record<number, AttendanceTrendPoint[]>
  removable: boolean
  onRemove: () => void
}) {
  const [selected, setSelected] = useState<Set<number>>(new Set([0]))

  const toggle = (id: number) => {
    setSelected((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      if (next.size === 0) next.add(0)
      return next
    })
  }

  // 月をベースに各系列の出席率を合成
  const months = (dataById[0] || []).map((p) => p.month)
  const chartData = months.map((month) => {
    const row: Record<string, number | string> = { month }
    entities.forEach((e) => {
      if (selected.has(e.id)) {
        const pt = (dataById[e.id] || []).find((p) => p.month === month)
        if (pt) row[e.name] = pt.rate
      }
    })
    return row
  })

  const selectedEntities = entities.filter((e) => selected.has(e.id))

  return (
    <div className="border border-gray-100 rounded-lg p-4">
      <div className="flex justify-end">
        {removable && (
          <button onClick={onRemove} className="text-gray-300 hover:text-red-400"><X size={16} /></button>
        )}
      </div>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="month" tick={{ fontSize: 12, fill: '#6b7280' }} tickFormatter={(v: string) => v.replace('-', '/')} />
          <YAxis domain={[0, 100]} tickFormatter={(v: number) => `${v}%`} tick={{ fontSize: 12, fill: '#6b7280' }} width={45} />
          <Tooltip formatter={(v: number) => `${v}%`} labelFormatter={(l: string) => `${l.replace('-', '/')}月`} contentStyle={{ fontSize: 12, borderRadius: 8 }} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          {selectedEntities.map((e, i) => (
            <Line key={e.id} type="monotone" dataKey={e.name} stroke={LINE_COLORS[i % LINE_COLORS.length]} strokeWidth={2} dot={{ r: 3 }} connectNulls />
          ))}
        </LineChart>
      </ResponsiveContainer>

      {/* クラスチェックボックス */}
      <div className="flex flex-wrap gap-2 mt-3">
        {entities.map((e) => (
          <label key={e.id} className={`flex items-center gap-1 text-xs px-2 py-1 rounded-full border cursor-pointer ${
            selected.has(e.id) ? 'bg-blue-50 border-blue-300 text-blue-700' : 'bg-white border-gray-200 text-gray-500'
          }`}>
            <input type="checkbox" checked={selected.has(e.id)} onChange={() => toggle(e.id)} className="accent-blue-600" />
            {e.name}
          </label>
        ))}
      </div>
    </div>
  )
}

// ============ 科目別平均スコア推移 ============
function ScoreComparison({ classes }: { classes: ClassInfo[] }) {
  const [panels, setPanels] = useState<number[]>([0])

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-semibold text-gray-800">科目別平均スコア推移</h3>
        <button
          onClick={() => setPanels((p) => [...p, Date.now()])}
          className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700"
        >
          <Plus size={15} /> 比較グラフを追加
        </button>
      </div>

      <div className="space-y-6">
        {panels.map((key) => (
          <ScorePanel
            key={key}
            classes={classes}
            removable={panels.length > 1}
            onRemove={() => setPanels((p) => p.filter((k) => k !== key))}
          />
        ))}
      </div>
    </div>
  )
}

function ScorePanel({
  classes, removable, onRemove,
}: {
  classes: ClassInfo[]
  removable: boolean
  onRemove: () => void
}) {
  const [classId, setClassId] = useState<number>(0)
  const [testType, setTestType] = useState<string>('業者模試A')

  const { data, isLoading } = useQuery({
    queryKey: ['score-trend', classId, testType],
    queryFn: () => dashboardApi.scoreTrend(14, classId || undefined, testType),
  })

  return (
    <div className="border border-gray-100 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-3 flex-wrap">
        <select value={classId} onChange={(e) => setClassId(parseInt(e.target.value))}
          className="text-sm px-2 py-1 border border-gray-300 rounded">
          <option value={0}>全体</option>
          {classes.map((c) => <option key={c.id} value={c.id}>{c.name}（{c.level}）</option>)}
        </select>
        <select value={testType} onChange={(e) => setTestType(e.target.value)}
          className="text-sm px-2 py-1 border border-gray-300 rounded">
          {TEST_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
        {removable && (
          <button onClick={onRemove} className="ml-auto text-gray-300 hover:text-red-400"><X size={16} /></button>
        )}
      </div>

      {isLoading ? (
        <LoadingSpinner text="成績データを読み込み中..." />
      ) : data && data.length > 0 ? (
        <ScoreBarChart data={data} />
      ) : (
        <div className="flex items-center justify-center h-48 text-gray-400 text-sm bg-gray-50 rounded-lg">
          {testType} のデータがありません
        </div>
      )}
    </div>
  )
}
