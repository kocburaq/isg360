/** Tüm modüllerde kullanılan temel tipler. */

/** Sunucudan gelen tanımlayıcılar (UUID veya benzeri). */
export type EntityId = string

/** ISO 8601 biçiminde tarih-saat (ör. 2026-10-18T09:30:00Z). */
export type ISODateString = string

/** Sayfalı liste yanıtları için ortak sözleşme (FastAPI tarafıyla uyumlu). */
export type Paginated<T> = {
  items: T[]
  total: number
  page: number
  pageSize: number
}
