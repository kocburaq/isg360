import { env } from '@/config/env'
import { type CameraService } from './camera-service'
import { createHttpCameraService } from './http-camera-service'
import { createMockCameraService } from './mock-camera-service'

/** Ortama göre seçilen kamera servisi (VITE_DATA_SOURCE). */
export const cameraService: CameraService =
  env.dataSource === 'api'
    ? createHttpCameraService()
    : createMockCameraService()

export const cameraKeys = {
  all: ['cameras'] as const,
  list: () => [...cameraKeys.all, 'list'] as const,
  detections: (cameraId: string) =>
    [...cameraKeys.all, 'detections', cameraId] as const,
  allViolations: () => [...cameraKeys.all, 'violations'] as const,
  violations: (filters?: object) =>
    [...cameraKeys.allViolations(), filters ?? {}] as const,
  systemStatus: () => [...cameraKeys.all, 'system-status'] as const,
}
