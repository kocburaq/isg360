import { createMockCameras } from '@/mocks/cameras'
import { createMockDetections } from '@/mocks/ppe-detections'
import { describe, expect, it } from 'vitest'
import { DEFAULT_CAMERA_FILTERS, filterCameras } from './filters'
import { personState, summarizeDetections } from './ppe'

describe('filterCameras', () => {
  const cameras = createMockCameras()

  it('returns all cameras with default filters', () => {
    expect(filterCameras(cameras, DEFAULT_CAMERA_FILTERS)).toHaveLength(6)
  })

  it('filters by status', () => {
    const result = filterCameras(cameras, {
      ...DEFAULT_CAMERA_FILTERS,
      status: 'offline',
    })
    expect(result.map((c) => c.code)).toEqual(['CAM-05'])
  })

  it('searches name, code and zone case-insensitively (Turkish locale)', () => {
    const byZone = filterCameras(cameras, {
      ...DEFAULT_CAMERA_FILTERS,
      search: 'LOJİSTİK',
    })
    expect(byZone.map((c) => c.code)).toEqual(['CAM-04', 'CAM-05'])

    const byCode = filterCameras(cameras, {
      ...DEFAULT_CAMERA_FILTERS,
      search: 'cam-03',
    })
    expect(byCode).toHaveLength(1)
  })
})

describe('PPE helpers', () => {
  const detections = createMockDetections()

  it('marks a person with any missing PPE as violation', () => {
    const [, second] = detections['cam-01'].persons
    expect(personState(second)).toBe('violation')
  })

  it('summarizes counts per enabled PPE class', () => {
    const summary = summarizeDetections(detections['cam-02'], [
      'helmet',
      'vest',
    ])
    const helmet = summary.find((s) => s.classId === 'helmet')!
    const vest = summary.find((s) => s.classId === 'vest')!
    expect(helmet.counts).toEqual({ compliant: 3, violation: 1, unknown: 0 })
    expect(vest.counts).toEqual({ compliant: 3, violation: 0, unknown: 1 })
  })

  it('returns zero counts when there is no snapshot', () => {
    const [helmet] = summarizeDetections(null, ['helmet'])
    expect(helmet.counts).toEqual({ compliant: 0, violation: 0, unknown: 0 })
  })
})
