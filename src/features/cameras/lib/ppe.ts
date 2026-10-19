import { ENABLED_PPE_CLASSES } from '../config/ppe-classes'
import {
  type DetectionSnapshot,
  type PersonDetection,
  type PpeCheckState,
  type PpeClassId,
} from '../types'

/** Kişide en az bir KKD ihlali varsa "violation", belirsiz varsa "unknown". */
export function personState(person: PersonDetection): PpeCheckState {
  const states = person.checks.map((c) => c.state)
  if (states.includes('violation')) return 'violation'
  if (states.includes('unknown')) return 'unknown'
  return 'compliant'
}

export type PpeClassSummary = {
  classId: PpeClassId
  counts: Record<PpeCheckState, number>
}

/** Etkin KKD sınıfları için bir tespit sonucundaki durum dağılımı. */
export function summarizeDetections(
  snapshot: DetectionSnapshot | null | undefined,
  classIds: PpeClassId[]
): PpeClassSummary[] {
  return ENABLED_PPE_CLASSES.filter((c) => classIds.includes(c.id)).map(
    (ppeClass) => {
      const counts: Record<PpeCheckState, number> = {
        compliant: 0,
        violation: 0,
        unknown: 0,
      }
      for (const person of snapshot?.persons ?? []) {
        const check = person.checks.find((c) => c.classId === ppeClass.id)
        counts[check?.state ?? 'unknown'] += 1
      }
      return { classId: ppeClass.id, counts }
    }
  )
}
