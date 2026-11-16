import {
  type PpeClassId,
  type PpeViolation,
  type ViolationSeverity,
  type ViolationStatus,
} from '@/features/cameras/types'
import { factoryIdOfZone } from './factory-zones'
import { minutesAgo } from './utils'

/** [kamera, bölge, eksik KKD, kaç dakika önce, durum, güven] */
type ViolationSpec = [
  string,
  string,
  PpeClassId[],
  number,
  ViolationStatus,
  number,
]

const SPECS: ViolationSpec[] = [
  ['cam-01', 'zone-entrance', ['vest'], 3, 'open', 0.91],
  ['cam-02', 'zone-assembly', ['helmet'], 6, 'open', 0.88],
  ['cam-04', 'zone-logistics', ['helmet', 'vest'], 11, 'open', 0.93],
  ['cam-02', 'zone-assembly', ['vest'], 27, 'acknowledged', 0.84],
  ['cam-01', 'zone-entrance', ['helmet'], 48, 'acknowledged', 0.79],
  ['cam-03', 'zone-production', ['vest'], 75, 'resolved', 0.86],
  ['cam-04', 'zone-logistics', ['vest'], 96, 'resolved', 0.9],
  ['cam-05', 'zone-logistics', ['helmet'], 150, 'resolved', 0.81],
  ['cam-02', 'zone-assembly', ['helmet', 'vest'], 190, 'resolved', 0.95],
  ['cam-06', 'zone-hazmat', ['helmet'], 260, 'resolved', 0.87],
  ['cam-01', 'zone-entrance', ['vest'], 340, 'resolved', 0.83],
  ['cam-04', 'zone-logistics', ['helmet'], 420, 'resolved', 0.89],
  ['cam-03', 'zone-production', ['helmet'], 610, 'resolved', 0.92],
  ['cam-02', 'zone-assembly', ['vest'], 980, 'resolved', 0.8],
  ['cam-05', 'zone-logistics', ['helmet', 'vest'], 1260, 'resolved', 0.94],
  ['cam-01', 'zone-entrance', ['helmet'], 1500, 'resolved', 0.85],
  ['cam-06', 'zone-hazmat', ['vest'], 1720, 'resolved', 0.82],
  ['cam-04', 'zone-logistics', ['vest'], 2100, 'resolved', 0.88],
  ['cam-02', 'zone-assembly', ['helmet'], 2490, 'resolved', 0.9],
  ['cam-03', 'zone-production', ['helmet', 'vest'], 2880, 'resolved', 0.96],
  ['cam-01', 'zone-entrance', ['vest'], 3300, 'resolved', 0.78],
  ['cam-04', 'zone-logistics', ['helmet'], 3720, 'resolved', 0.87],
]

/** Kimliği sabit ek kayıtlar (backend seed EXTRA_VIOLATIONS ile aynı). */
const EXTRA_SPECS: [string, ...ViolationSpec][] = [
  ['vio-0023', 'cam-07', 'zone-press', ['helmet'], 400, 'resolved', 0.86],
  ['vio-0024', 'cam-08', 'zone-press', ['vest'], 2600, 'resolved', 0.84],
]

const PPE_LABELS: Partial<Record<PpeClassId, string>> = {
  helmet: 'baret',
  vest: 'reflektörlü yelek',
}

function ppeLabel(id: PpeClassId): string {
  return PPE_LABELS[id] ?? id
}

function severityFor(missing: PpeClassId[]): ViolationSeverity {
  if (missing.length > 1) return 'high'
  return missing[0] === 'helmet' ? 'high' : 'medium'
}

/** SİMÜLE EDİLMİŞ İHLAL KAYITLARI — gerçek olay değildir. */
export function createMockViolations(): PpeViolation[] {
  const specs: [string, ...ViolationSpec][] = [
    ...SPECS.map(
      (spec, i) =>
        [`vio-${String(SPECS.length - i).padStart(4, '0')}`, ...spec] as [
          string,
          ...ViolationSpec,
        ]
    ),
    ...EXTRA_SPECS,
  ]
  return specs.map(
    ([id, cameraId, zoneId, missing, ago, status, confidence]) => ({
      id,
      cameraId,
      zoneId,
      factoryId: factoryIdOfZone(zoneId),
      violationType: 'missing_ppe',
      missing,
      detectedAt: minutesAgo(ago),
      confidence,
      severity: severityFor(missing),
      status,
      source: 'simulation',
      description: `Simüle edilmiş tespit: ${missing.map(ppeLabel).join(', ')} eksik.`,
      reviewedAt: status === 'open' ? null : minutesAgo(ago - 2),
      endedAt: null,
      edgeNodeId: null,
    })
  )
}
