/**
 * Tab2: 出欠・成績グラフ
 * 出席率推移 (折れ線) と科目別スコア推移 (棒グラフ)
 */

import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '@/api/dashboard'
import AttendanceLineChart from '@/components/charts/AttendanceLineChart'
import ScoreBarChart from '@/components/charts/ScoreBarChart'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

export default function AttendanceScoreTab() {
  const { data: attendanceTrend, isLoading: attendanceLoading } = useQuery({
    queryKey: ['attendance-trend'],
    queryFn: () => dashboardApi.attendanceTrend(6),
  })

  const { data: scoreTrend, isLoading: scoreLoading } = useQuery({
    queryKey: ['score-trend'],
    queryFn: () => dashboardApi.scoreTrend(12),
  })

  return (
    <div className="space-y-8">
      {/* 出席率推移 */}
      <div>
        <h3 className="text-base font-semibold text-gray-800 mb-4">
          出席率推移 (過去6ヶ月)
        </h3>
        {attendanceLoading ? (
          <LoadingSpinner text="出席データを読み込み中..." />
        ) : (
          <AttendanceLineChart data={attendanceTrend || []} />
        )}
      </div>

      {/* 科目別スコア推移 */}
      <div>
        <h3 className="text-base font-semibold text-gray-800 mb-4">
          科目別平均スコア推移 (教室全体)
        </h3>
        {scoreLoading ? (
          <LoadingSpinner text="成績データを読み込み中..." />
        ) : scoreTrend && scoreTrend.length > 0 ? (
          <ScoreBarChart data={scoreTrend} />
        ) : (
          <div className="flex items-center justify-center h-48 text-gray-400 text-sm bg-gray-50 rounded-lg">
            テストデータがありません
          </div>
        )}
      </div>

      {/* 補足説明 */}
      <div className="bg-blue-50 rounded-lg p-4 text-sm text-blue-700">
        <p className="font-medium mb-1">グラフについて</p>
        <ul className="list-disc list-inside space-y-1 text-blue-600">
          <li>出席率は在籍中・体験中の全生徒の平均を表示しています</li>
          <li>科目別スコアは各模試での教室全体の平均点です</li>
          <li>個別生徒のデータは生徒詳細ページで確認できます</li>
        </ul>
      </div>
    </div>
  )
}
