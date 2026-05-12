/**
 * Tab5: 学習進捗
 * 映像授業視聴ログの可視化 + 宿題提出状況
 */

import { useQuery } from '@tanstack/react-query'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  PieChart, Pie, Cell, ResponsiveContainer,
} from 'recharts'
import { dashboardApi } from '@/api/dashboard'
import { gradeLabel } from '@/components/ui/GradeLabel'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

const COLORS = ['#6366f1', '#3b82f6', '#22c55e', '#f59e0b', '#ec4899', '#8b5cf6']

export default function LearningProgressTab() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['learning-progress'],
    queryFn: () => dashboardApi.learningProgress(),
  })

  if (isLoading) return <LoadingSpinner text="学習進捗データを読み込み中..." />
  if (isError || !data) return (
    <div className="text-center text-red-500 py-8">データの取得に失敗しました</div>
  )

  const { video_monthly, video_by_category, homework_summary } = data

  return (
    <div className="space-y-8">

      {/* ===== 映像授業 ===== */}
      <div>
        <h3 className="text-base font-semibold text-gray-800 mb-1">映像授業 視聴時間推移（過去6ヶ月）</h3>
        <p className="text-xs text-gray-400 mb-4">自立部門（映像）受講生徒の合計視聴時間</p>

        {video_monthly.length === 0 ? (
          <div className="flex items-center justify-center h-40 text-gray-400 text-sm bg-gray-50 rounded-lg">
            映像授業データがありません
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={video_monthly} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="month"
                tick={{ fontSize: 12, fill: '#6b7280' }}
                tickFormatter={(v: string) => v.replace('-', '/')}
              />
              <YAxis
                tick={{ fontSize: 12, fill: '#6b7280' }}
                tickFormatter={(v: number) => `${v}分`}
                width={50}
              />
              <Tooltip
                formatter={(v: number) => [`${v.toFixed(0)}分`, '視聴時間']}
                labelFormatter={(l: string) => `${l.replace('-', '/')}月`}
                contentStyle={{ fontSize: 12, borderRadius: 8 }}
              />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="total_minutes" name="視聴時間（分）" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* 科目別視聴時間 */}
      {video_by_category.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 円グラフ */}
          <div>
            <h3 className="text-base font-semibold text-gray-800 mb-4">科目別 視聴割合</h3>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={video_by_category}
                  dataKey="total_minutes"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={({ category, percent }: { category: string; percent: number }) =>
                    `${category} ${(percent * 100).toFixed(0)}%`
                  }
                  labelLine={false}
                >
                  {video_by_category.map((_, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(v: number) => [`${v.toFixed(0)}分`]}
                  contentStyle={{ fontSize: 12, borderRadius: 8 }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* 一覧テーブル */}
          <div>
            <h3 className="text-base font-semibold text-gray-800 mb-4">科目別 視聴時間一覧</h3>
            <div className="space-y-2">
              {video_by_category.map((item, idx) => {
                const total = video_by_category.reduce((s, i) => s + i.total_minutes, 0)
                const pct = total > 0 ? (item.total_minutes / total) * 100 : 0
                return (
                  <div key={item.category}>
                    <div className="flex justify-between text-sm mb-0.5">
                      <span className="text-gray-700">{item.category}</span>
                      <span className="text-gray-500">{item.total_minutes.toFixed(0)}分 ({item.view_count}回)</span>
                    </div>
                    <div className="w-full h-2 bg-gray-100 rounded-full">
                      <div
                        className="h-full rounded-full"
                        style={{ width: `${pct}%`, backgroundColor: COLORS[idx % COLORS.length] }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {/* ===== 宿題提出状況 ===== */}
      <div>
        <h3 className="text-base font-semibold text-gray-800 mb-1">宿題提出状況（直近30日）</h3>
        <p className="text-xs text-gray-400 mb-4">提出率の低い生徒から表示</p>

        {homework_summary.length === 0 ? (
          <div className="flex items-center justify-center h-32 text-gray-400 text-sm bg-gray-50 rounded-lg">
            宿題データがありません
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">生徒名</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">学年</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">出題数</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">提出数</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500">提出率</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 w-40">進捗バー</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {homework_summary.map((item) => {
                  const rate = item.submission_rate
                  const barColor = rate >= 80 ? 'bg-green-400' : rate >= 50 ? 'bg-yellow-400' : 'bg-red-400'
                  const textColor = rate >= 80 ? 'text-green-600' : rate >= 50 ? 'text-yellow-600' : 'text-red-600'
                  return (
                    <tr key={item.student_id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-medium text-gray-900">{item.student_name}</td>
                      <td className="px-4 py-3 text-gray-500">{gradeLabel(item.grade)}</td>
                      <td className="px-4 py-3 text-gray-600">{item.total}</td>
                      <td className="px-4 py-3 text-gray-600">{item.submitted}</td>
                      <td className={`px-4 py-3 font-semibold ${textColor}`}>{rate.toFixed(0)}%</td>
                      <td className="px-4 py-3">
                        <div className="w-full h-2 bg-gray-100 rounded-full">
                          <div
                            className={`h-full rounded-full ${barColor}`}
                            style={{ width: `${rate}%` }}
                          />
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* 補足 */}
      <div className="bg-blue-50 rounded-lg p-4 text-sm text-blue-700">
        <p className="font-medium mb-1">データについて</p>
        <ul className="list-disc list-inside space-y-1 text-blue-600">
          <li>映像授業データは外部システムからCSVインポートで取り込みます</li>
          <li>宿題は直近30日間の出題・提出を集計しています</li>
          <li>個別生徒の詳細は生徒詳細ページで確認できます</li>
        </ul>
      </div>
    </div>
  )
}
