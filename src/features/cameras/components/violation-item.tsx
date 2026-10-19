import { Check, CheckCheck } from 'lucide-react'
import { formatDateTime, formatPercent, formatRelative } from '@/lib/format'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { getPpeClass } from '../config/ppe-classes'
import { VIOLATION_SEVERITY } from '../config/status'
import { useUpdateViolationStatus } from '../hooks/use-camera-queries'
import { type Camera, type PpeViolation } from '../types'
import { ViolationStatusBadge } from './violation-status-badge'

type ViolationItemProps = {
  violation: PpeViolation
  camera?: Camera
  /** Kamera bilgisini gizle (ör. kamera ayrıntı panelinde). */
  hideCamera?: boolean
  onSelectCamera?: (cameraId: string) => void
}

export function ViolationItem({
  violation,
  camera,
  hideCamera,
  onSelectCamera,
}: ViolationItemProps) {
  const update = useUpdateViolationStatus()
  const severity = VIOLATION_SEVERITY[violation.severity]
  const isPending = update.isPending

  return (
    <li className='space-y-2 p-3'>
      <div className='flex items-start justify-between gap-2'>
        <div className='min-w-0 space-y-1'>
          <div className='flex flex-wrap items-center gap-1.5'>
            {violation.missing.map((id) => {
              const ppe = getPpeClass(id)
              return (
                <span
                  key={id}
                  className='inline-flex items-center gap-1 text-sm font-medium'
                >
                  <ppe.icon className='size-3.5 text-destructive' />
                  {ppe.label} yok
                </span>
              )
            })}
          </div>
          {!hideCamera && camera && (
            <button
              type='button'
              className='truncate text-xs text-muted-foreground hover:text-foreground hover:underline'
              onClick={() => onSelectCamera?.(camera.id)}
            >
              {camera.code} · {camera.name}
            </button>
          )}
        </div>
        <ViolationStatusBadge status={violation.status} />
      </div>

      <div className='flex flex-wrap items-center justify-between gap-2'>
        <p
          className='text-xs text-muted-foreground'
          title={formatDateTime(violation.detectedAt)}
        >
          {formatRelative(violation.detectedAt)} ·{' '}
          <span className={cn(severity.className)}>{severity.label} önem</span>{' '}
          · Güven {formatPercent(violation.confidence)}
        </p>
        {violation.status !== 'resolved' && (
          <div className='flex gap-1'>
            {violation.status === 'open' && (
              <Button
                size='sm'
                variant='outline'
                className='h-7 px-2 text-xs'
                disabled={isPending}
                onClick={() =>
                  update.mutate({ id: violation.id, status: 'acknowledged' })
                }
              >
                <Check />
                İncelendi
              </Button>
            )}
            <Button
              size='sm'
              variant='outline'
              className='h-7 px-2 text-xs'
              disabled={isPending}
              onClick={() =>
                update.mutate({ id: violation.id, status: 'resolved' })
              }
            >
              <CheckCheck />
              Çözüldü
            </Button>
          </div>
        )}
      </div>
    </li>
  )
}
