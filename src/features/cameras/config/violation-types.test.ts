import { describe, expect, it } from 'vitest'
import { createMockCameraService } from '../api/mock-camera-service'
import { violationLabelParts } from './violation-types'

describe('violationLabelParts', () => {
  it('lists each missing PPE class for missing_ppe violations', () => {
    const parts = violationLabelParts({
      violationType: 'missing_ppe',
      missing: ['helmet', 'vest'],
    })
    expect(parts.map((p) => p.label)).toEqual([
      'Baret yok',
      'Reflektörlü Yelek yok',
    ])
  })

  it('uses the type label for restricted area and harness violations', () => {
    expect(
      violationLabelParts({ violationType: 'restricted_area', missing: [] })[0]
        .label
    ).toBe('Yasaklı bölgeye giriş')
    expect(
      violationLabelParts({ violationType: 'missing_harness', missing: [] })[0]
        .label
    ).toBe('Yüksekte emniyet kemeri yok')
  })
})

describe('mock service factory filter', () => {
  const service = createMockCameraService()

  it('lists factories and filters cameras, violations and summary', async () => {
    const factories = await service.listFactories()
    expect(factories.map((f) => f.id)).toEqual(['fac-default', 'fac-gebze'])

    const gebze = await service.listCameras({ factoryId: 'fac-gebze' })
    expect(gebze.map((c) => c.id)).toEqual(['cam-07', 'cam-08'])
    expect(await service.listCameras()).toHaveLength(8)

    const vios = await service.listViolations({ factoryId: 'fac-gebze' })
    expect(vios.map((v) => v.id).sort()).toEqual(['vio-0023', 'vio-0024'])

    const summary = await service.getSummary('fac-gebze')
    expect(summary.cameras.total).toBe(2)
    expect(summary.violations.total).toBe(2)
    expect((await service.getSummary()).cameras.total).toBe(8)
  })
})
