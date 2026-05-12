/**
 * 顔写真アップロードコンポーネント
 * ファイル選択 → Base64変換 → API保存
 */

import { useRef, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Camera, Trash2 } from 'lucide-react'
import { studentsApi } from '@/api/students'

interface Props {
  studentId: number
  photoData?: string
}

export default function PhotoUpload({ studentId, photoData }: Props) {
  const fileRef = useRef<HTMLInputElement>(null)
  const queryClient = useQueryClient()
  const [preview, setPreview] = useState<string | null>(photoData || null)

  const saveMutation = useMutation({
    mutationFn: (data: string | null) => studentsApi.uploadPhoto(studentId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['student-detail', studentId] })
    },
  })

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = () => {
      const base64 = reader.result as string
      setPreview(base64)
      saveMutation.mutate(base64)
    }
    reader.readAsDataURL(file)
  }

  const handleDelete = () => {
    setPreview(null)
    saveMutation.mutate(null)
  }

  return (
    <div className="flex flex-col items-center gap-2">
      {/* 写真表示 */}
      <div
        className="w-20 h-20 rounded-full overflow-hidden bg-blue-100 flex items-center justify-center cursor-pointer border-2 border-blue-200 hover:border-blue-400 transition-colors"
        onClick={() => fileRef.current?.click()}
        title="クリックして写真を変更"
      >
        {preview ? (
          <img src={preview} alt="顔写真" className="w-full h-full object-cover" />
        ) : (
          <Camera size={28} className="text-blue-400" />
        )}
      </div>

      {/* ボタン */}
      <div className="flex gap-1">
        <button
          onClick={() => fileRef.current?.click()}
          className="text-xs text-blue-600 hover:underline"
        >
          {preview ? '変更' : '写真を追加'}
        </button>
        {preview && (
          <>
            <span className="text-gray-300">|</span>
            <button
              onClick={handleDelete}
              className="text-xs text-red-500 hover:underline flex items-center gap-0.5"
            >
              <Trash2 size={10} />削除
            </button>
          </>
        )}
      </div>

      {/* 非表示ファイル入力 */}
      <input
        ref={fileRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleFileChange}
      />

      {saveMutation.isPending && (
        <span className="text-xs text-gray-400">保存中...</span>
      )}
    </div>
  )
}
