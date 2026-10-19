import { isToday } from 'date-fns'
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

    async getCamera(cameraId) {
      await simulateLatency(150)
      const camera = cameras.find((c) => c.id === cameraId)
      if (!camera) throw new Error(`Kamera bulunamadı: ${cameraId}`)
      return clone(camera)
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
      if (violation.status !== status) {
        violation.reviewedAt =
          status === 'open'
            ? null
            : (violation.reviewedAt ?? new Date().toISOString())
      }
      violation.status = status
      return clone(violation)
    },

    async getSystemStatus() {
      await simulateLatency(150)
      return createMockSystemStatus()
    },

    async getSummary() {
      await simulateLatency(150)
      const count = <T>(items: T[], predicate: (item: T) => boolean) =>
        items.filter(predicate).length
      return {
        cameras: {
          total: cameras.length,
          online: count(cameras, (c) => c.status === 'online'),
          offline: count(cameras, (c) => c.status === 'offline'),
          unknown: count(cameras, (c) => c.status === 'unknown'),
        },
        violations: {
          total: violations.length,
          today: count(violations, (v) => isToday(new Date(v.detectedAt))),
          open: count(violations, (v) => v.status === 'open'),
          acknowledged: count(violations, (v) => v.status === 'acknowledged'),
          resolved: count(violations, (v) => v.status === 'resolved'),
        },
        containsSimulatedData: true,
        generatedAt: new Date().toISOString(),
      }
    },
  }
}
