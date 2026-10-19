import { type Camera, type CameraStatus } from '../types'

export type CameraFilterState = {
  search: string
  status: CameraStatus | 'all'
  zoneId: string | 'all'
}

export const DEFAULT_CAMERA_FILTERS: CameraFilterState = {
  search: '',
  status: 'all',
  zoneId: 'all',
}

export function filterCameras(cameras: Camera[], filters: CameraFilterState) {
  const q = filters.search.trim().toLocaleLowerCase('tr-TR')
  return cameras.filter((camera) => {
    if (filters.status !== 'all' && camera.status !== filters.status)
      return false
    if (filters.zoneId !== 'all' && camera.zone.id !== filters.zoneId)
      return false
    if (!q) return true
    return [camera.code, camera.name, camera.location, camera.zone.name]
      .join(' ')
      .toLocaleLowerCase('tr-TR')
      .includes(q)
  })
}
