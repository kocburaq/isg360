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
import { SERVICE_STATE } from '../config/status'
import { useCameraSummary } from '../hooks/use-camera-queries'

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

export function CameraSummaryCards() {
  const { summary, system, isLoading } = useCameraSummary()
  const systemMeta = system ? SERVICE_STATE[system.state] : null

  return (
    <div className='grid grid-cols-2 gap-3 sm:gap-4 xl:grid-cols-4'>
      <StatCard
        title='Toplam Kamera'
        icon={Cctv}
        value={summary.total}
        hint='Sisteme kayıtlı kamera sayısı'
        isLoading={isLoading}
      />
      <StatCard
        title='Aktif Kamera'
        icon={Activity}
        value={
          <>
            {summary.online}
            <span className='text-base font-medium text-muted-foreground'>
              {' '}
              / {summary.total}
            </span>
          </>
        }
        hint={
          summary.offline > 0
            ? `${summary.offline} kamera çevrimdışı`
            : 'Tüm kameralar çevrimiçi'
        }
        isLoading={isLoading}
      />
      <StatCard
        title='Tespit Edilen İhlal'
        icon={ShieldAlert}
        value={summary.violationsToday}
        valueClassName={summary.openViolations > 0 ? 'text-destructive' : ''}
        hint={`Bugün · ${summary.openViolations} açık ihlal (simüle)`}
        isLoading={isLoading}
      />
      <StatCard
        title='Sistem Durumu'
        icon={Server}
        value={systemMeta?.label ?? '—'}
        valueClassName={systemMeta?.className}
        hint={
          system?.state === 'simulated'
            ? 'Örnek veri; gerçek servis bağlı değil'
            : `${system?.services.length ?? 0} servis izleniyor`
        }
        isLoading={isLoading}
      />
    </div>
  )
}
