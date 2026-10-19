import { Link } from '@tanstack/react-router'
import { type ModuleDefinition } from '@/modules/registry'
import { ArrowRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'

type ModuleCardProps = {
  module: ModuleDefinition
}

export function ModuleCard({ module }: ModuleCardProps) {
  const isActive = module.status === 'active'
  const Icon = module.icon

  return (
    <Link
      to={module.url}
      className={cn(
        'group relative flex min-h-56 flex-col justify-between gap-6 rounded-xl border bg-card p-6 text-card-foreground shadow-sm transition-colors',
        'focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none',
        isActive
          ? 'hover:border-primary/60 hover:bg-accent/40'
          : 'hover:bg-muted/40'
      )}
    >
      <div className='flex items-start justify-between gap-4'>
        <div
          className={cn(
            'flex size-14 items-center justify-center rounded-lg',
            isActive
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted text-muted-foreground'
          )}
        >
          <Icon className='size-7' />
        </div>
        {isActive ? (
          <Badge className='border-success/30 bg-success/15 text-success'>
            Aktif
          </Badge>
        ) : (
          <Badge variant='secondary'>Yakında</Badge>
        )}
      </div>

      <div className='space-y-1.5'>
        <h2 className='text-xl font-semibold tracking-tight'>{module.title}</h2>
        <p className='text-sm text-muted-foreground'>{module.description}</p>
      </div>

      <div
        className={cn(
          'flex items-center gap-1.5 text-sm font-medium',
          isActive ? 'text-primary' : 'text-muted-foreground'
        )}
      >
        {isActive ? 'Modülü aç' : 'Planlanan özellikleri gör'}
        <ArrowRight className='size-4 transition-transform group-hover:translate-x-0.5 rtl:rotate-180' />
      </div>
    </Link>
  )
}
