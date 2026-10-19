import { VideoOff } from 'lucide-react'
import { cn } from '@/lib/utils'
import { getPpeClass } from '../config/ppe-classes'
import { personState } from '../lib/ppe'
import { type Camera, type DetectionSnapshot } from '../types'

type SimulatedFeedProps = {
  camera: Camera
  snapshot?: DetectionSnapshot | null
  /** Kutucuklarda küçük, ayrıntı panelinde büyük etiketler. */
  size?: 'sm' | 'lg'
  className?: string
}

const BOX_STYLE = {
  compliant: 'border-success bg-success/10',
  violation: 'border-destructive bg-destructive/15',
  unknown: 'border-warning bg-warning/10',
} as const

/**
 * Kamera görüntüsü YER TUTUCUSU.
 * Gerçek video akışı göstermez; örnek bir sahne ve simüle edilmiş tespit
 * kutuları çizer. RTSP/WebRTC entegrasyonunda bu bileşen bir video oynatıcı
 * ile değiştirilecek, kutu katmanı (overlay) aynen korunabilir.
 */
export function SimulatedFeed({
  camera,
  snapshot,
  size = 'sm',
  className,
}: SimulatedFeedProps) {
  const isOffline = camera.status === 'offline'

  return (
    <div
      className={cn(
        'relative aspect-video w-full overflow-hidden rounded-md bg-slate-900 text-slate-100',
        className
      )}
      role='img'
      aria-label={`${camera.name} için örnek görüntü (simülasyon)`}
    >
      {isOffline ? (
        <div className='flex h-full flex-col items-center justify-center gap-2 bg-[repeating-linear-gradient(45deg,transparent_0_12px,rgb(255_255_255/0.03)_12px_24px)] text-slate-400'>
          <VideoOff className={size === 'lg' ? 'size-10' : 'size-7'} />
          <span className='text-sm font-medium'>Sinyal yok</span>
        </div>
      ) : (
        <>
          {/* Örnek sahne: zemin, raf/duvar hatları */}
          <div
            aria-hidden='true'
            className='absolute inset-0 bg-[linear-gradient(180deg,#1e293b_0%,#0f172a_55%,#334155_100%)]'
          />
          <div
            aria-hidden='true'
            className='absolute inset-x-0 bottom-0 h-[38%] origin-bottom [transform:perspective(200px)_rotateX(35deg)] bg-[repeating-linear-gradient(90deg,rgb(255_255_255/0.05)_0_1px,transparent_1px_10%)]'
          />
          <div
            aria-hidden='true'
            className='absolute inset-x-[6%] top-[14%] h-[30%] border border-slate-600/40 bg-[repeating-linear-gradient(90deg,rgb(148_163_184/0.08)_0_14%,transparent_14%_16%)]'
          />

          {/* Simüle edilmiş tespit kutuları */}
          {snapshot?.persons.map((person) => {
            const state = personState(person)
            const missing = person.checks
              .filter((c) => c.state === 'violation')
              .map((c) => getPpeClass(c.classId).shortLabel)
            return (
              <div
                key={person.id}
                className={cn('absolute rounded-sm border-2', BOX_STYLE[state])}
                style={{
                  left: `${person.box.x * 100}%`,
                  top: `${person.box.y * 100}%`,
                  width: `${person.box.width * 100}%`,
                  height: `${person.box.height * 100}%`,
                }}
              >
                {size === 'lg' && (
                  <span
                    className={cn(
                      'absolute -top-5 left-0 rounded-sm px-1 text-[10px] leading-4 font-medium whitespace-nowrap',
                      state === 'violation'
                        ? 'bg-destructive text-white'
                        : state === 'unknown'
                          ? 'bg-warning text-slate-900'
                          : 'bg-success text-slate-900'
                    )}
                  >
                    {state === 'violation'
                      ? `Eksik: ${missing.join(', ')}`
                      : state === 'unknown'
                        ? 'Belirsiz'
                        : 'Uyumlu'}
                  </span>
                )}
              </div>
            )
          })}
        </>
      )}

      {/* Bu görüntünün gerçek olmadığını her zaman belirt */}
      <span className='absolute end-2 bottom-2 rounded-sm bg-black/60 px-1.5 py-0.5 text-[10px] font-semibold tracking-wide text-amber-300 uppercase'>
        Örnek görüntü · Simülasyon
      </span>
    </div>
  )
}
