import { z } from 'zod'
import { createFileRoute } from '@tanstack/react-router'
import { Cameras } from '@/features/cameras'

const searchSchema = z.object({
  /** Ayrıntı panelinde açık olan kamera. */
  camera: z.string().optional(),
  tab: z.enum(['cameras', 'history']).optional(),
})

export const Route = createFileRoute('/_authenticated/cameras/')({
  validateSearch: searchSchema,
  component: Cameras,
})
