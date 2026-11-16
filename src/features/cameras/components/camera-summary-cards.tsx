import {
  Activity,
  Cctv,
  Server,
  ShieldAlert,
  type LucideIcon,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { QueryErrorState } from '@/components/query-error-state'
import { SERVICE_STATE } from '../config/status'
import { useCameraSummary } from '../hooks/use-camera-queries'
import { type CameraSummary } from '../types'

type StatCardProps = {
  title: string
  icon: LucideIcon
  value: React.ReactNode
  hint: React.ReactNode
  valueClassName?: string
  isLoading?: boolean
}

function StatCard({
  title,
  icon: Icon,
  value,
  hint,
  valueClassName,
  isLoading,
}: StatCardProps) {
  return (
    <Card className='gap-2 py-4'>
      <CardHeader className='flex flex-row items-center justify-between px-4'>
        <CardTitle className='text-sm font-medium text-muted-foreground'>
          {title}
        </CardTitle>
        <Icon className='size-4 text-muted-foreground' />
      </CardHeader>
      <CardContent className='space-y-1 px-4'>
        {isLoading ? (
          <Skeleton className='h-8 w-20' />
        ) : (
          <div className={cn('text-2xl font-bold', valueClassName)}>
            {value}
          </div>
        )}
        <p className='text-xs text-muted-foreground'>{hint}</p>
      </CardContent>
    </Card>
  )
}

function cameraHint(cameras: CameraSummary['cameras'] | undefined): string {
  if (!cameras) return ''
  const parts: string[] = []
  if (cameras.offline > 0) parts.push(`${cameras.offline} çevrimdışı`)
  if (cameras.unknown > 0) parts.push(`${cameras.unknown} durumu bilinmiyor`)
  return parts.length > 0 ? parts.join(' · ') : 'Tüm kameralar çevrimiçi'
}

export function CameraSummaryCards({ factoryId }: { factoryId?: string }) {
  const { summary, system, isLoading, error, refetch, isRefetching } =
    useCameraSummary(factoryId)

  if (error && !summary) {
    return (
      <QueryErrorState
        compact
        title='Özet bilgiler yüklenemedi'
        error={error}
        onRetry={refetch}
        isRetrying={isRefetching}
      />
    )
  }

  const cameras = summary?.cameras
  const violations = summary?.violations
  const systemMeta = system ? SERVICE_STATE[system.state] : null
  const services = system?.services ?? []
  const operational = services.filter((s) => s.state === 'operational').length
  const simulated = services.filter((s) => s.state === 'simulated').length
  const openCount = violations?.open ?? 0

  return (
    <div className='grid grid-cols-2 gap-3 sm:gap-4 xl:grid-cols-4'>
      <StatCard
        title='Toplam Kamera'
        icon={Cctv}
        value={cameras?.total ?? '—'}
        hint='Sisteme kayıtlı kamera sayısı'
        isLoading={isLoading}
      />
      <StatCard
        title='Aktif Kamera'
        icon={Activity}
        value={
          <>
            {cameras?.online ?? '—'}
            <span className='text-base font-medium text-muted-foreground'>
              {' '}
              / {cameras?.total ?? '—'}
            </span>
          </>
        }
        hint={cameraHint(cameras)}
        isLoading={isLoading}
      />
      <StatCard
        title='Tespit Edilen İhlal'
        icon={ShieldAlert}
        value={violations?.today ?? '—'}
        valueClassName={openCount > 0 ? 'text-destructive' : ''}
        hint={`Bugün · ${openCount} açık ihlal${summary?.containsSimulatedData ? ' (simüle)' : ''}`}
        isLoading={isLoading}
      />
      <StatCard
        title='Sistem Durumu'
        icon={Server}
        value={systemMeta?.label ?? '—'}
        valueClassName={systemMeta?.className}
        hint={
          simulated > 0
            ? `${operational} servis çalışıyor · ${simulated} simülasyon`
            : `${operational}/${services.length} servis çalışıyor`
        }
        isLoading={isLoading}
      />
    </div>
  )
}
