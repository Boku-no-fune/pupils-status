/**
 * 試験成績セクション
 * - 複数の試験種別(塾内A/B・業者模試A/B・学校定期テスト・その他)を切替表示
 * - 科目チェックボックスで表示する科目を切替
 * - 推移は折れ線グラフ
 * - 手入力で追記でき、保存すると生徒詳細を再取得して他タブにも反映
 */

import { useMemo, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import { Plus, Trash2 } from 'lucide-react'
import { studentsApi } from '@/api/students'
import type { TestScore } from '@/types'

interface Props {
  studentId: number
  scores: TestScore[]
}

const SUBJECTS = ['国語', '数学', '英語', '理科', '社会']
const SUBJECT_COLORS: Record<string, string> = {
  国語: '#6366f1', 数学: '#3b82f6', 英語: '#22c55e', 理科: '#f59e0b', 社会: '#ec4899',
}
const TEST_TYPE_OPTIONS = ['塾内試験A', '塾内試験B', '業者模試A', '業者模試B', '学校定期テスト', 'その他']

export default function TestScoreSection({ studentId, scores }: Props) {
  const queryClient = useQueryClient()

  // 存在する試験種別
  const availableTypes = useMemo(() => {
    const set = new Set(scores.map((s) => s.test_type || 'その他'))
    return TEST_TYPE_OPTIONS.filter((t) => set.has(t))
  }, [scores])

  const [activeType, setActiveType] = useState<string>(availableTypes[0] || '塾内試験A')
  const [visibleSubjects, setVisibleSubjects] = useState<Set<string>>(new Set(SUBJECTS))
  const [showForm, setShowForm] = useState(false)

  const typeScores = scores.filter((s) => (s.test_type || 'その他') === activeType)

  // セッション(test_id)ごとに科目スコアをまとめてグラフ用データに変換
  const chartData = useMemo(() => {
    const sessions: Record<string, { name: string; date: string; [k: string]: any }> = {}
    typeScores.forEach((s) => {
      const key = s.test_id
      if (!sessions[key]) {
        sessions[key] = { name: s.test_name || s.test_id, date: s.test_date || '' }
      }
      sessions[key][s.subject] = s.raw_score
    })
    return Object.values(sessions).sort((a, b) => (a.date < b.date ? -1 : 1))
  }, [typeScores])

  const toggleSubject = (subj: string) => {
    setVisibleSubjects((prev) => {
      const next = new Set(prev)
      next.has(subj) ? next.delete(subj) : next.add(subj)
      return next
    })
  }

  const deleteMutation = useMutation({
    mutationFn: (scoreId: number) => studentsApi.deleteTestScore(studentId, scoreId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['student-detail', studentId] }),
  })

  return (
    <div className="space-y-4">
      {/* 試験種別タブ */}
      <div className="flex flex-wrap gap-2">
        {(availableTypes.length ? availableTypes : [activeType]).map((t) => (
          <button
            key={t}
            onClick={() => setActiveType(t)}
            className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
              activeType === t
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-600 border-gray-200 hover:border-blue-300'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* 科目チェックボックス */}
      <div className="flex flex-wrap gap-3">
        {SUBJECTS.map((subj) => (
          <label key={subj} className="flex items-center gap-1.5 text-xs text-gray-600 cursor-pointer">
            <input
              type="checkbox"
              checked={visibleSubjects.has(subj)}
              onChange={() => toggleSubject(subj)}
              className="accent-blue-600"
            />
            <span style={{ color: SUBJECT_COLORS[subj] }}>●</span>
            {subj}
          </label>
        ))}
      </div>

      {/* 折れ線グラフ */}
      {chartData.length === 0 ? (
        <div className="flex items-center justify-center h-40 text-gray-400 text-sm bg-gray-50 rounded-lg">
          {activeType} のデータがありません
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#6b7280' }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 12, fill: '#6b7280' }} width={35} />
            <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8 }} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            {SUBJECTS.filter((s) => visibleSubjects.has(s)).map((subj) => (
              <Line
                key={subj}
                type="monotone"
                dataKey={subj}
                stroke={SUBJECT_COLORS[subj]}
                strokeWidth={2}
                dot={{ r: 3 }}
                connectNulls
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      )}

      {/* 手入力フォーム */}
      {showForm ? (
        <ManualScoreForm
          studentId={studentId}
          defaultType={activeType}
          onDone={() => setShowForm(false)}
        />
      ) : (
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-700"
        >
          <Plus size={16} /> 成績を手入力で追加
        </button>
      )}

      {/* スコア一覧 (削除可) */}
      {typeScores.length > 0 && (
        <div className="overflow-x-auto border border-gray-100 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-gray-50 text-gray-400">
              <tr>
                <th className="px-3 py-2 text-left">試験</th>
                <th className="px-3 py-2 text-left">科目</th>
                <th className="px-3 py-2 text-left">点数</th>
                <th className="px-3 py-2 text-left">偏差値</th>
                <th className="px-3 py-2 text-left">日付</th>
                <th className="px-3 py-2"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {[...typeScores]
                .sort((a, b) => (a.test_date || '') < (b.test_date || '') ? 1 : -1)
                .map((s) => (
                  <tr key={s.id} className="group">
                    <td className="px-3 py-1.5 text-gray-600">{s.test_name}</td>
                    <td className="px-3 py-1.5 text-gray-600">{s.subject}</td>
                    <td className="px-3 py-1.5 font-medium text-gray-800">{s.raw_score}</td>
                    <td className="px-3 py-1.5 text-gray-500">{s.deviation_value ?? '—'}</td>
                    <td className="px-3 py-1.5 text-gray-400">{s.test_date || '—'}</td>
                    <td className="px-3 py-1.5 text-right">
                      <button
                        onClick={() => deleteMutation.mutate(s.id)}
                        className="text-gray-300 hover:text-red-400 opacity-0 group-hover:opacity-100"
                      >
                        <Trash2 size={13} />
                      </button>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

function ManualScoreForm({
  studentId, defaultType, onDone,
}: { studentId: number; defaultType: string; onDone: () => void }) {
  const queryClient = useQueryClient()
  const [testType, setTestType] = useState(defaultType)
  const [testName, setTestName] = useState('')
  const [subject, setSubject] = useState('国語')
  const [score, setScore] = useState('')
  const [deviation, setDeviation] = useState('')
  const [testDate, setTestDate] = useState(new Date().toISOString().slice(0, 10))

  const mutation = useMutation({
    mutationFn: () =>
      studentsApi.createTestScore(studentId, {
        test_id: `manual-${testName || testType}-${testDate}`,
        test_name: testName || testType,
        test_type: testType,
        subject,
        raw_score: parseFloat(score),
        deviation_value: deviation ? parseFloat(deviation) : undefined,
        test_date: testDate,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['student-detail', studentId] })
      onDone()
    },
  })

  return (
    <div className="border border-blue-200 bg-blue-50 rounded-lg p-3 space-y-2">
      <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
        <select value={testType} onChange={(e) => setTestType(e.target.value)}
          className="text-sm px-2 py-1 border border-gray-300 rounded">
          {TEST_TYPE_OPTIONS.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
        <input placeholder="試験名(任意)" value={testName} onChange={(e) => setTestName(e.target.value)}
          className="text-sm px-2 py-1 border border-gray-300 rounded" />
        <select value={subject} onChange={(e) => setSubject(e.target.value)}
          className="text-sm px-2 py-1 border border-gray-300 rounded">
          {SUBJECTS.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <input type="number" placeholder="点数" value={score} onChange={(e) => setScore(e.target.value)}
          className="text-sm px-2 py-1 border border-gray-300 rounded" />
        <input type="number" placeholder="偏差値(任意)" value={deviation} onChange={(e) => setDeviation(e.target.value)}
          className="text-sm px-2 py-1 border border-gray-300 rounded" />
        <input type="date" value={testDate} onChange={(e) => setTestDate(e.target.value)}
          className="text-sm px-2 py-1 border border-gray-300 rounded" />
      </div>
      <div className="flex gap-2">
        <button
          onClick={() => mutation.mutate()}
          disabled={!score || mutation.isPending}
          className="text-sm px-4 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-40"
        >
          {mutation.isPending ? '保存中...' : '保存'}
        </button>
        <button onClick={onDone} className="text-sm px-4 py-1.5 border border-gray-300 rounded-lg hover:bg-white">
          キャンセル
        </button>
      </div>
    </div>
  )
}
