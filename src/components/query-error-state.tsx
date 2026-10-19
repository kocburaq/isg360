import { RotateCw, TriangleAlert } from 'lucide-react'
import { getApiErrorMessage } from '@/lib/api-error'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'

type QueryErrorStateProps = {
  error: unknown
  /** Kullanıcıya hangi verinin yüklenemediğini söyler, ör. "Kameralar yüklenemedi". */
  title: string
  onRetry?: () => void
  isRetrying?: boolean
  compact?: boolean
  className?: string
}

/** API çağrısı başarısız olduğunda gösterilen, tekrar denenebilir hata kutusu. */
export function QueryErrorState({
  error,
  title,
  onRetry,
  isRetrying,
  compact,
  className,
}: QueryErrorStateProps) {
  const message =
    getApiErrorMessage(error) ??
    (error instanceof Error && error.message
      ? error.message
      : 'Beklenmeyen bir hata oluştu.')

  return (
    <div
      role='alert'
      className={cn(
        'flex flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-destructive/40 text-center',
        compact ? 'px-4 py-6' : 'py-14',
        className
      )}
    >
      <TriangleAlert className='size-6 text-destructive' />
      <p className='font-medium'>{title}</p>
      <p className='max-w-md px-4 text-sm text-muted-foreground'>{message}</p>
      {onRetry && (
        <Button
          variant='outline'
          size='sm'
          className='mt-1'
          onClick={onRetry}
          disabled={isRetrying}
        >
          <RotateCw className={cn(isRetrying && 'animate-spin')} />
          Tekrar dene
        </Button>
      )}
    </div>
  )
}
