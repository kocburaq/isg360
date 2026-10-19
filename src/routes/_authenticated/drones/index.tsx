import { createFileRoute } from '@tanstack/react-router'
import { Drones } from '@/features/drones'

export const Route = createFileRoute('/_authenticated/drones/')({
  component: Drones,
})
