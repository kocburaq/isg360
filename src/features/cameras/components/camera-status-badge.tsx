import { CircleHelp, Wifi, WifiOff } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { CAMERA_STATUS } from '../config/status'
import { type CameraStatus } from '../types'

type CameraStatusBadgeProps = {
  status: CameraStatus
  className?: string
}

export function CameraStatusBadge({
  status,
  className,
}: CameraStatusBadgeProps) {
  const meta = CAMERA_STATUS[status]
  const Icon =
    status === 'online' ? Wifi : status === 'offline' ? WifiOff : CircleHelp
  return (
    <Badge variant='outline' className={cn(meta.className, className)}>
      <Icon />
      {meta.label}
    </Badge>
  )
}
