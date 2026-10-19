import { createMockCameras } from '@/mocks/cameras'
import { createMockDetections } from '@/mocks/ppe-detections'
import { createMockViolations } from '@/mocks/ppe-violations'
import { createMockSystemStatus } from '@/mocks/system-status'
import { clone, simulateLatency } from '@/mocks/utils'
import { type CameraService } from './camera-service'

/**
 * Bellek içi örnek veri ile çalışan servis.
 * Yapılan değişiklikler (ör. ihlal durumu) sayfa yenilenene kadar korunur.
 */
export function createMockCameraService(): CameraService {
  const cameras = createMockCameras()
  const detections = createMockDetections()
  const violations = createMockViolations()

  return {
    async listCameras() {
      await simulateLatency()
      return clone(cameras)
    },

    async getLatestDetections(cameraId) {
      await simulateLatency(200)
      return detections[cameraId] ? clone(detections[cameraId]) : null
    },

    async listViolations(query) {
      await simulateLatency()
      const result = violations
        .filter((v) => !query?.cameraId || v.cameraId === query.cameraId)
        .filter((v) => !query?.status || query.status.includes(v.status))
        .sort((a, b) => b.detectedAt.localeCompare(a.detectedAt))
      return clone(result)
    },

    async updateViolationStatus(id, status) {
      await simulateLatency(200)
      const violation = violations.find((v) => v.id === id)
      if (!violation) throw new Error(`İhlal kaydı bulunamadı: ${id}`)
      violation.status = status
      return clone(violation)
    },

    async getSystemStatus() {
      await simulateLatency(150)
      return createMockSystemStatus()
    },
  }
}
