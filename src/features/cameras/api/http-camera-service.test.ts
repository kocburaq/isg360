import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createHttpCameraService } from './http-camera-service'

const http = vi.hoisted(() => ({ get: vi.fn(), patch: vi.fn() }))

vi.mock('@/services/http-client', () => ({ httpClient: http }))

function page<T>(items: T[], total: number, pageNo = 1) {
  return { data: { items, total, page: pageNo, pageSize: 500 } }
}

describe('createHttpCameraService', () => {
  const service = createHttpCameraService()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('unwraps paginated camera lists', async () => {
    http.get.mockResolvedValueOnce(page([{ id: 'cam-01' }], 1))

    const cameras = await service.listCameras()

    expect(cameras).toEqual([{ id: 'cam-01' }])
    expect(http.get).toHaveBeenCalledWith('/cameras', {
      params: { page: 1, page_size: 500 },
    })
  })

  it('follows pages until all items are loaded', async () => {
    http.get
      .mockResolvedValueOnce(page([{ id: 'a' }, { id: 'b' }], 3, 1))
      .mockResolvedValueOnce(page([{ id: 'c' }], 3, 2))

    const result = await service.listViolations()

    expect(result.map((v) => v.id)).toEqual(['a', 'b', 'c'])
    expect(http.get).toHaveBeenCalledTimes(2)
    expect(http.get.mock.calls[1][1].params.page).toBe(2)
  })

  it('sends violation filters as API query params', async () => {
    http.get.mockResolvedValueOnce(page([], 0))

    await service.listViolations({
      cameraId: 'cam-02',
      status: ['open', 'acknowledged'],
    })

    expect(http.get).toHaveBeenCalledWith('/violations', {
      params: {
        camera_id: 'cam-02',
        status: ['open', 'acknowledged'],
        page: 1,
        page_size: 500,
      },
    })
  })

  it('persists a status change with PATCH /violations/{id}', async () => {
    http.patch.mockResolvedValueOnce({
      data: { id: 'vio-0022', status: 'acknowledged' },
    })

    const updated = await service.updateViolationStatus(
      'vio-0022',
      'acknowledged'
    )

    expect(http.patch).toHaveBeenCalledWith('/violations/vio-0022', {
      status: 'acknowledged',
    })
    expect(updated.status).toBe('acknowledged')
  })

  it('loads camera detail, summary and health from their endpoints', async () => {
    http.get
      .mockResolvedValueOnce({ data: { id: 'cam 1' } })
      .mockResolvedValueOnce({ data: { cameras: { total: 6 } } })
      .mockResolvedValueOnce({
        data: {
          status: 'ok',
          state: 'simulated',
          checkedAt: 'x',
          services: [],
        },
      })

    await service.getCamera('cam 1')
    const summary = await service.getSummary()
    const system = await service.getSystemStatus()

    expect(http.get.mock.calls.map((c) => c[0])).toEqual([
      '/cameras/cam%201',
      '/dashboard/summary',
      '/health',
    ])
    expect(summary.cameras.total).toBe(6)
    expect(system).toEqual({ state: 'simulated', checkedAt: 'x', services: [] })
  })

  it('does not call the API for detections (no inference service yet)', async () => {
    await expect(service.getLatestDetections('cam-01')).resolves.toBeNull()
    expect(http.get).not.toHaveBeenCalled()
  })
})
