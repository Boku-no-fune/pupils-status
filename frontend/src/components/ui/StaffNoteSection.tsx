/**
 * スタッフ記録セクション
 * 電話報告・保護者面談・生徒ミーティングなどの記録入力
 * Web Speech API による音声入力対応
 */

import { useState, useRef } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Mic, MicOff, Plus, Trash2, ChevronDown, ChevronUp } from 'lucide-react'
import { studentsApi } from '@/api/students'
import type { StaffNote } from '@/types'

interface Props {
  studentId: number
  notes: StaffNote[]
}

const NOTE_TYPES = ['電話報告', '保護者面談', '生徒ミーティング', 'その他']

// Web Speech API の型定義
interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList
}
interface SpeechRecognitionResultList {
  [index: number]: SpeechRecognitionResult
  length: number
}
interface SpeechRecognitionResult {
  [index: number]: SpeechRecognitionAlternative
  isFinal: boolean
}
interface SpeechRecognitionAlternative {
  transcript: string
}

declare global {
  interface Window {
    SpeechRecognition?: new () => SpeechRecognitionInstance
    webkitSpeechRecognition?: new () => SpeechRecognitionInstance
  }
}
interface SpeechRecognitionInstance extends EventTarget {
  lang: string
  continuous: boolean
  interimResults: boolean
  start(): void
  stop(): void
  onresult: ((e: SpeechRecognitionEvent) => void) | null
  onend: (() => void) | null
}

export default function StaffNoteSection({ studentId, notes }: Props) {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [noteType, setNoteType] = useState(NOTE_TYPES[0])
  const [content, setContent] = useState('')
  const [occurredAt, setOccurredAt] = useState(
    new Date().toISOString().slice(0, 16)
  )
  const [isListening, setIsListening] = useState(false)
  const [showAll, setShowAll] = useState(false)
  const recognitionRef = useRef<SpeechRecognitionInstance | null>(null)

  const createMutation = useMutation({
    mutationFn: () =>
      studentsApi.createStaffNote(studentId, {
        note_type: noteType,
        content,
        occurred_at: new Date(occurredAt).toISOString(),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['student-detail', studentId] })
      setContent('')
      setShowForm(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (noteId: number) => studentsApi.deleteStaffNote(studentId, noteId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['student-detail', studentId] })
    },
  })

  // 音声入力の開始・停止
  const toggleVoice = () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) {
      alert('このブラウザは音声入力に対応していません')
      return
    }

    if (isListening) {
      recognitionRef.current?.stop()
      setIsListening(false)
      return
    }

    const recognition = new SR()
    recognition.lang = 'ja-JP'
    recognition.continuous = true
    recognition.interimResults = false
    recognition.onresult = (e: SpeechRecognitionEvent) => {
      const transcript = Array.from({ length: e.results.length }, (_, i) => e.results[i][0].transcript).join('')
      setContent((prev) => prev + transcript)
    }
    recognition.onend = () => setIsListening(false)
    recognition.start()
    recognitionRef.current = recognition
    setIsListening(true)
  }

  const displayNotes = showAll ? notes : notes.slice(0, 3)

  return (
    <div className="space-y-3">
      {/* 記録一覧 */}
      {notes.length === 0 ? (
        <p className="text-sm text-gray-400 text-center py-2">記録がありません</p>
      ) : (
        <>
          {displayNotes.map((note) => (
            <div key={note.id} className="border border-gray-100 rounded-lg p-3 bg-gray-50 group">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-semibold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full">
                      {note.note_type}
                    </span>
                    <span className="text-xs text-gray-400">
                      {new Date(note.occurred_at).toLocaleString('ja-JP', {
                        month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit',
                      })}
                    </span>
                    {note.teacher_name && (
                      <span className="text-xs text-gray-400">• {note.teacher_name}</span>
                    )}
                  </div>
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">{note.content}</p>
                </div>
                <button
                  onClick={() => deleteMutation.mutate(note.id)}
                  className="text-gray-300 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}

          {notes.length > 3 && (
            <button
              onClick={() => setShowAll(!showAll)}
              className="text-xs text-blue-600 hover:underline flex items-center gap-1"
            >
              {showAll ? <><ChevronUp size={12} />閉じる</> : <><ChevronDown size={12} />残り {notes.length - 3} 件を表示</>}
            </button>
          )}
        </>
      )}

      {/* 追加フォーム */}
      {showForm ? (
        <div className="border border-blue-200 rounded-lg p-3 bg-blue-50 space-y-2">
          {/* 種別・日時 */}
          <div className="flex gap-2 flex-wrap">
            <select
              value={noteType}
              onChange={(e) => setNoteType(e.target.value)}
              className="text-sm px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-400"
            >
              {NOTE_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
            <input
              type="datetime-local"
              value={occurredAt}
              onChange={(e) => setOccurredAt(e.target.value)}
              className="text-sm px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-400"
            />
          </div>

          {/* テキストエリア + 音声ボタン */}
          <div className="relative">
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="記録内容を入力してください..."
              rows={4}
              className="w-full text-sm px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-400 resize-none"
            />
            <button
              type="button"
              onClick={toggleVoice}
              title={isListening ? '音声入力を停止' : '音声入力を開始'}
              className={`absolute right-2 top-2 p-1.5 rounded-full transition-colors ${
                isListening
                  ? 'bg-red-100 text-red-500 animate-pulse'
                  : 'bg-gray-100 text-gray-400 hover:text-blue-500'
              }`}
            >
              {isListening ? <MicOff size={16} /> : <Mic size={16} />}
            </button>
          </div>
          {isListening && (
            <p className="text-xs text-red-500 flex items-center gap-1">
              <span className="w-2 h-2 bg-red-400 rounded-full animate-pulse inline-block" />
              音声入力中... マイクに向かって話してください
            </p>
          )}

          <div className="flex gap-2">
            <button
              onClick={() => createMutation.mutate()}
              disabled={!content.trim() || createMutation.isPending}
              className="text-sm px-4 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-40"
            >
              {createMutation.isPending ? '保存中...' : '保存'}
            </button>
            <button
              onClick={() => { setShowForm(false); setContent('') }}
              className="text-sm px-4 py-1.5 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              キャンセル
            </button>
          </div>
        </div>
      ) : (
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-700"
        >
          <Plus size={16} />
          記録を追加
        </button>
      )}
    </div>
  )
}
