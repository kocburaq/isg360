import {
  type DetectionSnapshot,
  type PersonDetection,
  type PpeCheckState,
} from '@/features/cameras/types'
import { minutesAgo } from './utils'

/** Kısa kişi tanımı: [x, y, genişlik, yükseklik, baret, yelek] */
type PersonSpec = [number, number, number, number, PpeCheckState, PpeCheckState]

function persons(cameraId: string, specs: PersonSpec[]): PersonDetection[] {
  return specs.map(([x, y, width, height, helmet, vest], i) => ({
    id: `${cameraId}-p${i + 1}`,
    box: { x, y, width, height },
    checks: [
      {
        classId: 'helmet',
        state: helmet,
        confidence: helmet === 'unknown' ? 0.41 : 0.86 + (i % 3) * 0.04,
      },
      {
        classId: 'vest',
        state: vest,
        confidence: vest === 'unknown' ? 0.38 : 0.82 + (i % 4) * 0.03,
      },
    ],
  }))
}

/**
 * SİMÜLE EDİLMİŞ TESPİTLER — YOLO modeli çıktısı değildir.
 * Çevrimdışı kameralar için kayıt yoktur.
 */
export function createMockDetections(): Record<string, DetectionSnapshot> {
  const snapshot = (
    cameraId: string,
    specs: PersonSpec[],
    ageMinutes = 0
  ): DetectionSnapshot => ({
    cameraId,
    capturedAt: minutesAgo(ageMinutes),
    source: 'simulation',
    model: null,
    persons: persons(cameraId, specs),
  })

  return {
    'cam-01': snapshot('cam-01', [
      [0.12, 0.3, 0.13, 0.58, 'compliant', 'compliant'],
      [0.42, 0.26, 0.14, 0.62, 'compliant', 'violation'],
      [0.7, 0.34, 0.12, 0.54, 'compliant', 'compliant'],
    ]),
    'cam-02': snapshot('cam-02', [
      [0.08, 0.28, 0.12, 0.6, 'compliant', 'compliant'],
      [0.3, 0.3, 0.12, 0.58, 'violation', 'compliant'],
      [0.55, 0.27, 0.12, 0.6, 'compliant', 'compliant'],
      [0.78, 0.32, 0.11, 0.55, 'compliant', 'unknown'],
    ]),
    'cam-03': snapshot(
      'cam-03',
      [
        [0.2, 0.25, 0.15, 0.64, 'compliant', 'compliant'],
        [0.6, 0.3, 0.14, 0.6, 'compliant', 'compliant'],
      ],
      1
    ),
    'cam-04': snapshot('cam-04', [
      [0.25, 0.32, 0.13, 0.56, 'violation', 'violation'],
      [0.62, 0.28, 0.13, 0.6, 'compliant', 'compliant'],
    ]),
    'cam-06': snapshot(
      'cam-06',
      [[0.45, 0.3, 0.14, 0.6, 'compliant', 'compliant']],
      2
    ),
  }
}
