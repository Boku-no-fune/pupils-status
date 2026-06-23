/**
 * Tab: 通塾元・通学校マップ
 * 生徒の自宅(通塾元)と通学校を Leaflet + OpenStreetMap 上にプロット。
 * ※モックアップのため座標は東京都内のダミーデータ。
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { MapContainer, TileLayer, CircleMarker, Popup, Polyline } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { dashboardApi } from '@/api/dashboard'
import { useViewStore } from '@/stores/viewStore'
import { gradeLabel } from '@/components/ui/GradeLabel'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

export default function MapTab() {
  const showAll = useViewStore((s) => s.showAll)
  const { data, isLoading, isError } = useQuery({ queryKey: ['map-data', showAll], queryFn: () => dashboardApi.mapData(showAll) })
  const [showHomes, setShowHomes] = useState(true)
  const [showSchools, setShowSchools] = useState(true)
  const [showLines, setShowLines] = useState(false)

  if (isLoading) return <LoadingSpinner text="地図データを読み込み中..." />
  if (isError || !data) return <div className="text-center text-red-500 py-8">データの取得に失敗しました</div>

  const center: [number, number] = [data.classroom.lat, data.classroom.lng]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h3 className="text-base font-semibold text-gray-800">通塾元・通学校マップ</h3>
          <p className="text-xs text-gray-400">生徒の自宅と通学校の分布（東京都内ダミーデータ）</p>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <label className="flex items-center gap-1.5 cursor-pointer">
            <input type="checkbox" checked={showHomes} onChange={(e) => setShowHomes(e.target.checked)} className="accent-blue-600" />
            <span className="w-3 h-3 rounded-full bg-blue-500 inline-block" /> 自宅
          </label>
          <label className="flex items-center gap-1.5 cursor-pointer">
            <input type="checkbox" checked={showSchools} onChange={(e) => setShowSchools(e.target.checked)} className="accent-orange-500" />
            <span className="w-3 h-3 rounded-full bg-orange-500 inline-block" /> 通学校
          </label>
          <label className="flex items-center gap-1.5 cursor-pointer">
            <input type="checkbox" checked={showLines} onChange={(e) => setShowLines(e.target.checked)} className="accent-gray-400" />
            自宅↔学校の線
          </label>
        </div>
      </div>

      <div className="rounded-xl overflow-hidden border border-gray-200" style={{ height: 560 }}>
        <MapContainer center={center} zoom={13} style={{ height: '100%', width: '100%' }} scrollWheelZoom>
          <TileLayer
            attribution='&copy; OpenStreetMap contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* 教室 */}
          <CircleMarker center={center} radius={10} pathOptions={{ color: '#16a34a', fillColor: '#22c55e', fillOpacity: 0.9, weight: 2 }}>
            <Popup><strong>{data.classroom.name}</strong><br />（教室）</Popup>
          </CircleMarker>

          {/* 自宅↔学校の線 */}
          {showLines && data.students.map((s) =>
            s.school_lat != null && s.school_lng != null ? (
              <Polyline
                key={`line-${s.id}`}
                positions={[[s.home_lat, s.home_lng], [s.school_lat, s.school_lng]]}
                pathOptions={{ color: '#94a3b8', weight: 1, opacity: 0.4 }}
              />
            ) : null
          )}

          {/* 通学校 (重複排除、通学者数で半径) */}
          {showSchools && data.schools.map((sc) => (
            <CircleMarker
              key={`school-${sc.name}`}
              center={[sc.lat, sc.lng]}
              radius={6 + Math.min(sc.count, 12)}
              pathOptions={{ color: '#ea580c', fillColor: '#fb923c', fillOpacity: 0.6, weight: 1 }}
            >
              <Popup><strong>{sc.name}</strong><br />通学者 {sc.count} 名</Popup>
            </CircleMarker>
          ))}

          {/* 自宅 */}
          {showHomes && data.students.map((s) => (
            <CircleMarker
              key={`home-${s.id}`}
              center={[s.home_lat, s.home_lng]}
              radius={5}
              pathOptions={{ color: '#2563eb', fillColor: '#3b82f6', fillOpacity: 0.7, weight: 1 }}
            >
              <Popup>
                <strong>{s.name}</strong>（{gradeLabel(s.grade)}）<br />
                {s.class_label && <>クラス: {s.class_label}<br /></>}
                通学校: {s.school || '—'}<br />
                {s.address && <span className="text-gray-500">{s.address}</span>}
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      <p className="text-xs text-gray-400">
        ● 緑: 教室 / ● 青: 生徒の自宅（通塾元） / ● 橙: 通学校（円の大きさ＝通学者数）。マーカーをクリックで詳細表示。
      </p>
    </div>
  )
}
