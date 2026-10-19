import { useAuthStore } from '@/stores/auth-store'
import { getDisplayNameInitials } from '@/lib/utils'

/** Oturumdaki kullanıcı ve görüntüleme yardımcıları. */
export function useCurrentUser() {
  const session = useAuthStore((s) => s.session)
  const user = session?.user ?? null

  return {
    user,
    initials: user ? getDisplayNameInitials(user.displayName) : '?',
    isDemo: session?.mode === 'demo',
    roleLabel: user?.role === 'admin' ? 'Yönetici' : 'Operatör',
  }
}
