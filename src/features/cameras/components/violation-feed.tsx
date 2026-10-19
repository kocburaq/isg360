import { BellRing, ShieldCheck } from 'lucide-react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { QueryErrorState } from '@/components/query-error-state'
import { useViolations } from '../hooks/use-camera-queries'
import { type Camera } from '../types'
import { ViolationItem } from './violation-item'

type ViolationFeedProps = {
  camerasById: Map<string, Camera>
  onSelectCamera: (cameraId: string) => void
}

/** Açık ve incelenmekte olan ihlallerin bildirim listesi. */
export function ViolationFeed({
  camerasById,
  onSelectCamera,
}: ViolationFeedProps) {
  const { data, isLoading, error, refetch, isFetching } = useViolations({
    status: ['open', 'acknowledged'],
  })
  const openCount = data?.filter((v) => v.status === 'open').length ?? 0

  return (
    <Card className='gap-0 py-0'>
      <CardHeader className='border-b px-4 py-4'>
        <CardTitle className='flex items-center gap-2 text-base'>
          <BellRing className='size-4' />
          İhlal Bildirimleri
        </CardTitle>
        <CardDescription>
          {openCount > 0
            ? `${openCount} açık bildirim`
            : 'Açık bildirim bulunmuyor'}{' '}
          · simüle edilmiş kayıtlar
        </CardDescription>
      </CardHeader>
      <CardContent className='p-0'>
        {isLoading ? (
          <div className='space-y-2 p-3'>
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className='h-16 w-full' />
            ))}
          </div>
        ) : error && !data ? (
          <QueryErrorState
            compact
            className='m-3'
            title='Bildirimler yüklenemedi'
            error={error}
            onRetry={() => void refetch()}
            isRetrying={isFetching}
          />
        ) : data && data.length > 0 ? (
          <div className='max-h-[32rem] overflow-y-auto'>
            <ul className='divide-y'>
              {data.map((violation) => (
                <ViolationItem
                  key={violation.id}
                  violation={violation}
                  camera={camerasById.get(violation.cameraId)}
                  onSelectCamera={onSelectCamera}
                />
              ))}
            </ul>
          </div>
        ) : (
          <div className='flex flex-col items-center gap-2 px-4 py-10 text-center text-sm text-muted-foreground'>
            <ShieldCheck className='size-6 text-success' />
            Bekleyen ihlal bildirimi yok.
          </div>
        )}
      </CardContent>
    </Card>
  )
}
