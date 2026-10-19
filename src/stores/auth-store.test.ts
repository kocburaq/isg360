import { type AuthSession } from '@/services/auth/types'
import { beforeEach, describe, expect, it, vi } from 'vitest'

async function importAuthStore() {
  return await import('./auth-store')
}

function session(expiresInMs: number): AuthSession {
  return {
    user: {
      id: 'u1',
      username: 'demo.admin',
      displayName: 'Demo Yönetici',
      role: 'admin',
    },
    mode: 'demo',
    issuedAt: new Date().toISOString(),
    expiresAt: new Date(Date.now() + expiresInMs).toISOString(),
  }
}

describe('auth-store', () => {
  beforeEach(() => {
    sessionStorage.clear()
    localStorage.clear()
    vi.resetModules()
  })

  it('starts without a session', async () => {
    const { useAuthStore } = await importAuthStore()
    expect(useAuthStore.getState().session).toBeNull()
  })

  it('persists the session summary in sessionStorage only', async () => {
    const { useAuthStore } = await importAuthStore()
    useAuthStore.getState().setSession(session(60_000))

    const stored = sessionStorage.getItem('fcs-session') ?? ''
    expect(stored).toContain('demo.admin')
    expect(stored).not.toMatch(/password|token/i)
    expect(localStorage.length).toBe(0)
    expect(document.cookie).not.toContain('fcs-session')
  })

  it('restores a persisted session after reload', async () => {
    const first = await importAuthStore()
    first.useAuthStore.getState().setSession(session(60_000))

    vi.resetModules()
    const { getActiveSession } = await importAuthStore()
    expect(getActiveSession()?.user.username).toBe('demo.admin')
  })

  it('treats an expired session as signed out and clears it', async () => {
    const { useAuthStore, getActiveSession } = await importAuthStore()
    useAuthStore.getState().setSession(session(-1_000))

    expect(getActiveSession()).toBeNull()
    expect(useAuthStore.getState().session).toBeNull()
  })

  it('clearSession removes the session', async () => {
    const { useAuthStore } = await importAuthStore()
    useAuthStore.getState().setSession(session(60_000))
    useAuthStore.getState().clearSession()
    expect(useAuthStore.getState().session).toBeNull()
  })
})
