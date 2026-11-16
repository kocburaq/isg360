import { httpClient } from '@/services/http-client'
import { type Paginated } from '@/types/common'
import { type Factory } from '@/types/factory'
import {
  type Camera,
  type CameraSummary,
  type PpeViolation,
  type SystemStatus,
} from '../types'
import { type CameraService } from './camera-service'

/**
 * FastAPI backend uygulaması (backend/ klasörü). Uç noktalar (/api/v1 altında):
 *
 *   GET   /factories               fabrikalar
 *   GET   /cameras                 sayfalı liste (?factory_id=)
 *   GET   /cameras/{id}            kamera ayrıntısı
 *   GET   /violations              ?camera_id=&factory_id=&status=open&status=...  (sayfalı)
 *   PATCH /violations/{id}         { status }
 *   GET   /dashboard/summary       özet sayılar (?factory_id=)
 *   GET   /health                  servis durumları
 *
 * Swagger: http://localhost:8000/docs
 */

/** Backend'in izin verdiği en büyük sayfa boyutu. */
const PAGE_SIZE = 500
/** Güvenlik sınırı: en fazla bu kadar sayfa çekilir. */
const MAX_PAGES = 20

/** Sayfalı bir listenin tüm sayfalarını sırayla çeker. */
async function fetchAll<T>(
  path: string,
  params: Record<string, unknown> = {}
): Promise<T[]> {
  const items: T[] = []
  for (let page = 1; page <= MAX_PAGES; page++) {
    const { data } = await httpClient.get<Paginated<T>>(path, {
      params: { ...params, page, page_size: PAGE_SIZE },
    })
    items.push(...data.items)
    if (items.length >= data.total || data.items.length === 0) break
  }
  return items
}

type HealthResponse = SystemStatus & { status: 'ok' | 'error' }

export function createHttpCameraService(): CameraService {
  return {
    async listFactories() {
      const { data } = await httpClient.get<Factory[]>('/factories')
      return data
    },

    listCameras(query) {
      return fetchAll<Camera>('/cameras', { factory_id: query?.factoryId })
    },

    async getCamera(cameraId) {
      const { data } = await httpClient.get<Camera>(
        `/cameras/${encodeURIComponent(cameraId)}`
      )
      return data
    },

    async getLatestDetections() {
      // Görüntü işleme (YOLO) servisi bu aşamada yok; backend tespit kaydı tutmaz.
      // Arayüz "Tespit kaydı yok" durumunu gösterir.
      return null
    },

    listViolations(query) {
      return fetchAll<PpeViolation>('/violations', {
        camera_id: query?.cameraId,
        factory_id: query?.factoryId,
        // Tekrarlanan parametre olarak gönderilir: status=open&status=acknowledged
        status: query?.status,
      })
    },

    async updateViolationStatus(id, status) {
      const { data } = await httpClient.patch<PpeViolation>(
        `/violations/${encodeURIComponent(id)}`,
        { status }
      )
      return data
    },

    async getSystemStatus() {
      const { data } = await httpClient.get<HealthResponse>('/health')
      return {
        state: data.state,
        checkedAt: data.checkedAt,
        services: data.services,
      }
    },

    async getSummary(factoryId) {
      const { data } = await httpClient.get<CameraSummary>(
        '/dashboard/summary',
        { params: { factory_id: factoryId } }
      )
      return data
    },
  }
}
