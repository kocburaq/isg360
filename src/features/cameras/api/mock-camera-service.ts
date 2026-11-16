import { isToday } from 'date-fns'
import { createMockCameras } from '@/mocks/cameras'
import { mockFactories } from '@/mocks/factory-zones'
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
  const factories = Object.values(mockFactories)
  const cameras = createMockCameras()
  const detections = createMockDetections()
  const violations = createMockViolations()

  const inFactory = (factoryId: string | undefined, id: string | undefined) =>
    !factoryId || id === factoryId

  return {
    async listFactories() {
      await simulateLatency(100)
      return clone(factories)
    },

    async listCameras(query) {
      await simulateLatency()
      return clone(
        cameras.filter((c) => inFactory(query?.factoryId, c.factory.id))
      )
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
        .filter((v) => inFactory(query?.factoryId, v.factoryId))
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

    async getSummary(factoryId) {
      await simulateLatency(150)
      const cams = cameras.filter((c) => inFactory(factoryId, c.factory.id))
      const vios = violations.filter((v) => inFactory(factoryId, v.factoryId))
      const count = <T>(items: T[], predicate: (item: T) => boolean) =>
        items.filter(predicate).length
      return {
        cameras: {
          total: cams.length,
          online: count(cams, (c) => c.status === 'online'),
          offline: count(cams, (c) => c.status === 'offline'),
          unknown: count(cams, (c) => c.status === 'unknown'),
        },
        violations: {
          total: vios.length,
          today: count(vios, (v) => isToday(new Date(v.detectedAt))),
          open: count(vios, (v) => v.status === 'open'),
          acknowledged: count(vios, (v) => v.status === 'acknowledged'),
          resolved: count(vios, (v) => v.status === 'resolved'),
        },
        containsSimulatedData: true,
        generatedAt: new Date().toISOString(),
      }
    },
  }
}
