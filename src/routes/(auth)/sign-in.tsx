import { z } from 'zod'
import { createFileRoute, redirect } from '@tanstack/react-router'
import { getActiveSession } from '@/stores/auth-store'
import { SignIn } from '@/features/auth/sign-in'

const searchSchema = z.object({
  redirect: z.string().optional(),
})

export const Route = createFileRoute('/(auth)/sign-in')({
  validateSearch: searchSchema,
  beforeLoad: () => {
    if (getActiveSession()) throw redirect({ to: '/' })
  },
  component: SignIn,
})
