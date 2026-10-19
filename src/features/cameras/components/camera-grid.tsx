import { CameraOff } from 'lucide-react'
import { Skeleton } from '@/components/ui/skeleton'
import { QueryErrorState } from '@/components/query-error-state'
import { type Camera } from '../types'
import { CameraTile } from './camera-tile'

type CameraGridProps = {
  cameras: Camera[]
  /** Filtre uygulanmadan önceki kamera sayısı (boş durum mesajı için). */
  totalCount: number
  isLoading: boolean
  error?: unknown
  onRetry?: () => void
  isRetrying?: boolean
  selectedId?: string
  openViolationsByCamera: Record<string, number>
  onSelect: (camera: Camera) => void
}

const GRID = 'grid gap-4 sm:grid-cols-2 2xl:grid-cols-3'

export function CameraGrid({
  cameras,
  totalCount,
  isLoading,
  error,
  onRetry,
  isRetrying,
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

  if (error && totalCount === 0) {
    return (
      <QueryErrorState
        title='Kameralar yüklenemedi'
        error={error}
        onRetry={onRetry}
        isRetrying={isRetrying}
      />
    )
  }

  if (cameras.length === 0) {
    const noCameras = totalCount === 0
    return (
      <div className='flex flex-col items-center justify-center gap-2 rounded-xl border border-dashed py-16 text-center text-muted-foreground'>
        <CameraOff className='size-8' />
        <p className='font-medium text-foreground'>
          {noCameras ? 'Henüz kayıtlı kamera yok' : 'Kamera bulunamadı'}
        </p>
        <p className='text-sm'>
          {noCameras
            ? 'Kamera eklendiğinde burada listelenecek.'
            : 'Arama veya filtre ölçütlerini değiştirin.'}
        </p>
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
