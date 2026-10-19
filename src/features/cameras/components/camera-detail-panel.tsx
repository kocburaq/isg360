import { useState } from 'react'
import { History, Info, ShieldCheck } from 'lucide-react'
import { formatDateTime, formatRelative } from '@/lib/format'
import { Separator } from '@/components/ui/separator'
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import { Skeleton } from '@/components/ui/skeleton'
import { useCameraDetections, useViolations } from '../hooks/use-camera-queries'
import { type Camera } from '../types'
import { CameraStatusBadge } from './camera-status-badge'
import { PpeStatusPanel } from './ppe-status-panel'
import { SimulatedFeed } from './simulated-feed'
import { ViolationItem } from './violation-item'

type CameraDetailPanelProps = {
  camera: Camera | undefined
  onClose: () => void
}

function Section({
  title,
  icon: Icon,
  children,
}: {
  title: string
  icon: React.ElementType
  children: React.ReactNode
}) {
  return (
    <section className='space-y-3'>
      <h3 className='flex items-center gap-2 text-sm font-semibold'>
        <Icon className='size-4 text-muted-foreground' />
        {title}
      </h3>
      {children}
    </section>
  )
}

export function CameraDetailPanel({ camera, onClose }: CameraDetailPanelProps) {
  // Kapanma animasyonu sırasında içeriğin boşalmaması için son kamera korunur.
  const [shown, setShown] = useState(camera)
  if (camera && camera !== shown) setShown(camera)

  return (
    <Sheet open={!!camera} onOpenChange={(open) => !open && onClose()}>
      <SheetContent className='w-full gap-0 sm:max-w-xl'>
        {shown && <CameraDetailContent camera={shown} />}
      </SheetContent>
    </Sheet>
  )
}

function CameraDetailContent({ camera }: { camera: Camera }) {
  const detections = useCameraDetections(
    camera.status === 'online' ? camera.id : undefined
  )
  const violations = useViolations({ cameraId: camera.id })

  const info: [string, React.ReactNode][] = [
    ['Kamera kodu', <span className='font-mono'>{camera.code}</span>],
    ['Bölge', `${camera.zone.name} (${camera.zone.area})`],
    ['Konum', camera.location],
    [
      'Akış',
      `${camera.stream.protocol.toUpperCase()} · ${camera.stream.resolution} · ${camera.stream.fps} fps`,
    ],
    [
      'Bağlantı',
      camera.stream.configured
        ? 'Yapılandırıldı'
        : 'Yapılandırılmadı (prototip)',
    ],
    [
      'Son sinyal',
      <span title={formatDateTime(camera.lastSeenAt)}>
        {formatRelative(camera.lastSeenAt)}
      </span>,
    ],
  ]

  return (
    <>
      <SheetHeader className='border-b pe-12'>
        <div className='flex items-center gap-2'>
          <SheetTitle className='text-lg'>{camera.name}</SheetTitle>
          <CameraStatusBadge status={camera.status} />
        </div>
        <SheetDescription>
          {camera.code} · {camera.zone.name}
        </SheetDescription>
      </SheetHeader>

      <div className='flex-1 space-y-6 overflow-y-auto p-4'>
        <SimulatedFeed
          camera={camera}
          snapshot={detections.data}
          size='lg'
          className='rounded-lg'
        />

        <Section title='KKD Denetimi' icon={ShieldCheck}>
          <PpeStatusPanel
            camera={camera}
            snapshot={detections.data}
            isLoading={detections.isLoading}
          />
        </Section>

        <Separator />

        <Section title='Kamera Bilgileri' icon={Info}>
          <dl className='grid grid-cols-[auto_1fr] gap-x-6 gap-y-2 text-sm'>
            {info.map(([label, value]) => (
              <div key={label} className='contents'>
                <dt className='text-muted-foreground'>{label}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
        </Section>

        <Separator />

        <Section title='Son İhlaller' icon={History}>
          {violations.isLoading ? (
            <Skeleton className='h-24 w-full' />
          ) : violations.data && violations.data.length > 0 ? (
            <ul className='divide-y rounded-lg border'>
              {violations.data.slice(0, 5).map((v) => (
                <ViolationItem key={v.id} violation={v} hideCamera />
              ))}
            </ul>
          ) : (
            <p className='text-sm text-muted-foreground'>
              Bu kamera için ihlal kaydı yok.
            </p>
          )}
        </Section>
      </div>
    </>
  )
}
