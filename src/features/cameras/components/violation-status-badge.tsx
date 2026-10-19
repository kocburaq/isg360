import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { VIOLATION_STATUS } from '../config/status'
import { type ViolationStatus } from '../types'

export function ViolationStatusBadge({
  status,
  className,
}: {
  status: ViolationStatus
  className?: string
}) {
  const meta = VIOLATION_STATUS[status]
  return (
    <Badge variant='outline' className={cn(meta.className, className)}>
      {meta.label}
    </Badge>
  )
}
