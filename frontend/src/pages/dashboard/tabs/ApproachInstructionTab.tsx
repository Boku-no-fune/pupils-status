/**
 * Tab: アプローチ指示 (管理者・教室長)
 * 部門/学年/クラス/全体 を対象に指示を作成 (PDF添付可)。生徒ページに該当指示が表示される。
 */

import { useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2, FileText, Megaphone } from 'lucide-react'
import { approachApi } from '@/api/approachInstructions'
import { dashboardApi } from '@/api/dashboard'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

const TARGET_TYPES = ['全体', '部門', '学年', 'クラス']
const DIVISIONS = ['集団', '個別', '自立']
const GRADES = [
  ...[1, 2, 3, 4, 5, 6].map((g) => ({ value: String(g), label: `小${g}` })),
  ...[7, 8, 9].map((g) => ({ value: String(g), label: `中${g - 6}` })),
  ...[10, 11, 12].map((g) => ({ value: String(g), label: `高${g - 9}` })),
]

export default function ApproachInstructionTab() {
  const queryClient = useQueryClient()
  const fileRef = useRef<HTMLInputElement>(null)
  const { data: instructions, isLoading } = useQuery({ queryKey: ['approach-instructions'], queryFn: () => approachApi.list() })
  const { data: classes } = useQuery({ queryKey: ['classes'], queryFn: () => dashboardApi.classes() })

  const [showForm, setShowForm] = useState(false)
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [targetType, setTargetType] = useState('全体')
  const [targetValue, setTargetValue] = useState('')
  const [period, setPeriod] = useState('')
  const [pdfData, setPdfData] = useState<string | null>(null)
  const [pdfName, setPdfName] = useState<string | null>(null)

  const reset = () => {
    setTitle(''); setContent(''); setTargetType('全体'); setTargetValue('')
    setPeriod(''); setPdfData(null); setPdfName(null); setShowForm(false)
  }

  const create = useMutation({
    mutationFn: () => approachApi.create({
      title, content, target_type: targetType,
      target_value: targetType === '全体' ? undefined : targetValue || undefined,
      period: period || undefined,
      pdf_data: pdfData || undefined, pdf_filename: pdfName || undefined,
    }),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['approach-instructions'] }); reset() },
  })
  const remove = useMutation({
    mutationFn: (id: number) => approachApi.remove(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['approach-instructions'] }),
  })

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => { setPdfData(reader.result as string); setPdfName(file.name) }
    reader.readAsDataURL(file)
  }

  const openPdf = async (id: number) => {
    const { pdf_data } = await approachApi.getPdf(id)
    const w = window.open()
    if (w) w.document.write(`<iframe src="${pdf_data}" style="width:100%;height:100%;border:0"></iframe>`)
  }

  if (isLoading) return <LoadingSpinner text="読み込み中..." />

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold text-gray-800 flex items-center gap-2"><Megaphone size={18} className="text-amber-500" />アプローチ指示</h3>
          <p className="text-xs text-gray-400">部門・学年・クラス・全体を対象に指示を出します。該当生徒の個人ページに表示されます。</p>
        </div>
        {!showForm && (
          <button onClick={() => setShowForm(true)} className="flex items-center gap-1 text-sm px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            <Plus size={15} /> 指示を作成
          </button>
        )}
      </div>

      {showForm && (
        <div className="border border-blue-200 bg-blue-50 rounded-xl p-4 space-y-3">
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="タイトル"
            className="w-full text-sm px-3 py-2 border border-gray-300 rounded-lg" />
          <textarea value={content} onChange={(e) => setContent(e.target.value)} rows={3} placeholder="指示内容"
            className="w-full text-sm px-3 py-2 border border-gray-300 rounded-lg resize-none" />
          <div className="flex flex-wrap gap-2 items-center">
            <select value={targetType} onChange={(e) => { setTargetType(e.target.value); setTargetValue('') }}
              className="text-sm px-2 py-1.5 border border-gray-300 rounded-lg">
              {TARGET_TYPES.map((t) => <option key={t} value={t}>対象: {t}</option>)}
            </select>
            {targetType === '部門' && (
              <select value={targetValue} onChange={(e) => setTargetValue(e.target.value)} className="text-sm px-2 py-1.5 border border-gray-300 rounded-lg">
                <option value="">部門を選択</option>
                {DIVISIONS.map((d) => <option key={d} value={d}>{d}</option>)}
              </select>
            )}
            {targetType === '学年' && (
              <select value={targetValue} onChange={(e) => setTargetValue(e.target.value)} className="text-sm px-2 py-1.5 border border-gray-300 rounded-lg">
                <option value="">学年を選択</option>
                {GRADES.map((g) => <option key={g.value} value={g.value}>{g.label}</option>)}
              </select>
            )}
            {targetType === 'クラス' && (
              <select value={targetValue} onChange={(e) => setTargetValue(e.target.value)} className="text-sm px-2 py-1.5 border border-gray-300 rounded-lg">
                <option value="">クラスを選択</option>
                {(classes || []).map((c) => <option key={c.id} value={c.name}>{c.name}</option>)}
              </select>
            )}
            <input value={period} onChange={(e) => setPeriod(e.target.value)} placeholder="時期 (例: 2026-06 第2週)"
              className="text-sm px-2 py-1.5 border border-gray-300 rounded-lg" />
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => fileRef.current?.click()} className="flex items-center gap-1 text-sm px-3 py-1.5 border border-gray-300 rounded-lg bg-white hover:bg-gray-50">
              <FileText size={14} /> PDF添付
            </button>
            {pdfName && <span className="text-xs text-gray-500">{pdfName}</span>}
            <input ref={fileRef} type="file" accept="application/pdf" className="hidden" onChange={handleFile} />
          </div>
          <div className="flex gap-2">
            <button onClick={() => create.mutate()} disabled={!title.trim() || !content.trim() || create.isPending}
              className="text-sm px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-40">
              {create.isPending ? '保存中...' : '指示を出す'}
            </button>
            <button onClick={reset} className="text-sm px-4 py-2 border border-gray-300 rounded-lg hover:bg-white">キャンセル</button>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {(instructions || []).length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-8">指示はまだありません</p>
        ) : (instructions || []).map((ins) => (
          <div key={ins.id} className="border border-gray-200 rounded-xl p-4 group">
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1 flex-wrap">
                  <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full">
                    {ins.target_type}{ins.target_value ? `: ${ins.target_value}` : ''}
                  </span>
                  {ins.period && <span className="text-xs text-gray-400">{ins.period}</span>}
                  {ins.created_by_name && <span className="text-xs text-gray-400">• {ins.created_by_name}</span>}
                </div>
                <p className="text-sm font-medium text-gray-800">{ins.title}</p>
                <p className="text-sm text-gray-600 mt-0.5 whitespace-pre-wrap">{ins.content}</p>
                {ins.has_pdf && (
                  <button onClick={() => openPdf(ins.id)} className="mt-2 inline-flex items-center gap-1 text-xs text-blue-600 hover:underline">
                    <FileText size={13} /> {ins.pdf_filename || '添付PDF'}
                  </button>
                )}
              </div>
              <button onClick={() => remove.mutate(ins.id)} className="text-gray-300 hover:text-red-400 opacity-0 group-hover:opacity-100">
                <Trash2 size={15} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
