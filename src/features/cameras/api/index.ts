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
  factories: () => [...cameraKeys.all, 'factories'] as const,
  allLists: () => [...cameraKeys.all, 'list'] as const,
  list: (filters?: object) =>
    [...cameraKeys.allLists(), filters ?? {}] as const,
  detail: (cameraId: string) =>
    [...cameraKeys.all, 'detail', cameraId] as const,
  detections: (cameraId: string) =>
    [...cameraKeys.all, 'detections', cameraId] as const,
  allViolations: () => [...cameraKeys.all, 'violations'] as const,
  violations: (filters?: object) =>
    [...cameraKeys.allViolations(), filters ?? {}] as const,
  systemStatus: () => [...cameraKeys.all, 'system-status'] as const,
  allSummaries: () => [...cameraKeys.all, 'summary'] as const,
  summary: (factoryId?: string) =>
    [...cameraKeys.allSummaries(), factoryId ?? 'all'] as const,
}
