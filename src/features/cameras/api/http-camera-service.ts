import { httpClient } from '@/services/http-client'
import { type CameraService } from './camera-service'

/**
 * FastAPI backend uygulaması (henüz backend yok).
 * Uç noktalar taslaktır; backend geliştirilirken bu sözleşme birlikte netleştirilmelidir.
 *
 *   GET   /cameras
 *   GET   /cameras/{id}/detections/latest   → 404 ise tespit yok
 *   GET   /ppe/violations?camera_id=&status=
 *   PATCH /ppe/violations/{id}               { status }
 *   GET   /system/status
 */
export function createHttpCameraService(): CameraService {
  return {
    async listCameras() {
      const { data } = await httpClient.get('/cameras')
      return data
    },

    async getLatestDetections(cameraId) {
      const response = await httpClient.get(
        `/cameras/${encodeURIComponent(cameraId)}/detections/latest`,
        { validateStatus: (s) => s === 200 || s === 404 }
      )
      return response.status === 404 ? null : response.data
    },

    async listViolations(query) {
      const { data } = await httpClient.get('/ppe/violations', {
        params: {
          camera_id: query?.cameraId,
          status: query?.status?.join(','),
        },
      })
      return data
    },

    async updateViolationStatus(id, status) {
      const { data } = await httpClient.patch(
        `/ppe/violations/${encodeURIComponent(id)}`,
        { status }
      )
      return data
    },

    async getSystemStatus() {
      const { data } = await httpClient.get('/system/status')
      return data
    },
  }
}
