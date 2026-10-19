import { env } from '@/config/env'
import { httpClient } from '@/services/http-client'
import {
  AuthUnavailableError,
  type AuthService,
  type AuthSession,
} from './types'

const DEMO_SESSION_HOURS = 8

function createDemoSession(): AuthSession {
  const now = new Date()
  const expires = new Date(now.getTime() + DEMO_SESSION_HOURS * 60 * 60 * 1000)
  return {
    user: {
      id: 'demo-admin',
      username: 'demo.admin',
      displayName: 'Demo Yönetici',
      role: 'admin',
    },
    mode: 'demo',
    issuedAt: now.toISOString(),
    expiresAt: expires.toISOString(),
  }
}

/**
 * Backend'e bağlı kimlik doğrulama. Sözleşme FastAPI tarafında
 * `POST /auth/login` ve `POST /auth/logout` olarak öngörülmüştür.
 * Oturum anahtarı httpOnly çerezde tutulmalı; tarayıcı tarafı yalnızca
 * dönen oturum özetini saklar.
 */
const serverAuth: Pick<AuthService, 'login' | 'logout'> = {
  async login(credentials) {
    const { data } = await httpClient.post<AuthSession>(
      '/auth/login',
      credentials
    )
    return data
  },
  async logout() {
    await httpClient.post('/auth/logout')
  },
}

export const authService: AuthService = {
  async login(credentials) {
    if (env.dataSource !== 'api') {
      throw new AuthUnavailableError(
        'Kimlik doğrulama sunucusu henüz bağlı değil. Prototipi incelemek için "Demo Modu ile Giriş" seçeneğini kullanın.'
      )
    }
    return serverAuth.login(credentials)
  },

  async loginDemo() {
    return createDemoSession()
  },

  async logout(session) {
    if (session?.mode === 'server') await serverAuth.logout(session)
  },
}
