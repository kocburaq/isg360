import { useMemo } from 'react'
import { isToday } from 'date-fns'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { env } from '@/config/env'
import { toast } from 'sonner'
import { cameraKeys, cameraService } from '../api'
import { type ViolationQuery, type ViolationStatus } from '../types'

/** Gerçek backend'de veriler periyodik yenilenir; mock modda gereksiz. */
const LIVE_REFETCH_MS = env.dataSource === 'api' ? 5_000 : false

export function useCameras() {
  return useQuery({
    queryKey: cameraKeys.list(),
    queryFn: () => cameraService.listCameras(),
    refetchInterval: LIVE_REFETCH_MS,
  })
}

export function useCameraDetections(cameraId: string | undefined) {
  return useQuery({
    queryKey: cameraKeys.detections(cameraId ?? ''),
    queryFn: () => cameraService.getLatestDetections(cameraId!),
    enabled: !!cameraId,
    refetchInterval: LIVE_REFETCH_MS,
  })
}

export function useViolations(query?: ViolationQuery) {
  return useQuery({
    queryKey: cameraKeys.violations(query),
    queryFn: () => cameraService.listViolations(query),
    refetchInterval: LIVE_REFETCH_MS,
  })
}

export function useSystemStatus() {
  return useQuery({
    queryKey: cameraKeys.systemStatus(),
    queryFn: () => cameraService.getSystemStatus(),
    refetchInterval: env.dataSource === 'api' ? 30_000 : false,
  })
}

export function useUpdateViolationStatus() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: ViolationStatus }) =>
      cameraService.updateViolationStatus(id, status),
    onSuccess: () => {
      toast.success('İhlal kaydı güncellendi.')
      // Tüm filtre kombinasyonlarındaki ihlal listelerini yenile
      queryClient.invalidateQueries({ queryKey: cameraKeys.allViolations() })
    },
  })
}

/** Üst özet kartları için türetilmiş değerler. */
export function useCameraSummary() {
  const cameras = useCameras()
  const violations = useViolations()
  const system = useSystemStatus()

  const summary = useMemo(() => {
    const list = cameras.data ?? []
    const vios = violations.data ?? []
    return {
      total: list.length,
      online: list.filter((c) => c.status === 'online').length,
      offline: list.filter((c) => c.status === 'offline').length,
      violationsToday: vios.filter((v) => isToday(new Date(v.detectedAt)))
        .length,
      openViolations: vios.filter((v) => v.status === 'open').length,
    }
  }, [cameras.data, violations.data])

  return {
    summary,
    system: system.data,
    isLoading: cameras.isLoading || violations.isLoading || system.isLoading,
  }
}
