/**
 * Tab1: 生徒一覧・ステータス
 * フィルタ・ソート・ページネーション付きテーブル
 * 列: 会員番号 / 氏名 / 学年 / クラス / ステータス / 最終来室 / 出席率 / 直近成績 / 担当講師
 */

import { useState } from 'react'
import { useQuery, keepPreviousData } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Search, ChevronUp, ChevronDown, Minus, ArrowUpDown } from 'lucide-react'
import { dashboardApi } from '@/api/dashboard'
import { StudentStatusBadge } from '@/components/ui/Badge'
import { gradeLabel } from '@/components/ui/GradeLabel'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import type { StudentStatus } from '@/types'

const STATUS_OPTIONS = [
  { value: '', label: 'すべて' },
  { value: 'enrolled', label: '在籍' },
  { value: 'trial', label: '体験' },
  { value: 'on_leave', label: '休会' },
  { value: 'withdrawn', label: '退会' },
]

const SCHOOL_TYPE_OPTIONS = [
  { value: '', label: '学校区分: すべて' },
  { value: '公立', label: '公立' },
  { value: '私立', label: '私立' },
  { value: '国立', label: '国立' },
]

const DIVISION_OPTIONS = [
  { value: '', label: '部門: すべて' },
  { value: '集団', label: '集団' },
  { value: '個別', label: '個別' },
  { value: '自立', label: '自立' },
]

type SortKey = 'member_number' | 'name' | 'grade' | 'class' | 'status' | 'last_visit' | 'attendance_rate_30d'

const COLUMNS: { key: SortKey | null; label: string }[] = [
  { key: 'member_number', label: '会員番号' },
  { key: 'name', label: '氏名' },
  { key: 'grade', label: '学年' },
  { key: 'class', label: 'クラス' },
  { key: 'status', label: 'ステータス' },
  { key: 'last_visit', label: '最終来室' },
  { key: 'attendance_rate_30d', label: '出席率(30日)' },
  { key: null, label: '直近成績' },
  { key: null, label: '担当講師' },
]

export default function StudentListTab() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [schoolTypeFilter, setSchoolTypeFilter] = useState('')
  const [divisionFilter, setDivisionFilter] = useState('')
  const [sortBy, setSortBy] = useState<SortKey>('grade')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')
  const [page, setPage] = useState(1)
  const perPage = 20

  const toggleSort = (key: SortKey) => {
    if (sortBy === key) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(key)
      setSortDir('asc')
    }
    setPage(1)
  }

  const { data, isLoading, isError } = useQuery({
    queryKey: ['student-list', search, statusFilter, schoolTypeFilter, divisionFilter, sortBy, sortDir, page],
    queryFn: () =>
      dashboardApi.studentList({
        search: search || undefined,
        status: statusFilter || undefined,
        school_type: schoolTypeFilter || undefined,
        division: divisionFilter || undefined,
        sort_by: sortBy,
        sort_dir: sortDir,
        page,
        per_page: perPage,
      }),
    placeholderData: keepPreviousData,
  })

  const totalPages = data ? Math.ceil(data.total / perPage) : 1

  if (isLoading) return <LoadingSpinner />
  if (isError) return <div className="text-center text-red-500 py-8">データの取得に失敗しました</div>

  return (
    <div className="space-y-4">
      {/* フィルターバー */}
      <div className="flex flex-wrap gap-3 items-center">
        <div className="relative flex-1 min-w-48">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="生徒名で検索..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
            className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1) }}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {STATUS_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>

        <select
          value={schoolTypeFilter}
          onChange={(e) => { setSchoolTypeFilter(e.target.value); setPage(1) }}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {SCHOOL_TYPE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>

        <select
          value={divisionFilter}
          onChange={(e) => { setDivisionFilter(e.target.value); setPage(1) }}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {DIVISION_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>

        <span className="text-sm text-gray-500 ml-auto">
          全 {data?.total ?? 0} 名
        </span>
      </div>

      {/* テーブル */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              {COLUMNS.map((col) => (
                <th
                  key={col.label}
                  onClick={col.key ? () => toggleSort(col.key as SortKey) : undefined}
                  className={`px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap ${
                    col.key ? 'cursor-pointer select-none hover:text-gray-800' : ''
                  }`}
                >
                  <span className="inline-flex items-center gap-1">
                    {col.label}
                    {col.key && (
                      sortBy === col.key
                        ? (sortDir === 'asc' ? <ChevronUp size={12} /> : <ChevronDown size={12} />)
                        : <ArrowUpDown size={12} className="text-gray-300" />
                    )}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {data?.students.map((student) => (
              <tr
                key={student.id}
                onClick={() => navigate(`/students/${student.id}`)}
                className="hover:bg-blue-50 cursor-pointer transition-colors"
              >
                <td className="px-4 py-3 text-gray-500 font-mono text-xs">{student.member_number || '—'}</td>
                <td className="px-4 py-3 font-medium text-gray-900">{student.name}</td>
                <td className="px-4 py-3 text-gray-600">{gradeLabel(student.grade)}</td>
                <td className="px-4 py-3">
                  {student.class_label ? (
                    <span className="text-xs bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-full border border-indigo-100">
                      {student.class_label}
                    </span>
                  ) : <span className="text-gray-400">—</span>}
                </td>
                <td className="px-4 py-3">
                  <StudentStatusBadge status={student.status as StudentStatus} />
                </td>
                <td className="px-4 py-3 text-gray-600">
                  {student.last_visit ? student.last_visit : '—'}
                </td>
                <td className="px-4 py-3">
                  {student.attendance_rate_30d !== undefined ? (
                    <span className={
                      student.attendance_rate_30d < 60 ? 'text-red-600 font-semibold' :
                      student.attendance_rate_30d < 75 ? 'text-yellow-600 font-medium' :
                      'text-green-600'
                    }>
                      {student.attendance_rate_30d.toFixed(0)}%
                    </span>
                  ) : '—'}
                </td>
                <td className="px-4 py-3">
                  {student.recent_grade_change ? (
                    <span className={
                      student.recent_grade_change.direction === 'up' ? 'text-green-600 flex items-center gap-1' :
                      student.recent_grade_change.direction === 'down' ? 'text-red-600 flex items-center gap-1' :
                      'text-gray-500 flex items-center gap-1'
                    }>
                      {student.recent_grade_change.direction === 'up' ? <ChevronUp size={14} /> :
                       student.recent_grade_change.direction === 'down' ? <ChevronDown size={14} /> :
                       <Minus size={14} />}
                      {student.recent_grade_change.subject} ({student.recent_grade_change.change > 0 ? '+' : ''}{student.recent_grade_change.change.toFixed(0)}点)
                    </span>
                  ) : '—'}
                </td>
                <td className="px-4 py-3 text-gray-600">
                  {student.teachers && student.teachers.length > 0
                    ? student.teachers.map((t) => t.name).join('、')
                    : (student.assigned_teacher_name || '—')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ページネーション */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-2">
          <button
            disabled={page <= 1}
            onClick={() => setPage(page - 1)}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg disabled:opacity-40 hover:bg-gray-50"
          >
            前へ
          </button>
          <span className="text-sm text-gray-600">{page} / {totalPages}</span>
          <button
            disabled={page >= totalPages}
            onClick={() => setPage(page + 1)}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg disabled:opacity-40 hover:bg-gray-50"
          >
            次へ
          </button>
        </div>
      )}
    </div>
  )
}
