import { type AuthSession } from '@/services/auth/types'
import { create } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'

const STORAGE_KEY = 'fcs-session'

type AuthState = {
  session: AuthSession | null
  setSession: (session: AuthSession) => void
  clearSession: () => void
}

/**
 * Oturum durumu. Yalnızca parolasız oturum özeti (kullanıcı adı, rol, süre)
 * sekme kapanınca silinen sessionStorage'da tutulur.
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      session: null,
      setSession: (session) => set({ session }),
      clearSession: () => set({ session: null }),
    }),
    {
      name: STORAGE_KEY,
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({ session: state.session }),
    }
  )
)

export function isSessionValid(session: AuthSession | null): boolean {
  if (!session) return false
  return new Date(session.expiresAt).getTime() > Date.now()
}

/** Rota koruyucuları gibi React dışı yerlerde kullanılır. */
export function getActiveSession(): AuthSession | null {
  const { session, clearSession } = useAuthStore.getState()
  if (session && !isSessionValid(session)) {
    clearSession()
    return null
  }
  return session
}
