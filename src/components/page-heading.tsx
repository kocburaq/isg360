import { cn } from '@/lib/utils'

type PageHeadingProps = {
  title: string
  description?: React.ReactNode
  /** Başlığın sağında gösterilen eylemler veya etiketler. */
  actions?: React.ReactNode
  className?: string
}

export function PageHeading({
  title,
  description,
  actions,
  className,
}: PageHeadingProps) {
  return (
    <div
      className={cn(
        'flex flex-wrap items-end justify-between gap-x-4 gap-y-2',
        className
      )}
    >
      <div className='space-y-1'>
        <h1 className='text-2xl font-bold tracking-tight'>{title}</h1>
        {description && (
          <p className='text-sm text-muted-foreground'>{description}</p>
        )}
      </div>
      {actions && <div className='flex items-center gap-2'>{actions}</div>}
    </div>
  )
}
