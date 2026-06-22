/**
 * 生徒詳細ページの追加セクション群
 * - PhoneListSection:    電話番号(最大3件)+メモ
 * - TeacherAssignSection: 担当講師の追加・削除
 * - ProfileMemoSection:  プロフィール定型メモ
 * - ParentRequestSection: 保護者要望・クレーム履歴
 * - ExamCertSection:     英検・漢検
 * - ReferralSection:     紹介・被紹介履歴
 * - VideoHistorySection: 映像授業 視聴履歴
 */

import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2, Phone, Pencil, Check } from 'lucide-react'
import { studentsApi } from '@/api/students'
import { dashboardApi } from '@/api/dashboard'
import type {
  StudentPhone, TeacherBrief, ProfileMemo, ParentRequest,
  ExamCertification, ReferralMade, ReferralReceived, VideoLessonLog,
} from '@/types'

function useInvalidate(studentId: number) {
  const qc = useQueryClient()
  return () => qc.invalidateQueries({ queryKey: ['student-detail', studentId] })
}

// ===================== 電話番号 =====================
export function PhoneListSection({ studentId, phones }: { studentId: number; phones: StudentPhone[] }) {
  const invalidate = useInvalidate(studentId)
  const [editing, setEditing] = useState<number | null>(null)
  const [memoDraft, setMemoDraft] = useState('')
  const [adding, setAdding] = useState(false)
  const [newNumber, setNewNumber] = useState('')
  const [newMemo, setNewMemo] = useState('')

  const updateMemo = useMutation({
    mutationFn: (p: { id: number; memo: string }) => studentsApi.updatePhoneMemo(studentId, p.id, p.memo),
    onSuccess: () => { invalidate(); setEditing(null) },
  })
  const addPhone = useMutation({
    mutationFn: () => studentsApi.createPhone(studentId, { phone_number: newNumber, memo: newMemo }),
    onSuccess: () => { invalidate(); setAdding(false); setNewNumber(''); setNewMemo('') },
  })
  const delPhone = useMutation({
    mutationFn: (id: number) => studentsApi.deletePhone(studentId, id),
    onSuccess: invalidate,
  })

  return (
    <div className="space-y-2">
      {phones.length === 0 && !adding && <p className="text-sm text-gray-400">登録なし</p>}
      {phones.map((p) => (
        <div key={p.id} className="flex items-center gap-2 group text-sm">
          <Phone size={13} className="text-gray-400 flex-shrink-0" />
          <span className="text-gray-700 font-mono">{p.phone_number}</span>
          {editing === p.id ? (
            <>
              <input
                value={memoDraft}
                onChange={(e) => setMemoDraft(e.target.value)}
                placeholder="メモ"
                className="text-xs px-2 py-0.5 border border-gray-300 rounded flex-1 min-w-0"
              />
              <button onClick={() => updateMemo.mutate({ id: p.id, memo: memoDraft })} className="text-green-500"><Check size={14} /></button>
            </>
          ) : (
            <>
              <span className="text-xs text-gray-400 flex-1">{p.memo || '（メモなし）'}</span>
              <button
                onClick={() => { setEditing(p.id); setMemoDraft(p.memo || '') }}
                className="text-gray-300 hover:text-blue-400 opacity-0 group-hover:opacity-100"
              ><Pencil size={12} /></button>
              <button
                onClick={() => delPhone.mutate(p.id)}
                className="text-gray-300 hover:text-red-400 opacity-0 group-hover:opacity-100"
              ><Trash2 size={12} /></button>
            </>
          )}
        </div>
      ))}

      {adding ? (
        <div className="flex flex-wrap gap-1.5 items-center">
          <input value={newNumber} onChange={(e) => setNewNumber(e.target.value)} placeholder="電話番号"
            className="text-xs px-2 py-1 border border-gray-300 rounded" />
          <input value={newMemo} onChange={(e) => setNewMemo(e.target.value)} placeholder="メモ(例:父の携帯)"
            className="text-xs px-2 py-1 border border-gray-300 rounded" />
          <button onClick={() => addPhone.mutate()} disabled={!newNumber}
            className="text-xs px-2 py-1 bg-blue-600 text-white rounded disabled:opacity-40">追加</button>
          <button onClick={() => setAdding(false)} className="text-xs text-gray-400">取消</button>
        </div>
      ) : phones.length < 3 && (
        <button onClick={() => setAdding(true)} className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700">
          <Plus size={13} /> 電話番号を追加
        </button>
      )}
    </div>
  )
}

// ===================== 担当講師 =====================
export function TeacherAssignSection({ studentId, teachers }: { studentId: number; teachers: TeacherBrief[] }) {
  const invalidate = useInvalidate(studentId)
  const [adding, setAdding] = useState(false)
  const { data: allTeachers } = useQuery({ queryKey: ['teachers'], queryFn: () => dashboardApi.teachers(), enabled: adding })

  const addT = useMutation({
    mutationFn: (uid: number) => studentsApi.addTeacher(studentId, uid),
    onSuccess: () => { invalidate(); setAdding(false) },
  })
  const removeT = useMutation({
    mutationFn: (uid: number) => studentsApi.removeTeacher(studentId, uid),
    onSuccess: invalidate,
  })

  const assignedIds = new Set(teachers.map((t) => t.id))
  const candidates = (allTeachers || []).filter((t) => !assignedIds.has(t.id))

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2">
        {teachers.length === 0 && <span className="text-sm text-gray-400">担当講師なし</span>}
        {teachers.map((t) => (
          <span key={t.id} className="group inline-flex items-center gap-1 text-xs bg-blue-50 text-blue-700 px-2.5 py-1 rounded-full border border-blue-200">
            {t.name}
            <button onClick={() => removeT.mutate(t.id)} className="text-blue-300 hover:text-red-500">
              <Trash2 size={11} />
            </button>
          </span>
        ))}
      </div>

      {adding ? (
        <div className="flex flex-wrap gap-1.5 items-center">
          <select
            onChange={(e) => e.target.value && addT.mutate(parseInt(e.target.value))}
            defaultValue=""
            className="text-xs px-2 py-1 border border-gray-300 rounded"
          >
            <option value="" disabled>講師を選択...</option>
            {candidates.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
          </select>
          <button onClick={() => setAdding(false)} className="text-xs text-gray-400">取消</button>
        </div>
      ) : (
        <button onClick={() => setAdding(true)} className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700">
          <Plus size={13} /> 担当講師を追加
        </button>
      )}
    </div>
  )
}

// ===================== プロフィール定型メモ =====================
const PROFILE_CATEGORIES = ['部活動', '習い事', '家族構成', '家族の職業・学年', '通学校情報']

export function ProfileMemoSection({ studentId, memos }: { studentId: number; memos: ProfileMemo[] }) {
  const invalidate = useInvalidate(studentId)
  const [category, setCategory] = useState(PROFILE_CATEGORIES[0])
  const [content, setContent] = useState('')

  const add = useMutation({
    mutationFn: () => studentsApi.createProfileMemo(studentId, { category, content }),
    onSuccess: () => { invalidate(); setContent('') },
  })
  const del = useMutation({
    mutationFn: (id: number) => studentsApi.deleteProfileMemo(studentId, id),
    onSuccess: invalidate,
  })

  return (
    <div className="space-y-2">
      {memos.length === 0 && <p className="text-sm text-gray-400">メモなし</p>}
      {memos.map((m) => (
        <div key={m.id} className="flex items-start gap-2 group text-sm">
          <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded flex-shrink-0">{m.category}</span>
          <span className="flex-1 text-gray-700">{m.content}</span>
          <button onClick={() => del.mutate(m.id)} className="text-gray-300 hover:text-red-400 opacity-0 group-hover:opacity-100">
            <Trash2 size={13} />
          </button>
        </div>
      ))}
      <div className="flex flex-wrap gap-1.5 items-center pt-1">
        <select value={category} onChange={(e) => setCategory(e.target.value)}
          className="text-xs px-2 py-1 border border-gray-300 rounded">
          {PROFILE_CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <input value={content} onChange={(e) => setContent(e.target.value)} placeholder="内容を入力..."
          className="text-xs px-2 py-1 border border-gray-300 rounded flex-1 min-w-32" />
        <button onClick={() => add.mutate()} disabled={!content.trim()}
          className="text-xs px-2 py-1 bg-blue-600 text-white rounded disabled:opacity-40">追加</button>
      </div>
    </div>
  )
}

// ===================== 保護者要望・クレーム =====================
export function ParentRequestSection({ studentId, requests }: { studentId: number; requests: ParentRequest[] }) {
  const invalidate = useInvalidate(studentId)
  const [showForm, setShowForm] = useState(false)
  const [reqType, setReqType] = useState('要望')
  const [content, setContent] = useState('')

  const add = useMutation({
    mutationFn: () => studentsApi.createParentRequest(studentId, { request_type: reqType, content }),
    onSuccess: () => { invalidate(); setContent(''); setShowForm(false) },
  })
  const toggleStatus = useMutation({
    mutationFn: (p: { id: number; status: string }) => studentsApi.updateParentRequest(studentId, p.id, p.status),
    onSuccess: invalidate,
  })
  const del = useMutation({
    mutationFn: (id: number) => studentsApi.deleteParentRequest(studentId, id),
    onSuccess: invalidate,
  })

  return (
    <div className="space-y-2">
      {requests.length === 0 && !showForm && <p className="text-sm text-gray-400">記録なし</p>}
      {requests.map((r) => (
        <div key={r.id} className="border-b border-gray-100 pb-2 last:border-0 group">
          <div className="flex items-center gap-2">
            <span className={`text-xs px-2 py-0.5 rounded-full ${r.request_type === 'クレーム' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}`}>
              {r.request_type}
            </span>
            <button
              onClick={() => toggleStatus.mutate({ id: r.id, status: r.status === '対応中' ? '対応済' : '対応中' })}
              className={`text-xs px-2 py-0.5 rounded-full ${r.status === '対応済' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}
            >
              {r.status}
            </button>
            <span className="text-xs text-gray-400 ml-auto">{new Date(r.occurred_at).toLocaleDateString('ja-JP')}</span>
            <button onClick={() => del.mutate(r.id)} className="text-gray-300 hover:text-red-400 opacity-0 group-hover:opacity-100">
              <Trash2 size={12} />
            </button>
          </div>
          <p className="text-sm text-gray-700 mt-1">{r.content}</p>
        </div>
      ))}

      {showForm ? (
        <div className="border border-blue-200 bg-blue-50 rounded-lg p-2 space-y-2">
          <div className="flex gap-2">
            {['要望', 'クレーム'].map((t) => (
              <button key={t} onClick={() => setReqType(t)}
                className={`text-xs px-2.5 py-1 rounded-full border ${reqType === t ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-500 border-gray-200'}`}>
                {t}
              </button>
            ))}
          </div>
          <textarea value={content} onChange={(e) => setContent(e.target.value)} rows={2} placeholder="内容..."
            className="w-full text-sm px-2 py-1 border border-gray-300 rounded resize-none" />
          <div className="flex gap-2">
            <button onClick={() => add.mutate()} disabled={!content.trim()}
              className="text-sm px-3 py-1 bg-blue-600 text-white rounded disabled:opacity-40">保存</button>
            <button onClick={() => setShowForm(false)} className="text-sm px-3 py-1 border border-gray-300 rounded">取消</button>
          </div>
        </div>
      ) : (
        <button onClick={() => setShowForm(true)} className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700">
          <Plus size={13} /> 要望・クレームを記録
        </button>
      )}
    </div>
  )
}

// ===================== 英検・漢検 =====================
const EIKEN_LEVELS = ['5級', '4級', '3級', '準2級', '準2級プラス', '2級', '準1級', '1級']
const KANKEN_LEVELS = ['10級', '9級', '8級', '7級', '6級', '5級', '4級', '3級', '準2級', '2級', '準1級', '1級']

export function ExamCertSection({ studentId, certs }: { studentId: number; certs: ExamCertification[] }) {
  const invalidate = useInvalidate(studentId)
  const [showForm, setShowForm] = useState(false)
  const [examType, setExamType] = useState<'英検' | '漢検'>('英検')
  const [level, setLevel] = useState('5級')
  const [score, setScore] = useState('')
  const [result, setResult] = useState('合格')
  const [examDate, setExamDate] = useState(new Date().toISOString().slice(0, 10))

  const add = useMutation({
    mutationFn: () => studentsApi.createExamCert(studentId, {
      exam_type: examType, level, score: score ? parseInt(score) : undefined, result, exam_date: examDate,
    }),
    onSuccess: () => { invalidate(); setShowForm(false); setScore('') },
  })
  const del = useMutation({
    mutationFn: (id: number) => studentsApi.deleteExamCert(studentId, id),
    onSuccess: invalidate,
  })

  const levels = examType === '英検' ? EIKEN_LEVELS : KANKEN_LEVELS

  return (
    <div className="space-y-2">
      {certs.length === 0 && !showForm && <p className="text-sm text-gray-400">記録なし</p>}
      {certs.map((c) => (
        <div key={c.id} className="flex items-center gap-2 group text-sm">
          <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">{c.exam_type}</span>
          <span className="font-medium text-gray-800">{c.level}</span>
          {c.score != null && <span className="text-xs text-gray-500">{c.score}点</span>}
          <span className={`text-xs ${c.result === '合格' ? 'text-green-600' : c.result === '受験予定' ? 'text-blue-500' : 'text-red-500'}`}>
            {c.result}
          </span>
          <span className="text-xs text-gray-400 ml-auto">{c.exam_date || ''}</span>
          <button onClick={() => del.mutate(c.id)} className="text-gray-300 hover:text-red-400 opacity-0 group-hover:opacity-100">
            <Trash2 size={12} />
          </button>
        </div>
      ))}

      {showForm ? (
        <div className="border border-blue-200 bg-blue-50 rounded-lg p-2 space-y-2">
          <div className="grid grid-cols-2 gap-2">
            <select value={examType} onChange={(e) => { setExamType(e.target.value as '英検' | '漢検'); setLevel(e.target.value === '英検' ? '5級' : '10級') }}
              className="text-xs px-2 py-1 border border-gray-300 rounded">
              <option value="英検">英検</option>
              <option value="漢検">漢検</option>
            </select>
            <select value={level} onChange={(e) => setLevel(e.target.value)} className="text-xs px-2 py-1 border border-gray-300 rounded">
              {levels.map((l) => <option key={l} value={l}>{l}</option>)}
            </select>
            <input type="number" value={score} onChange={(e) => setScore(e.target.value)} placeholder="スコア(任意)"
              className="text-xs px-2 py-1 border border-gray-300 rounded" />
            <select value={result} onChange={(e) => setResult(e.target.value)} className="text-xs px-2 py-1 border border-gray-300 rounded">
              {['合格', '不合格', '受験予定'].map((r) => <option key={r} value={r}>{r}</option>)}
            </select>
            <input type="date" value={examDate} onChange={(e) => setExamDate(e.target.value)}
              className="text-xs px-2 py-1 border border-gray-300 rounded col-span-2" />
          </div>
          <div className="flex gap-2">
            <button onClick={() => add.mutate()} className="text-sm px-3 py-1 bg-blue-600 text-white rounded">保存</button>
            <button onClick={() => setShowForm(false)} className="text-sm px-3 py-1 border border-gray-300 rounded">取消</button>
          </div>
        </div>
      ) : (
        <button onClick={() => setShowForm(true)} className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700">
          <Plus size={13} /> 検定結果を追加
        </button>
      )}
    </div>
  )
}

// ===================== 紹介・被紹介 (システム連携・閲覧のみ) =====================
export function ReferralSection({ made, received }: { made: ReferralMade[]; received: ReferralReceived[] }) {
  if (made.length === 0 && received.length === 0) {
    return <p className="text-sm text-gray-400">紹介履歴はありません</p>
  }
  return (
    <div className="space-y-3 text-sm">
      {received.length > 0 && (
        <div>
          <p className="text-xs text-gray-400 mb-1">被紹介（この生徒を紹介した人）</p>
          {received.map((r) => (
            <div key={r.id} className="text-gray-700">
              ← {r.referrer_name || '不明'}
              {r.occurred_at && <span className="text-xs text-gray-400 ml-2">{r.occurred_at}</span>}
            </div>
          ))}
        </div>
      )}
      {made.length > 0 && (
        <div>
          <p className="text-xs text-gray-400 mb-1">紹介（この生徒が紹介した人）</p>
          {made.map((r) => (
            <div key={r.id} className="text-gray-700">
              → {r.referred_name || '不明'}
              {r.note && <span className="text-xs text-gray-400 ml-2">{r.note}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ===================== 映像授業 視聴履歴 =====================
export function VideoHistorySection({ logs }: { logs: VideoLessonLog[] }) {
  if (logs.length === 0) return <p className="text-sm text-gray-400">視聴履歴はありません</p>
  return (
    <div className="space-y-1.5 max-h-72 overflow-y-auto">
      {logs.map((v) => (
        <div key={v.id} className="flex items-center justify-between text-sm border-b border-gray-50 pb-1.5">
          <div className="flex items-center gap-2 min-w-0">
            {v.lesson_category && (
              <span className="text-xs bg-indigo-50 text-indigo-600 px-1.5 py-0.5 rounded flex-shrink-0">{v.lesson_category}</span>
            )}
            <span className="text-gray-700 truncate">{v.lesson_name}</span>
          </div>
          <span className="text-xs text-gray-400 flex-shrink-0 ml-2">
            {new Date(v.viewed_at).toLocaleDateString('ja-JP', { month: 'numeric', day: 'numeric' })}
          </span>
        </div>
      ))}
    </div>
  )
}
