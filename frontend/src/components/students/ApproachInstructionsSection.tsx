/**
 * この生徒に該当する 本部・教室長からのアプローチ指示 (生徒詳細)
 */

import { FileText, Download } from 'lucide-react'
import { approachApi } from '@/api/approachInstructions'
import type { ApproachInstruction } from '@/types'

const TARGET_LABEL: Record<string, string> = { 全体: '全体', 部門: '部門', 学年: '学年', クラス: 'クラス' }

export default function ApproachInstructionsSection({ instructions }: { instructions: ApproachInstruction[] }) {
  const openPdf = async (id: number) => {
    const { pdf_data } = await approachApi.getPdf(id)
    const w = window.open()
    if (w) w.document.write(`<iframe src="${pdf_data}" style="width:100%;height:100%;border:0"></iframe>`)
  }

  if (!instructions || instructions.length === 0) {
    return <p className="text-sm text-gray-400">該当する指示はありません</p>
  }

  return (
    <div className="space-y-3">
      {instructions.map((ins) => (
        <div key={ins.id} className="border border-amber-100 bg-amber-50/50 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full">
              {TARGET_LABEL[ins.target_type]}{ins.target_value ? `: ${ins.target_value}` : ''}
            </span>
            {ins.period && <span className="text-xs text-gray-400">{ins.period}</span>}
            {ins.created_by_name && <span className="text-xs text-gray-400">• {ins.created_by_name}</span>}
          </div>
          <p className="text-sm font-medium text-gray-800">{ins.title}</p>
          <p className="text-sm text-gray-600 mt-0.5 whitespace-pre-wrap">{ins.content}</p>
          {ins.has_pdf && (
            <button
              onClick={() => openPdf(ins.id)}
              className="mt-2 inline-flex items-center gap-1 text-xs text-blue-600 hover:underline"
            >
              <FileText size={13} /> {ins.pdf_filename || '添付PDF'} <Download size={12} />
            </button>
          )}
        </div>
      ))}
    </div>
  )
}
