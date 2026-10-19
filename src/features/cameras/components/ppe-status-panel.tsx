import { formatTime } from '@/lib/format'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { getPpeClass, PLANNED_PPE_CLASSES } from '../config/ppe-classes'
import { CHECK_STATE } from '../config/status'
import { summarizeDetections } from '../lib/ppe'
import {
  type Camera,
  type DetectionSnapshot,
  type PpeCheckState,
} from '../types'

type PpeStatusPanelProps = {
  camera: Camera
  snapshot: DetectionSnapshot | null | undefined
  isLoading: boolean
}

const STATES: PpeCheckState[] = ['compliant', 'violation', 'unknown']

/** Seçili kameradaki KKD tespit durumlarının sınıf bazlı özeti. */
export function PpeStatusPanel({
  camera,
  snapshot,
  isLoading,
}: PpeStatusPanelProps) {
  if (isLoading) return <Skeleton className='h-36 w-full' />

  const summaries = summarizeDetections(snapshot, camera.ppeClasses)
  const personCount = snapshot?.persons.length ?? 0

  return (
    <div className='space-y-3'>
      <div className='flex flex-wrap items-center justify-between gap-2 text-xs text-muted-foreground'>
        <span>
          {camera.status === 'offline'
            ? 'Kamera çevrimdışı — tespit yapılamıyor.'
            : snapshot
              ? `${personCount} kişi tespit edildi · ${formatTime(snapshot.capturedAt)}`
              : 'Tespit kaydı yok.'}
        </span>
        {snapshot?.source === 'simulation' && (
          <Badge variant='outline' className='border-warning/40 text-warning'>
            Simüle edilmiş tespit
          </Badge>
        )}
      </div>

      <ul className='divide-y rounded-lg border'>
        {summaries.map(({ classId, counts }) => {
          const ppe = getPpeClass(classId)
          const Icon = ppe.icon
          return (
            <li key={classId} className='flex items-center gap-3 p-3'>
              <div className='flex size-9 items-center justify-center rounded-md bg-muted'>
                <Icon className='size-4' />
              </div>
              <div className='flex-1'>
                <p className='text-sm font-medium'>{ppe.label}</p>
                <p className='text-xs text-muted-foreground'>
                  {counts.violation > 0
                    ? `${counts.violation} kişide eksik`
                    : personCount > 0
                      ? 'Eksik tespit edilmedi'
                      : 'Değerlendirilecek kişi yok'}
                </p>
              </div>
              <dl className='flex gap-3 text-center'>
                {STATES.map((state) => (
                  <div key={state} className='min-w-12'>
                    <dt className='text-[11px] text-muted-foreground'>
                      {CHECK_STATE[state].label}
                    </dt>
                    <dd
                      className={cn(
                        'text-sm font-semibold tabular-nums',
                        counts[state] > 0 && CHECK_STATE[state].className
                      )}
                    >
                      {counts[state]}
                    </dd>
                  </div>
                ))}
              </dl>
            </li>
          )
        })}
      </ul>

      <div className='flex flex-wrap items-center gap-1.5'>
        <span className='text-xs text-muted-foreground'>
          Planlanan sınıflar:
        </span>
        {PLANNED_PPE_CLASSES.map((ppe) => (
          <Badge key={ppe.id} variant='secondary' className='font-normal'>
            <ppe.icon />
            {ppe.label}
          </Badge>
        ))}
      </div>
    </div>
  )
}
