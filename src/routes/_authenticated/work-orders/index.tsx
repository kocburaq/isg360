import { createFileRoute } from '@tanstack/react-router'
import { WorkOrders } from '@/features/work-orders'

export const Route = createFileRoute('/_authenticated/work-orders/')({
  component: WorkOrders,
})
