/**
 * Ortam değişkenlerinin tek okuma noktası.
 * Bileşenler `import.meta.env`'e doğrudan erişmez; buradaki tipli değerleri kullanır.
 */
export type DataSource = 'mock' | 'api'

// "api" ve "http" aynı anlama gelir: FastAPI backend kullanılır.
const rawSource = import.meta.env.VITE_DATA_SOURCE
const dataSource: DataSource =
  rawSource === 'api' || rawSource === 'http' ? 'api' : 'mock'

export const env = {
  /** Veri katmanı kaynağı: "mock" (örnek veri, varsayılan) veya "api" (FastAPI). */
  dataSource,
  /** FastAPI backend adresi (backend/ klasörü). */
  apiBaseUrl:
    import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1',
} as const
