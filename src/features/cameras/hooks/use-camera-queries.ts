import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { env } from '@/config/env'
import { toast } from 'sonner'
import { cameraKeys, cameraService } from '../api'
import {
  type Camera,
  type ViolationQuery,
  type ViolationStatus,
} from '../types'

/** Gerçek backend'de veriler periyodik yenilenir; mock modda gereksiz. */
const LIVE_REFETCH_MS = env.dataSource === 'api' ? 5_000 : false

export function useCameras() {
  return useQuery({
    queryKey: cameraKeys.list(),
    queryFn: () => cameraService.listCameras(),
    refetchInterval: LIVE_REFETCH_MS,
  })
}

/**
 * Tek kamera ayrıntısı. Listeden gelen kayıt varsa anında gösterilir,
 * ardından ayrıntı uç noktasından güncellenir.
 */
export function useCamera(cameraId: string | undefined, placeholder?: Camera) {
  return useQuery({
    queryKey: cameraKeys.detail(cameraId ?? ''),
    queryFn: () => cameraService.getCamera(cameraId!),
    enabled: !!cameraId,
    placeholderData: placeholder,
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
      // Tüm filtre kombinasyonlarındaki ihlal listelerini ve özet sayıları yenile
      queryClient.invalidateQueries({ queryKey: cameraKeys.allViolations() })
      queryClient.invalidateQueries({ queryKey: cameraKeys.summary() })
    },
  })
}

/** Üst özet kartları: sayılar ve servis durumları veri kaynağından gelir. */
export function useCameraSummary() {
  const summary = useQuery({
    queryKey: cameraKeys.summary(),
    queryFn: () => cameraService.getSummary(),
    refetchInterval: LIVE_REFETCH_MS,
  })
  const system = useSystemStatus()

  return {
    summary: summary.data,
    system: system.data,
    isLoading: summary.isLoading || system.isLoading,
    error: summary.error ?? system.error,
    refetch: () => {
      void summary.refetch()
      void system.refetch()
    },
    isRefetching: summary.isFetching || system.isFetching,
  }
}
