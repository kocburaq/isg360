import { AxiosError } from 'axios'
import { env } from '@/config/env'

/**
 * Backend hata sözleşmesi:
 *   { "error": { "code": "not_found", "message": "...", "details": [...] } }
 */
type ApiErrorBody = {
  error?: { code?: string; message?: string; details?: unknown }
  title?: string
}

/** Hatadan kullanıcıya gösterilebilir Türkçe mesaj üretir; yoksa `undefined`. */
export function getApiErrorMessage(error: unknown): string | undefined {
  if (!(error instanceof AxiosError)) return undefined

  if (!error.response) {
    // Ağ hatası, CORS reddi veya backend kapalı
    return `Sunucuya ulaşılamadı (${env.apiBaseUrl}). Backend'in çalıştığından emin olun.`
  }

  const data = error.response.data as ApiErrorBody | undefined
  const message = data?.error?.message ?? data?.title
  return typeof message === 'string' && message.length > 0 ? message : undefined
}
