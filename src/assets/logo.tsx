import { type SVGProps } from 'react'
import { cn } from '@/lib/utils'

/** Factory Control System logosu (fabrika silueti). */
export function Logo({ className, ...props }: SVGProps<SVGSVGElement>) {
  return (
    <svg
      id='fcs-logo'
      viewBox='0 0 24 24'
      xmlns='http://www.w3.org/2000/svg'
      height='24'
      width='24'
      fill='none'
      stroke='currentColor'
      strokeWidth='2'
      strokeLinecap='round'
      strokeLinejoin='round'
      className={cn('size-6', className)}
      {...props}
    >
      <title>Factory Control System</title>
      <path d='M2 20h20' />
      <path d='M3 20V9l5 3V9l5 3V9l5 3V4h3v16' />
      <path d='M7 16h2M12 16h2M17 16h1' />
    </svg>
  )
}
