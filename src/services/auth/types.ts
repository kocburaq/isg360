import { type EntityId, type ISODateString } from '@/types/common'

export type UserRole = 'admin' | 'operator'

export type AuthUser = {
  id: EntityId
  username: string
  displayName: string
  role: UserRole
}

/**
 * Tarayıcıda tutulan oturum özeti.
 * Parola, erişim anahtarı veya başka bir gizli bilgi İÇERMEZ.
 */
export type AuthSession = {
  user: AuthUser
  /** "demo": prototip oturumu, hiçbir güvenlik sağlamaz. */
  mode: 'demo' | 'server'
  issuedAt: ISODateString
  expiresAt: ISODateString
}

export type LoginCredentials = {
  username: string
  password: string
}

export interface AuthService {
  /** Gerçek kimlik doğrulama (backend gerektirir). */
  login(credentials: LoginCredentials): Promise<AuthSession>
  /** Yalnızca prototip amaçlı demo oturumu açar. */
  loginDemo(): Promise<AuthSession>
  logout(session: AuthSession | null): Promise<void>
}

export class AuthUnavailableError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'AuthUnavailableError'
  }
}
