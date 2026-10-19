import { type EntityId } from '@/types/common'
import {
  type Camera,
  type DetectionSnapshot,
  type PpeViolation,
  type SystemStatus,
  type ViolationQuery,
  type ViolationStatus,
} from '../types'

/**
 * Kamera modülünün veri sözleşmesi.
 * Bileşenler yalnızca bu arayüzü (hook'lar üzerinden) kullanır; veri kaynağı
 * mock veya FastAPI olabilir. Yeni kaynak eklemek için bu arayüzü uygulayın.
 */
export interface CameraService {
  listCameras(): Promise<Camera[]>
  /** Kameradan alınan son tespit sonucu; kayıt yoksa null. */
  getLatestDetections(cameraId: EntityId): Promise<DetectionSnapshot | null>
  listViolations(query?: ViolationQuery): Promise<PpeViolation[]>
  updateViolationStatus(
    id: EntityId,
    status: ViolationStatus
  ): Promise<PpeViolation>
  getSystemStatus(): Promise<SystemStatus>
}
