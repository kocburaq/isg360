import axios from 'axios'
import { env } from '@/config/env'

/**
 * FastAPI backend için ortak HTTP istemcisi.
 * Tüm "api" servis uygulamaları bu örneği kullanır; böylece kimlik doğrulama
 * başlıkları, zaman aşımı ve hata yönetimi tek noktadan yapılandırılır.
 */
export const httpClient = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: 15_000,
  // Oturumun sunucu tarafında httpOnly çerez ile taşınması öngörülüyor.
  withCredentials: true,
  // Dizi parametreleri tekrarlanan anahtar olarak gönderilir: status=open&status=acknowledged
  // (FastAPI'nin beklediği biçim; varsayılan "status[]=" biçimi değil)
  paramsSerializer: { indexes: null },
})
