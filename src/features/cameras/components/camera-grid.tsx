import { CameraOff } from 'lucide-react'
import { Skeleton } from '@/components/ui/skeleton'
import { type Camera } from '../types'
import { CameraTile } from './camera-tile'

type CameraGridProps = {
  cameras: Camera[]
  isLoading: boolean
  selectedId?: string
  openViolationsByCamera: Record<string, number>
  onSelect: (camera: Camera) => void
}

const GRID = 'grid gap-4 sm:grid-cols-2 2xl:grid-cols-3'

export function CameraGrid({
  cameras,
  isLoading,
  selectedId,
  openViolationsByCamera,
  onSelect,
}: CameraGridProps) {
  if (isLoading) {
    return (
      <div className={GRID}>
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className='aspect-[16/11] rounded-xl' />
        ))}
      </div>
    )
  }

  if (cameras.length === 0) {
    return (
      <div className='flex flex-col items-center justify-center gap-2 rounded-xl border border-dashed py-16 text-center text-muted-foreground'>
        <CameraOff className='size-8' />
        <p className='font-medium text-foreground'>Kamera bulunamadı</p>
        <p className='text-sm'>Arama veya filtre ölçütlerini değiştirin.</p>
      </div>
    )
  }

  return (
    <div className={GRID}>
      {cameras.map((camera) => (
        <CameraTile
          key={camera.id}
          camera={camera}
          openViolations={openViolationsByCamera[camera.id] ?? 0}
          selected={camera.id === selectedId}
          onSelect={onSelect}
        />
      ))}
    </div>
  )
}
