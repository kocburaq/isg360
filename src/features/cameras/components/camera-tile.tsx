import { MapPin, ShieldAlert } from 'lucide-react'
import { formatRelative } from '@/lib/format'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { useCameraDetections } from '../hooks/use-camera-queries'
import { type Camera } from '../types'
import { CameraStatusBadge } from './camera-status-badge'
import { SimulatedFeed } from './simulated-feed'

type CameraTileProps = {
  camera: Camera
  openViolations: number
  selected: boolean
  onSelect: (camera: Camera) => void
}

export function CameraTile({
  camera,
  openViolations,
  selected,
  onSelect,
}: CameraTileProps) {
  const { data: snapshot } = useCameraDetections(
    camera.status === 'online' ? camera.id : undefined
  )

  return (
    <button
      type='button'
      onClick={() => onSelect(camera)}
      aria-pressed={selected}
      className={cn(
        'group flex flex-col gap-3 rounded-xl border bg-card p-2.5 text-start text-card-foreground shadow-sm transition-colors',
        'hover:border-primary/50 focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none',
        selected && 'border-primary ring-1 ring-primary'
      )}
    >
      <div className='relative'>
        <SimulatedFeed camera={camera} snapshot={snapshot} />
        <div className='absolute start-2 top-2 flex items-center gap-1.5'>
          <span className='rounded-sm bg-black/60 px-1.5 py-0.5 font-mono text-xs font-semibold text-white'>
            {camera.code}
          </span>
          {openViolations > 0 && (
            <Badge className='bg-destructive text-white'>
              <ShieldAlert />
              {openViolations} ihlal
            </Badge>
          )}
        </div>
      </div>

      <div className='flex items-start justify-between gap-2 px-1 pb-0.5'>
        <div className='min-w-0 space-y-1'>
          <p className='truncate font-medium'>{camera.name}</p>
          <p className='flex items-center gap-1 truncate text-xs text-muted-foreground'>
            <MapPin className='size-3 shrink-0' />
            {camera.zone.name} · {camera.zone.area}
          </p>
        </div>
        <div className='flex shrink-0 flex-col items-end gap-1'>
          <CameraStatusBadge status={camera.status} />
          {camera.status === 'offline' && (
            <span className='text-[11px] text-muted-foreground'>
              {formatRelative(camera.lastSeenAt)}
            </span>
          )}
        </div>
      </div>
    </button>
  )
}
