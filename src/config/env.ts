/**
 * Ortam değişkenlerinin tek okuma noktası.
 * Bileşenler `import.meta.env`'e doğrudan erişmez; buradaki tipli değerleri kullanır.
 */
export type DataSource = 'mock' | 'api'

const dataSource: DataSource =
  import.meta.env.VITE_DATA_SOURCE === 'api' ? 'api' : 'mock'

export const env = {
  /** Veri katmanı kaynağı. Backend hazır olana kadar varsayılan "mock". */
  dataSource,
  /** Gelecekteki FastAPI backend adresi. */
  apiBaseUrl:
    import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1',
} as const
